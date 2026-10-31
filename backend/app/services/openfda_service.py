"""
OpenFDA Drug Information & Label Service.
Integrates with the official US Food & Drug Administration (FDA) REST API (api.fda.gov)
to retrieve official drug labels, active ingredients, indications, warnings, and usage guidelines.
"""

from __future__ import annotations

import logging
import re
from typing import Dict, Any, List, Optional
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

OPENFDA_BASE_URL = "https://api.fda.gov/drug/label.json"


def clean_fda_indications(text: str) -> str:
    """Clean raw FDA section headers and regulatory codes for patient readability."""
    if not text:
        return "No official indications text provided."
    # Strip section prefixes e.g. "1 INDICATIONS AND USAGE", "INDICATIONS AND USAGE Hypertension"
    t = re.sub(r"^(?:\d+\s+)?INDICATIONS(?:\s+AND\s+USAGE)?(?:\s+[A-Z0-9\-]+)?\s*", "", text, flags=re.IGNORECASE).strip()
    # Strip regulatory section numbers like ( 1.1 ), ( 1.2 )
    t = re.sub(r"\(\s*\d+\.\d+\s*\)", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    if t and t[0].islower():
        t = t[0].upper() + t[1:]
    return t


def fetch_openfda_drug_info(drug_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetch official OpenFDA drug label data by drug name (brand or generic).
    """
    api_key = getattr(settings, "openfda_api_key", "AlqBpoXw03ITN1J2zteR2zg17gCnbQERlGQT3ema")
    clean_name = drug_name.strip().lower()

    search_query = f'openfda.brand_name:"{clean_name}"+OR+openfda.generic_name:"{clean_name}"'

    params = {
        "api_key": api_key,
        "search": search_query,
        "limit": 1
    }

    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(OPENFDA_BASE_URL, params=params)
            if resp.status_code != 200:
                params["search"] = clean_name
                resp = client.get(OPENFDA_BASE_URL, params=params)
                if resp.status_code != 200:
                    logger.info("OpenFDA drug info not found for query '%s' (status %d).", drug_name, resp.status_code)
                    return None

            data = resp.json()
            results = data.get("results", [])
            if not results:
                return None

            res = results[0]
            openfda_meta = res.get("openfda", {})

            b_name = openfda_meta.get("brand_name", [None])[0]
            g_name = openfda_meta.get("generic_name", [None])[0]
            active_ingredients = res.get("active_ingredient", openfda_meta.get("substance_name", []))
            indications = res.get("indications_and_usage", ["No official indications text provided."])
            warnings = res.get("warnings", res.get("warnings_and_cautions", ["Consult physician for safety warnings."]))
            dosage = res.get("dosage_and_administration", ["Follow physician or product package instructions."])

            indications_clean = clean_fda_indications(indications[0])
            if len(indications_clean) > 300:
                indications_clean = indications_clean[:300] + "..."

            warnings_clean = warnings[0][:250] + "..." if len(warnings[0]) > 250 else warnings[0]
            dosage_clean = dosage[0][:250] + "..." if len(dosage[0]) > 250 else dosage[0]

            resolved_brand = b_name if b_name else (g_name if g_name else drug_name.title())
            resolved_generic = g_name if g_name else resolved_brand

            return {
                "drug_name": drug_name,
                "brand_name": resolved_brand,
                "generic_name": resolved_generic,
                "active_ingredient": active_ingredients[0] if active_ingredients else "Not specified",
                "indications_and_usage": indications_clean,
                "warnings": warnings_clean,
                "dosage_and_administration": dosage_clean,
                "fda_verified": True,
                "fda_application_number": openfda_meta.get("application_number", ["N/A"])[0]
            }

    except Exception as exc:
        logger.warning("OpenFDA API request notice for '%s': %s", drug_name, exc)
        return None


def search_openfda_by_condition(condition: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Search OpenFDA for drugs indicated for a given medical condition or symptom keyword.
    """
    api_key = getattr(settings, "openfda_api_key", "AlqBpoXw03ITN1J2zteR2zg17gCnbQERlGQT3ema")

    # Clean condition string (remove parentheses, punctuation)
    clean_cond = re.sub(r"[^\w\s]", " ", condition.lower()).strip()
    # Pick primary medical keyword (e.g. 'stroke' for paralysis, 'vertigo' for vertigo, 'hypertension' for hypertension)
    keywords = [k for k in clean_cond.split() if len(k) > 3 and k not in ["paroymsal", "positional", "brain", "disease"]]
    search_keyword = keywords[0] if keywords else clean_cond

    params = {
        "api_key": api_key,
        "search": f'indications_and_usage:"{search_keyword}"',
        "limit": limit
    }

    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(OPENFDA_BASE_URL, params=params)
            if resp.status_code != 200:
                return []

            data = resp.json()
            results = data.get("results", [])
            drugs = []
            INVALID_TITLES = {"section", "because", "this", "table", "warning", "fda", "approved", "treatment", "page", "note"}
            for item in results:
                openfda_meta = item.get("openfda", {})
                b_name = openfda_meta.get("brand_name", [None])[0]
                g_name = openfda_meta.get("generic_name", [None])[0]
                active_ing_list = item.get("active_ingredient", openfda_meta.get("substance_name", []))
                active_ing = active_ing_list[0] if active_ing_list else None

                drug_title = b_name or g_name or active_ing
                if not drug_title or drug_title.strip().lower() in INVALID_TITLES:
                    drug_title = g_name or active_ing
                if not drug_title or drug_title.strip().lower() in INVALID_TITLES:
                    indications_raw = item.get("indications_and_usage", [""])[0]
                    match = re.search(r"usage\s+([a-zA-Z0-9\-]{3,20})\s+", indications_raw, re.IGNORECASE)
                    if match and match.group(1).lower() not in INVALID_TITLES:
                        drug_title = match.group(1).title()
                    else:
                        drug_title = "FDA Approved Treatment"

                indications_raw = item.get("indications_and_usage", [""])[0]
                indications_clean = clean_fda_indications(indications_raw)
                if len(indications_clean) > 250:
                    indications_clean = indications_clean[:250] + "..."

                drugs.append({
                    "drug_name": drug_title,
                    "brand_name": drug_title,
                    "generic_name": g_name or drug_title,
                    "active_ingredient": active_ing or drug_title,
                    "indications_and_usage": indications_clean,
                    "fda_verified": True
                })
            return drugs
    except Exception as exc:
        logger.warning("OpenFDA search by condition notice for '%s': %s", condition, exc)
        return []
