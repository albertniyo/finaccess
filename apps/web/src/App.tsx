import type { ComponentType, SVGProps } from 'react'
import { Link, NavLink, Route, Routes, useLocation } from 'react-router-dom'
import { getHealth } from './api/client'
import { ErrorBoundary } from './components/ErrorBoundary'
import { BookIcon, BriefIcon, CheckIcon, CompassMark, HomeIcon, MapIcon, RankIcon } from './components/Icons'
import { useApi } from './hooks/useApi'
import { useDocumentTitle } from './hooks/useDocumentTitle'
import { Brief } from './pages/Brief'
import { Explorer } from './pages/Explorer'
import { Home } from './pages/Home'
import { Methodology } from './pages/Methodology'
import { Priorities } from './pages/Priorities'
import './App.css'

type NavItem = {
  to: string
  label: string
  step?: string
  end?: boolean
  carry?: boolean
  icon: ComponentType<SVGProps<SVGSVGElement>>
}

const nav: NavItem[] = [
  { to: '/', label: 'Overview', end: true, icon: HomeIcon },
  { to: '/explorer', label: 'Explore gaps', step: '1', carry: true, icon: MapIcon },
  { to: '/priorities', label: 'Prioritise', step: '2', carry: true, icon: RankIcon },
  { to: '/brief', label: 'Policy brief', step: '3', carry: true, icon: BriefIcon },
  { to: '/methodology', label: 'Methodology & impact', icon: BookIcon },
]

function NotFound() {
  useDocumentTitle('Page not found')
  return (
    <section className="page">
      <h1>Page not found</h1>
      <p>
        <Link to="/">Back to the overview</Link>
      </p>
    </section>
  )
}

function EvidenceStatus() {
  const health = useApi('health', getHealth)
  const v = health.data?.validation
  const ok = health.data?.data === 'ok' && v?.failed === 0
  return (
    <div className="status-card" aria-live="polite">
      <p className="status-title">Evidence status</p>
      {health.error ? (
        <p className="status-line warn">API unreachable</p>
      ) : !health.data ? (
        <p className="status-line">Waking the API…</p>
      ) : (
        <>
          <p className={`status-line ${ok ? 'ok' : 'warn'}`}>
            {ok && <CheckIcon width={16} height={16} />} {v?.passed ?? 0} checks passing
          </p>
          <p className="status-sub">
            {health.data.districts} districts · EICV7 2023/24 · FinScope 2024
          </p>
        </>
      )}
    </div>
  )
}

export default function App() {
  const { search, pathname } = useLocation()
  return (
    <div className="shell">
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <aside className="sidebar no-print">
        <NavLink to="/" className="logo" end aria-label="FinAccess Compass Rwanda — overview">
          <CompassMark />
          <span>
            <span className="logo-name">FinAccess Compass</span>
            <span className="logo-sub">Rwanda</span>
          </span>
        </NavLink>
        <nav aria-label="Primary" className="side-nav">
          {nav.map(({ icon: Icon, ...item }) => (
            <NavLink
              key={item.to}
              to={item.carry ? { pathname: item.to, search } : item.to}
              end={item.end}
              className="nav-link"
            >
              <Icon />
              <span className="nav-label">{item.label}</span>
              {item.step && <span className="nav-step">{item.step}</span>}
            </NavLink>
          ))}
        </nav>
        <EvidenceStatus />
      </aside>
      <div className="content">
        <main id="main">
          <ErrorBoundary key={pathname}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/explorer" element={<Explorer />} />
              <Route path="/priorities" element={<Priorities />} />
              <Route path="/brief" element={<Brief />} />
              <Route path="/methodology" element={<Methodology />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </ErrorBoundary>
        </main>
        <footer className="foot no-print">
          NISR 2026 Big Data Hackathon · Track 2 · Data: NISR EICV7 2023/24 & FinScope Rwanda 2024 · No endorsement by
          NISR or AFR implied
        </footer>
      </div>
    </div>
  )
}
