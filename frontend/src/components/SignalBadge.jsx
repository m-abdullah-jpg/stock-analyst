export default function SignalBadge({ signal }) {
    const styles = {
        'Strong Buy': { bg: '#e1f5ee', color: '#085041', border: '#1d9e75' },
        'Buy': { bg: '#eef6ff', color: '#0c447c', border: '#378add' },
        'Hold': { bg: '#f1efe8', color: '#5f5e5a', border: '#b4b2a9' },
        'Sell': { bg: '#fff4e6', color: '#633806', border: '#ef9f27' },
        'Strong Sell': { bg: '#fcebeb', color: '#791f1f', border: '#e24b4a' },
    }
    const s = styles[signal] || styles['Hold']
    return (
        <span style={{
            background: s.bg, color: s.color,
            border: `1px solid ${s.border}`,
            borderRadius: 6, fontSize: 12, fontWeight: 500,
            padding: '3px 10px', whiteSpace: 'nowrap'
        }}>{signal}</span>
    )
}