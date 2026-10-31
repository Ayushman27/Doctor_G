
import re
import joblib
import numpy as np
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

MODEL = joblib.load(
    BASE_DIR / "disease_model.pkl"
)

LABEL_ENCODER = joblib.load(
    BASE_DIR / "label_encoder.pkl"
)

import json

with open(
    BASE_DIR / "symptom_metadata.json",
    "r"
) as f:

    METADATA = json.load(f)

SYMPTOMS = METADATA["symptoms"]


def normalize_symptom(symptom):

    symptom = str(symptom).strip().lower()

    symptom = symptom.replace(" ", "_")
    symptom = symptom.replace("-", "_")
    symptom = symptom.replace("/", "_")

    return symptom


def predict_disease(symptoms):

    input_vector = pd.DataFrame(
        0,
        index=[0],
        columns=SYMPTOMS
    )

    matched = []
    unmatched = []

    for symptom in symptoms:

        normalized = normalize_symptom(
            symptom
        )

        if normalized in input_vector.columns:

            input_vector.loc[
                0,
                normalized
            ] = 1

            matched.append(normalized)

        else:

            unmatched.append(symptom)

    if not matched:

        raise ValueError(
            "No valid symptoms were found."
        )

    probabilities = MODEL.predict_proba(
        input_vector
    )[0]

    top_indices = np.argsort(
        probabilities
    )[::-1][:5]

    predictions = []

    for index in top_indices:

        predictions.append({
            "disease":
                LABEL_ENCODER.inverse_transform(
                    [index]
                )[0],

            "probability":
                float(probabilities[index])
        })

    return {
        "matched_symptoms": matched,
        "unmatched_symptoms": unmatched,
        "predictions": predictions
    }
