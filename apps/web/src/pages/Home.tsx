import { Link } from 'react-router-dom'

export function Home() {
  return (
    <section className="page home">
      <p className="brand">FinAccess Compass Rwanda</p>
      <h1>Where should limited resources go first?</h1>
      <p className="lede">
        Explore verified poverty and financial-inclusion evidence, compare transparent priority
        scores against a poverty-only baseline, and generate a policy brief — without inventing
        numbers or claiming causal impact.
      </p>
      <div className="cta-row">
        <Link className="cta primary" to="/explorer">
          Start with Explorer
        </Link>
        <Link className="cta" to="/methodology">
          Methodology & limitations
        </Link>
      </div>
      <ol className="workflow">
        <li>
          <strong>Explore</strong> district gaps with sourced indicators
        </li>
        <li>
          <strong>Prioritise</strong> with explainable weights and baseline contrast
        </li>
        <li>
          <strong>Brief</strong> for a planning meeting — traceable and caveated
        </li>
      </ol>
    </section>
  )
}