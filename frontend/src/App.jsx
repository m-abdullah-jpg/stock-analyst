import { BrowserRouter, Routes, Route } from 'react-router-dom'
import NavBar from './components/NavBar'
import Dashboard from './pages/Dashboard'
import Analyze from './pages/Analyze'

// Simple sentiment page — calls /sentiment/{ticker}
import { useState } from 'react'
import { getSentiment } from './api/client'

function Sentiment() {
  const [ticker, setTicker] = useState('NVDA')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const TICKERS = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'TSLA', 'JPM', 'LLY', 'V']

  async function run() {
    setLoading(true)
    try { setData(await getSentiment(ticker)) }
    finally { setLoading(false) }
  }

  const scoreColor = data
    ? data.score > 0.1 ? '#1d9e75' : data.score < -0.1 ? '#d85a30' : '#888'
    : '#333'

  return (
    <div style={{ maxWidth: 600, margin: '2rem auto', padding: '0 1.5rem', fontFamily: 'system-ui,sans-serif' }}>
      <h1 style={{ fontSize: 24, fontWeight: 600, marginBottom: '1.5rem' }}>Sentiment analysis</h1>
      <div style={{ display: 'flex', gap: 12, marginBottom: '1.5rem' }}>
        <select value={ticker} onChange={e => setTicker(e.target.value)}
          style={{ padding: '8px 12px', fontSize: 15, borderRadius: 8, border: '1px solid #ddd' }}>
          {TICKERS.map(t => <option key={t}>{t}</option>)}
        </select>
        <button onClick={run} disabled={loading}
          style={{ padding: '8px 20px', fontSize: 15, fontWeight: 500, background: '#1a1a1a', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer' }}>
          {loading ? 'Loading...' : 'Get Sentiment'}
        </button>
      </div>
      {data && (
        <div style={{ background: '#fff', border: '1px solid #eee', borderRadius: 12, padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <span style={{ fontSize: 20, fontWeight: 600 }}>{data.ticker}</span>
            <span style={{ fontSize: 20, fontWeight: 500, color: scoreColor }}>{data.label}</span>
          </div>
          <div style={{ fontSize: 36, fontWeight: 700, color: scoreColor, marginBottom: '1rem' }}>
            {data.score > 0 ? '+' : ''}{data.score.toFixed(3)}
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, fontSize: 14, color: '#666' }}>
            <div>Headlines analysed: <b style={{ color: '#333' }}>{data.count}</b></div>
            <div>Momentum: <b style={{ color: scoreColor }}>{data.momentum > 0 ? '+' : ''}{data.momentum.toFixed(3)}</b></div>
            <div>Positive: <b style={{ color: '#1d9e75' }}>{data.pos_pct.toFixed(1)}%</b></div>
            <div>Negative: <b style={{ color: '#d85a30' }}>{data.neg_pct.toFixed(1)}%</b></div>
          </div>
        </div>
      )}
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <NavBar />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/analyze" element={<Analyze />} />
        <Route path="/sentiment" element={<Sentiment />} />
      </Routes>
    </BrowserRouter>
  )
}