import { NavLink, Route, Routes } from 'react-router-dom'
import { Brief } from './pages/Brief'
import { Explorer } from './pages/Explorer'
import { Home } from './pages/Home'
import { Methodology } from './pages/Methodology'
import { Priorities } from './pages/Priorities'
import './App.css'

const nav: { to: string; label: string; end?: boolean }[] = [
  { to: '/', label: 'Home', end: true },
  { to: '/explorer', label: 'Explorer' },
  { to: '/priorities', label: 'Priorities' },
  { to: '/brief', label: 'Brief' },
  { to: '/methodology', label: 'Methodology' },
]

export default function App() {
  return (
    <div className="shell">
      <header className="topbar">
        <NavLink to="/" className="logo" end>
          FinAccess Compass
        </NavLink>
        <nav aria-label="Primary">
          {nav.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.end} className="nav-link">
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/explorer" element={<Explorer />} />
          <Route path="/priorities" element={<Priorities />} />
          <Route path="/brief" element={<Brief />} />
          <Route path="/methodology" element={<Methodology />} />
        </Routes>
      </main>
      <footer className="foot">
        NISR 2026 Big Data Hackathon · Track 2 · Evidence over decoration
      </footer>
    </div>
  )
}