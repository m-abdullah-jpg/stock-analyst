import { useState } from 'react'
import { analyzeTicker } from '../api/client'
import SignalBadge from '../components/SignalBadge'
import ScoreBar from '../components/ScoreBar'
import MetricCard from '../components/MetricCard'

const TICKERS = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'TSLA', 'JPM', 'LLY', 'V']

export default function Analyze() {
    const [ticker, setTicker] = useState('NVDA')
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    async function run() {
        setLoading(true); setError(null)
        try { setResult(await analyzeTicker(ticker)) }
        catch (e) { setError(e.response?.data?.detail || e.message) }
        finally { setLoading(false) }
    }

    return (
        <div style={styles.page}>
            <h1 style={styles.title}>Analyze a stock</h1>

            <div style={styles.controls}>
                <select value={ticker} onChange={e => setTicker(e.target.value)} style={styles.select}>
                    {TICKERS.map(t => <option key={t}>{t}</option>)}
                </select>
                <button onClick={run} disabled={loading} style={styles.btn}>
                    {loading ? 'Analyzing...' : 'Run Analysis'}
                </button>
            </div>

            {error && <div style={styles.error}>{error}</div>}

            {result && (
                <div style={styles.results}>
                    <div style={styles.topRow}>
                        <div>
                            <span style={styles.tickerLabel}>{result.ticker}</span>
                            <span style={styles.priceLabel}>${result.close.toFixed(2)}</span>
                        </div>
                        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                            <SignalBadge signal={result.signal_5d} />
                            <SignalBadge signal={result.signal_20d} />
                        </div>
                    </div>

                    <div style={styles.metricsRow}>
                        <MetricCard label="5-day confidence" value={result.confidence_5d.toFixed(1) + '%'}
                            color={result.confidence_5d > 60 ? '#1d9e75' : '#185fa5'} />
                        <MetricCard label="20-day confidence" value={result.confidence_20d.toFixed(1) + '%'}
                            color={result.confidence_20d > 60 ? '#1d9e75' : '#185fa5'} />
                        <MetricCard label="RSI" value={result.rsi.toFixed(1)}
                            color={result.rsi > 70 ? '#d85a30' : result.rsi < 30 ? '#1d9e75' : '#333'}
                            sub={result.rsi > 70 ? 'Overbought' : result.rsi < 30 ? 'Oversold' : 'Neutral'} />
                        <MetricCard label="Sentiment" value={result.sentiment}
                            color={result.sentiment === 'bullish' ? '#1d9e75' : result.sentiment === 'bearish' ? '#d85a30' : '#888'} />
                    </div>

                    <div style={styles.barsSection}>
                        <ScoreBar value={result.confidence_5d} label="5-day model confidence" />
                        <ScoreBar value={result.confidence_20d} label="20-day model confidence" />
                        <ScoreBar value={result.rsi} label="RSI (0–100)" />
                        <ScoreBar value={(result.sentiment_score + 1) * 50} label="Sentiment score" />
                    </div>

                    {(result.pe_ratio || result.forward_pe) && (
                        <div style={styles.fundRow}>
                            <h3 style={styles.fundTitle}>Fundamentals</h3>
                            <div style={styles.metricsRow}>
                                {result.pe_ratio && <MetricCard label="P/E ratio" value={result.pe_ratio.toFixed(1)} />}
                                {result.forward_pe && <MetricCard label="Forward P/E" value={result.forward_pe.toFixed(1)} />}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}

const styles = {
    page: { maxWidth: 900, margin: '0 auto', padding: '2rem 1.5rem', fontFamily: 'system-ui,sans-serif' },
    title: { fontSize: 24, fontWeight: 600, marginBottom: '1.5rem' },
    controls: { display: 'flex', gap: 12, marginBottom: '1.5rem' },
    select: { padding: '8px 12px', fontSize: 15, borderRadius: 8, border: '1px solid #ddd', minWidth: 160 },
    btn: { padding: '8px 20px', fontSize: 15, fontWeight: 500, background: '#1a1a1a', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer' },
    error: { padding: '1rem', color: '#d85a30', background: '#fff4f0', borderRadius: 8, marginBottom: '1rem' },
    results: { display: 'flex', flexDirection: 'column', gap: '1.5rem' },
    topRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', background: '#fff', border: '1px solid #eee', borderRadius: 12 },
    tickerLabel: { fontSize: 28, fontWeight: 700, marginRight: 12 },
    priceLabel: { fontSize: 22, color: '#185fa5', fontWeight: 500 },
    metricsRow: { display: 'flex', gap: 10, flexWrap: 'wrap' },
    barsSection: { background: '#fff', border: '1px solid #eee', borderRadius: 12, padding: '1.25rem' },
    fundRow: { background: '#fff', border: '1px solid #eee', borderRadius: 12, padding: '1.25rem' },
    fundTitle: { fontSize: 15, fontWeight: 500, marginBottom: '0.75rem', color: '#555' },
}
