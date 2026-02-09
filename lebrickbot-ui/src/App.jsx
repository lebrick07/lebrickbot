import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [deployments, setDeployments] = useState([
    { id: 1, name: 'api-gateway', status: 'running', time: '2m ago', cost: '$0.12/hr' },
    { id: 2, name: 'auth-service', status: 'running', time: '5m ago', cost: '$0.08/hr' },
    { id: 3, name: 'database-cluster', status: 'healthy', time: '1h ago', cost: '$0.45/hr' }
  ])
  
  const [logs, setLogs] = useState([
    { time: '11:32:15', level: 'info', message: 'ArgoCD sync completed successfully' },
    { time: '11:31:42', level: 'success', message: 'Deployment api-gateway scaled to 3 replicas' },
    { time: '11:30:08', level: 'info', message: 'Image pull completed: backend:latest' },
    { time: '11:29:33', level: 'warning', message: 'Resolved ghcr.io authentication issue' },
    { time: '11:28:45', level: 'info', message: 'Triage agent detected ImagePullBackOff' }
  ])

  const [stats, setStats] = useState({
    deploymentsToday: 12,
    activeServices: 8,
    costThisMonth: '$142.35',
    uptime: '99.98%'
  })

  useEffect(() => {
    // Test API connectivity
    fetch('/api/')
      .then(res => res.json())
      .then(data => console.log('Backend connected:', data))
      .catch(err => console.log('Backend offline:', err))
  }, [])

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="header">
        <div className="logo">
          <span className="logo-icon">🤖</span>
          <h1>LeBrickBot</h1>
        </div>
        <nav className="nav">
          <a href="#deployments">Deployments</a>
          <a href="#monitoring">Monitoring</a>
          <a href="#costs">Costs</a>
          <a href="#settings">Settings</a>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <h2>Autonomous DevOps Platform</h2>
        <p>Replace your entire DevOps team with AI-powered infrastructure management</p>
        <div className="hero-features">
          <div className="feature">
            <span className="feature-icon">🚀</span>
            <span>Auto-Deploy</span>
          </div>
          <div className="feature">
            <span className="feature-icon">🔧</span>
            <span>Self-Heal</span>
          </div>
          <div className="feature">
            <span className="feature-icon">💰</span>
            <span>Cost Optimize</span>
          </div>
          <div className="feature">
            <span className="feature-icon">📊</span>
            <span>Real-time Monitor</span>
          </div>
        </div>
      </section>

      {/* Stats Grid */}
      <section className="stats">
        <div className="stat-card">
          <div className="stat-value">{stats.deploymentsToday}</div>
          <div className="stat-label">Deployments Today</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.activeServices}</div>
          <div className="stat-label">Active Services</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.costThisMonth}</div>
          <div className="stat-label">Cost This Month</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.uptime}</div>
          <div className="stat-label">Uptime</div>
        </div>
      </section>

      {/* Main Content */}
      <div className="content">
        {/* Deployments */}
        <section className="section deployments-section">
          <h3>Active Deployments</h3>
          <div className="deployments-list">
            {deployments.map(dep => (
              <div key={dep.id} className="deployment-card">
                <div className="deployment-header">
                  <span className="deployment-name">{dep.name}</span>
                  <span className={`deployment-status status-${dep.status}`}>{dep.status}</span>
                </div>
                <div className="deployment-meta">
                  <span className="deployment-time">⏱ {dep.time}</span>
                  <span className="deployment-cost">💰 {dep.cost}</span>
                </div>
              </div>
            ))}
          </div>
          <button className="btn-primary">Deploy New Service</button>
        </section>

        {/* Activity Logs */}
        <section className="section logs-section">
          <h3>Activity Logs</h3>
          <div className="logs-list">
            {logs.map((log, idx) => (
              <div key={idx} className={`log-entry log-${log.level}`}>
                <span className="log-time">{log.time}</span>
                <span className="log-level">[{log.level.toUpperCase()}]</span>
                <span className="log-message">{log.message}</span>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* Footer */}
      <footer className="footer">
        <p>LeBrickBot v0.1.0 - Autonomous DevOps Platform</p>
        <p>Powered by GitOps • K3s • ArgoCD • FastAPI</p>
      </footer>
    </div>
  )
}

export default App
