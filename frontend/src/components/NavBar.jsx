import { Link, useLocation } from 'react-router-dom'

const links = [
    { to: '/', label: 'Dashboard' },
    { to: '/analyze', label: 'Analyze' },
    { to: '/sentiment', label: 'Sentiment' },
]

export default function NavBar() {
    const { pathname } = useLocation()
    return (
        <nav style={styles.nav}>
            <span style={styles.logo}>Stock Analyst</span>
            <div style={styles.links}>
                {links.map(l => (
                    <Link key={l.to} to={l.to} style={{
                        ...styles.link,
                        ...(pathname === l.to ? styles.active : {})
                    }}>{l.label}</Link>
                ))}
            </div>
        </nav>
    )
}

const styles = {
    nav: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 2rem', height: 56, background: '#fff', borderBottom: '1px solid #eee', fontFamily: 'system-ui,sans-serif' },
    logo: { fontSize: 17, fontWeight: 600, color: '#1a1a1a' },
    links: { display: 'flex', gap: 4 },
    link: { padding: '6px 14px', borderRadius: 8, fontSize: 14, color: '#555', textDecoration: 'none', transition: 'all 0.15s' },
    active: { background: '#f1efe8', color: '#1a1a1a', fontWeight: 500 },
}