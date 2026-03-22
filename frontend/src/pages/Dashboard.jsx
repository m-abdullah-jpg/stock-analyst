import { useState, useEffect } from 'react'
import { getTopPicks, getSummary } from '../api/client'
import SignalBadge from '../components/SignalBadge'

export default function Dashboard() {
    const [picks, setPicks] = useState(null)
    const [summary, setSummary] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        Promise.all([getTopPicks(), getSummary()])
            .then(([p, s]) => { setPicks(p); setSummary(s) })
            .catch(e => setError(e.message))
            .finally(() => setLoading(false))
    }, [])

    if (loading) return <div style={styles.loading}>Loading predictions...</div>
    if (error) return <div style={styles.error}>API error: {error} — is the FastAPI server running?</div>

    return (
        <div style={styles.page}>
            <div style={styles.header}>
                <h1 style={styles.title}>Stock Analyst Dashboard</h1>
                <span style={styles.sub}>AI-powered predictions · {new Date().toLocaleDateString()}</span>
            </div>

            <section style={styles.section}>
                <h2 style={styles.sectionTitle}>Top picks today</h2>
                <div style={styles.picksGrid}>
                    {picks?.picks.map(p => (
                        <div key={p.ticker} style={styles.pickCard}>
                            <div style={styles.pickHeader}>
                                <span style={styles.ticker}>{p.ticker}</span>
                                <SignalBadge signal={p.signal_5d} />
                            </div>
                            <div style={styles.price}>${p.close.toFixed(2)}</div>
                            <div style={styles.pickMeta}>
                                <span>5d: <b>{p.confidence_5d.toFixed(1)}%</b></span>
                                <span>20d: <SignalBadge signal={p.signal_20d} /></span>
                            </div>
                            <div style={styles.pickMeta}>
                                <span style={{
                                    color: p.sentiment === 'bullish' ? '#1d9e75' :
                                        p.sentiment === 'bearish' ? '#d85a30' : '#888'
                                }}>
                                    {p.sentiment}
                                </span>
                                <span>RSI {p.rsi.toFixed(1)}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            <section style={styles.section}>
                <h2 style={styles.sectionTitle}>All tickers</h2>
                <table style={styles.table}>
                    <thead>
                        <tr style={styles.thead}>
                            {['Ticker', 'Price', '5d Signal', 'Conf', '20d Signal', 'Conf', 'Sentiment', 'RSI'].map(h => (
                                <th key={h} style={styles.th}>{h}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {summary?.tickers.map(t => (
                            <tr key={t.ticker} style={styles.tr}>
                                <td style={{ ...styles.td, fontWeight: 500 }}>{t.ticker}</td>
                                <td style={styles.td}>${t.close.toFixed(2)}</td>
                                <td style={styles.td}><SignalBadge signal={t.signal_5d} /></td>
                                <td style={styles.td}>{t.confidence_5d.toFixed(1)}%</td>
                                <td style={styles.td}><SignalBadge signal={t.signal_20d} /></td>
                                <td style={styles.td}>{t.confidence_20d.toFixed(1)}%</td>
                                <td style={{ ...styles.td, color: t.sentiment === 'bullish' ? '#1d9e75' : t.sentiment === 'bearish' ? '#d85a30' : '#888' }}>{t.sentiment}</td>
                                <td style={styles.td}>{t.rsi.toFixed(1)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </section>
        </div>
    )
}

const styles = {
    page: { maxWidth: 1100, margin: '0 auto', padding: '2rem 1.5rem', fontFamily: 'system-ui,sans-serif' },
    header: { marginBottom: '2rem' },
    title: { fontSize: 28, fontWeight: 600, margin: 0 },
    sub: { fontSize: 14, color: '#888' },
    section: { marginBottom: '2.5rem' },
    sectionTitle: { fontSize: 18, fontWeight: 500, marginBottom: '1rem', color: '#333' },
    picksGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(200px,1fr))', gap: 12 },
    pickCard: { background: '#fff', border: '1px solid #eee', borderRadius: 12, padding: '1rem', display: 'flex', flexDirection: 'column', gap: 8 },
    pickHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
    ticker: { fontSize: 18, fontWeight: 600 },
    price: { fontSize: 22, fontWeight: 500, color: '#185fa5' },
    pickMeta: { display: 'flex', justifyContent: 'space-between', fontSize: 13, color: '#666' },
    table: { width: '100%', borderCollapse: 'collapse', fontSize: 14 },
    thead: { background: '#f8f8f6' },
    th: { padding: '10px 12px', textAlign: 'left', fontWeight: 500, color: '#555', borderBottom: '1px solid #eee' },
    tr: { borderBottom: '1px solid #f0f0f0' },
    td: { padding: '10px 12px', color: '#333' },
    loading: { padding: '3rem', textAlign: 'center', color: '#888', fontFamily: 'system-ui' },
    error: { padding: '2rem', color: '#d85a30', fontFamily: 'system-ui', background: '#fff4f0', borderRadius: 8, margin: '2rem' },
}
