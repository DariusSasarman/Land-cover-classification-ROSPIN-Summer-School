export default function Header({ activeTab, setActiveTab }) {
  const isActive = (tab) => (activeTab === tab ? 'is-active' : '')

  return (
    <header className="site-header">
      <div className="site-header__inner">
        <a className="brand" onClick={() => setActiveTab('hero')}>
          <span className="brand__icon" aria-hidden="true">🌍</span>
          <span className="brand__text">Land<span>Observator</span></span>
        </a>
        <nav className="site-nav" aria-label="Main">
          <a className={isActive('demos')} onClick={() => setActiveTab('demos')}>Public demos</a>
          <a className={isActive('how-it-works')} onClick={() => setActiveTab('how-it-works')}>How it works</a>
          <a className={`site-nav__cta ${isActive('request')}`} onClick={() => setActiveTab('request')}>Request AOI</a>
        </nav>
      </div>
    </header>
  )
}