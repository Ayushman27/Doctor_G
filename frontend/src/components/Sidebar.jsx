import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, ClipboardPlus, Pill, FlaskConical,
  Info, ChevronRight, Activity, Menu, X, MessageSquare
} from 'lucide-react'
import { useState } from 'react'

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, exact: true },
  { to: '/chat', label: 'Conversational Chat', icon: MessageSquare },
  { to: '/assessment', label: 'Patient Assessment', icon: ClipboardPlus },
  { to: '/drugs', label: 'Drug Candidates', icon: Pill },
  { to: '/model', label: 'Model Information', icon: FlaskConical },
  { to: '/about', label: 'About & Disclaimer', icon: Info },
]


export default function Sidebar({ modelVersion = '1.0.0' }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="px-4 py-5 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-[#00FFFF]/20 flex items-center justify-center shadow-sm">
            <Activity size={18} className="text-[#00FFFF]" />
          </div>
          <div>
            <div className="text-sm font-bold text-white leading-tight">DoctorG</div>
            <div className="text-xs text-slate-400 leading-tight">Diagnostic Assistant</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        <p className="section-title px-1 mb-4">Navigation</p>
        {navItems.map(({ to, label, icon: Icon, exact }) => {
          const isActive = exact
            ? location.pathname === to
            : location.pathname.startsWith(to)
          return (
            <NavLink
              key={to}
              to={to}
              onClick={() => setMobileOpen(false)}
              className={isActive ? 'nav-item-active' : 'nav-item'}
            >
              <Icon size={17} />
              <span className="flex-1">{label}</span>
              {isActive && <ChevronRight size={14} className="opacity-50" />}
            </NavLink>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-slate-800/80">
        <div className="text-xs text-slate-400 space-y-0.5">
          <div className="font-medium text-slate-500">Model v{modelVersion}</div>
          <div>Research Prototype</div>
          <div className="text-[10px] mt-1 text-slate-500 leading-snug">
            Not for clinical use
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <>
      {/* Mobile hamburger */}
      <button
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-[#0f172a] text-slate-200 rounded-xl shadow-lg border border-slate-700/80"
        onClick={() => setMobileOpen(!mobileOpen)}
        aria-label="Toggle menu"
      >
        {mobileOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="lg:hidden fixed inset-0 z-40 bg-black/30 backdrop-blur-sm"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Mobile drawer */}
      <aside
        className={`lg:hidden fixed top-0 left-0 z-40 h-full w-64 bg-[#080c16] border-r border-slate-800/80 shadow-2xl
                    transform transition-transform duration-300
                    ${mobileOpen ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <SidebarContent />
      </aside>

      {/* Desktop sidebar */}
      <aside className="hidden lg:flex flex-col w-60 min-h-screen bg-[#080c16] border-r border-slate-800/80 shadow-sm ring-1 ring-white/5 flex-shrink-0">
        <SidebarContent />
      </aside>
    </>
  )
}
