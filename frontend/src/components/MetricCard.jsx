export default function MetricCard({ label, value, sub, color }) {
    return (
        <div style={{
            background: '#f8f8f6', borderRadius: 8,
            padding: '12px 16px', flex: 1, minWidth: 0
        }}>
            <div style={{ fontSize: 12, color: '#888', marginBottom: 4 }}>{label}</div>
            <div style={{ fontSize: 22, fontWeight: 500, color: color || '#1a1a1a' }}>{value}</div>
            {sub && <div style={{ fontSize: 11, color: '#aaa', marginTop: 2 }}>{sub}</div>}
        </div>
    )
}
