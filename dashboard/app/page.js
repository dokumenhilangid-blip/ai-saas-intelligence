'use client'
import { useState, useEffect } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://web-production-a696.up.railway.app'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [tools, setTools] = useState([])
  const [trending, setTrending] = useState([])
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    fetchAll()
  }, [])

  async function fetchAll() {
    try {
      const [statsRes, toolsRes, trendingRes, sourcesRes] = await Promise.all([
        fetch(`${API_URL}/stats`),
        fetch(`${API_URL}/tools?limit=50`),
        fetch(`${API_URL}/trending?limit=10`),
        fetch(`${API_URL}/sources`)
      ])
      setStats(await statsRes.json())
      const toolsData = await toolsRes.json()
      setTools(toolsData.data || [])
      const trendingData = await trendingRes.json()
      setTrending(trendingData.data || [])
      const sourcesData = await sourcesRes.json()
      setSources(sourcesData.sources || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const filtered = tools.filter(t =>
    t.name?.toLowerCase().includes(search.toLowerCase()) ||
    t.description?.toLowerCase().includes(search.toLowerCase())
  )

  if (loading) return (
    <div style={styles.center}>
      <div style={styles.loader}>⚡ Loading intelligence data...</div>
    </div>
  )

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>🔍 AI SaaS Intelligence</h1>
          <p style={styles.subtitle}>Real-time market intelligence engine</p>
        </div>
        <button onClick={fetchAll} style={styles.refreshBtn}>↻ Refresh</button>
      </div>

      {/* Stats Cards */}
      <div style={styles.statsGrid}>
        <StatCard label="Total Tools" value={stats?.total_tools || 0} icon="🛠️" />
        <StatCard label="Data Sources" value={Object.keys(stats?.by_source || {}).length} icon="📡" />
        <StatCard label="Insights" value={stats?.total_insights || 0} icon="💡" />
        <StatCard label="Status" value="LIVE" icon="🟢" />
      </div>

      {/* Tabs */}
      <div style={styles.tabs}>
        {['overview', 'tools', 'trending', 'sources'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              ...styles.tab,
              ...(activeTab === tab ? styles.tabActive : {})
            }}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div>
          <h2 style={styles.sectionTitle}>Sources Breakdown</h2>
          <div style={styles.sourceGrid}>
            {sources.map(s => (
              <div key={s.source} style={styles.sourceCard}>
                <div style={styles.sourceName}>{s.source}</div>
                <div style={styles.sourceCount}>{s.count} tools</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'tools' && (
        <div>
          <input
            placeholder="🔍 Search tools..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={styles.searchInput}
          />
          <p style={styles.resultCount}>{filtered.length} tools found</p>
          <div style={styles.toolGrid}>
            {filtered.map(t => (
              <ToolCard key={t.id} tool={t} />
            ))}
          </div>
        </div>
      )}

      {activeTab === 'trending' && (
        <div>
          <h2 style={styles.sectionTitle}>🔥 Trending Tools</h2>
          {trending.length === 0 ? (
            <p style={styles.empty}>No trending data yet. Run scraper first.</p>
          ) : (
            <div style={styles.toolGrid}>
              {trending.map(t => (
                <ToolCard key={t.id} tool={t} showScore />
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'sources' && (
        <div>
          <h2 style={styles.sectionTitle}>📡 Data Sources</h2>
          {sources.map(s => (
            <div key={s.source} style={styles.sourceRow}>
              <span style={styles.sourceName}>{s.source}</span>
              <div style={styles.barContainer}>
                <div style={{
                  ...styles.bar,
                  width: `${Math.min((s.count / (stats?.total_tools || 1)) * 100 * 3, 100)}%`
                }} />
              </div>
              <span style={styles.sourceCount}>{s.count}</span>
            </div>
          ))}
        </div>
      )}

      <div style={styles.footer}>
        API: {API_URL} · Last updated: {stats?.last_updated?.slice(0, 10) || 'Never'}
      </div>
    </div>
  )
}

function StatCard({ label, value, icon }) {
  return (
    <div style={styles.statCard}>
      <div style={styles.statIcon}>{icon}</div>
      <div style={styles.statValue}>{value}</div>
      <div style={styles.statLabel}>{label}</div>
    </div>
  )
}

function ToolCard({ tool, showScore }) {
  return (
    <div style={styles.toolCard}>
      <div style={styles.toolName}>{tool.name}</div>
      {tool.description && (
        <div style={styles.toolDesc}>{tool.description.slice(0, 100)}...</div>
      )}
      <div style={styles.toolMeta}>
        <span style={styles.badge}>{tool.source}</span>
        {tool.category && <span style={styles.badge}>{tool.category}</span>}
        {showScore && tool.upvotes > 0 && (
          <span style={styles.badgeGreen}>▲ {tool.upvotes}</span>
        )}
      </div>
      {tool.url && (
        <a href={tool.url} target="_blank" rel="noreferrer" style={styles.link}>
          Visit →
        </a>
      )}
    </div>
  )
}

const styles = {
  container: { maxWidth: 1200, margin: '0 auto', padding: '20px 16px' },
  center: { display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' },
  loader: { fontSize: 20, color: '#888' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 },
  title: { fontSize: 28, fontWeight: 700, margin: 0, color: '#fff' },
  subtitle: { color: '#666', margin: '4px 0 0', fontSize: 14 },
  refreshBtn: { background: '#1a1a1a', border: '1px solid #333', color: '#fff', padding: '8px 16px', borderRadius: 8, cursor: 'pointer' },
  statsGrid: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 24 },
  statCard: { background: '#111', border: '1px solid #222', borderRadius: 12, padding: 16, textAlign: 'center' },
  statIcon: { fontSize: 24, marginBottom: 8 },
  statValue: { fontSize: 28, fontWeight: 700, color: '#fff' },
  statLabel: { fontSize: 12, color: '#666', marginTop: 4 },
  tabs: { display: 'flex', gap: 8, marginBottom: 24, borderBottom: '1px solid #222', paddingBottom: 8 },
  tab: { background: 'none', border: 'none', color: '#666', padding: '8px 16px', cursor: 'pointer', borderRadius: 8, fontSize: 14 },
  tabActive: { background: '#1a1a1a', color: '#fff', border: '1px solid #333' },
  sectionTitle: { fontSize: 18, fontWeight: 600, marginBottom: 16, color: '#fff' },
  sourceGrid: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 },
  sourceCard: { background: '#111', border: '1px solid #222', borderRadius: 8, padding: 16 },
  sourceName: { fontWeight: 600, color: '#fff', marginBottom: 4 },
  sourceCount: { color: '#666', fontSize: 13 },
  sourceRow: { display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 },
  barContainer: { flex: 1, background: '#1a1a1a', borderRadius: 4, height: 8 },
  bar: { background: '#3b82f6', height: 8, borderRadius: 4, transition: 'width 0.3s' },
  searchInput: { width: '100%', background: '#111', border: '1px solid #333', color: '#fff', padding: '10px 14px', borderRadius: 8, fontSize: 14, marginBottom: 12, boxSizing: 'border-box' },
  resultCount: { color: '#666', fontSize: 13, marginBottom: 16 },
  toolGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 12 },
  toolCard: { background: '#111', border: '1px solid #222', borderRadius: 12, padding: 16 },
  toolName: { fontWeight: 600, fontSize: 15, color: '#fff', marginBottom: 6 },
  toolDesc: { color: '#888', fontSize: 13, marginBottom: 10, lineHeight: 1.4 },
  toolMeta: { display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 8 },
  badge: { background: '#1a1a1a', border: '1px solid #333', color: '#888', padding: '2px 8px', borderRadius: 4, fontSize: 11 },
  badgeGreen: { background: '#0d2818', border: '1px solid #1a4731', color: '#4ade80', padding: '2px 8px', borderRadius: 4, fontSize: 11 },
  link: { color: '#3b82f6', fontSize: 13, textDecoration: 'none' },
  empty: { color: '#666', textAlign: 'center', padding: 40 },
  footer: { textAlign: 'center', color: '#444', fontSize: 12, marginTop: 40, paddingTop: 20, borderTop: '1px solid #1a1a1a' }
    }
