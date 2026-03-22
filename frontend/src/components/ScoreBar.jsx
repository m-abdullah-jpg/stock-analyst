export default function ScoreBar({ value, max = 100, label }) {
    const pct = Math.min(100, Math.max(0, (value / max) * 100))
    const color = pct >= 65 ? '#1d9e75' : pct >= 45 ? '#378add' : '#d85a30'
    return (
        <div style={{ marginBottom: 8 }}>
            {label && <div style={{ fontSize: 12, color: '#888', marginBottom: 3 }}>{label}</div>}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div style={{ flex: 1, height: 6, background: '#eee', borderRadius: 3, overflow: 'hidden' }}>
                    <div style={{
                        width: `${pct}%`, height: '100%', background: color,
                        borderRadius: 3, transition: 'width 0.5s ease'
                    }} />
                </div>
                <span style={{ fontSize: 12, fontWeight: 500, color, minWidth: 36 }}>
                    {value.toFixed(1)}{max === 100 ? '%' : ''}
                </span>
            </div>
        </div>
    )
}