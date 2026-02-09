import { useState, useEffect } from 'react'
import './App.css'
import DeployModal from './components/DeployModal'
import ActionModal from './components/ActionModal'
import Toast from './components/Toast'
import IntegrationsDashboard from './components/IntegrationsDashboard'
import CostWidget from './components/CostWidget'
import AlertsPanel from './components/AlertsPanel'
import SettingsPage from './components/SettingsPage'

function App() {
  const [deployments, setDeployments] = useState([])
  const [customers, setCustomers] = useState([])
  
  const [logs, setLogs] = useState([
    { time: '12:39:15', level: 'success', message: 'All 3 customer apps deployed successfully' },
    { time: '12:38:42', level: 'info', message: 'ArgoCD synced widgetco-api' },
    { time: '12:38:24', level: 'info', message: 'ArgoCD synced techstart-webapp' },
    { time: '12:38:11', level: 'info', message: 'ArgoCD synced acme-corp-api' },
    { time: '12:37:45', level: 'info', message: 'Created K8s namespaces for 3 customers' }
  ])

  const [stats, setStats] = useState({
    deploymentsToday: 3,
    activeServices: 0,
    costThisMonth: '$142.35',
    uptime: '99.98%'
  })

  const [showDeployModal, setShowDeployModal] = useState(false)
  const [showActionModal, setShowActionModal] = useState(false)
  const [selectedDeployment, setSelectedDeployment] = useState(null)
  const [selectedAction, setSelectedAction] = useState(null)
  const [toast, setToast] = useState(null)
  const [loading, setLoading] = useState(false)
  const [currentView, setCurrentView] = useState('deployments')
  const [theme, setTheme] = useState('dark')
  const [searchQuery, setSearchQuery] = useState('')
  const [isInitialLoad, setIsInitialLoad] = useState(true)

  useEffect(() => {
    // Fetch real data from backend
    fetchCustomers()
    fetchDeployments()
    
    // Set up polling
    const interval = setInterval(() => {
      fetchCustomers()
      fetchDeployments()
    }, 10000) // Refresh every 10 seconds
    
    return () => clearInterval(interval)
  }, [])

  const fetchCustomers = async () => {
    try {
      const res = await fetch('/api/customers')
      const data = await res.json()
      setCustomers(data.customers || [])
      setStats(prev => ({
        ...prev,
        activeServices: data.customers?.filter(c => c.status === 'running').length || 0
      }))
      setIsInitialLoad(false)
    } catch (err) {
      console.error('Failed to fetch customers:', err)
      setIsInitialLoad(false)
    }
  }

  const fetchDeployments = async () => {
    try {
      const res = await fetch('/api/deployments')
      const data = await res.json()
      setDeployments(data.deployments?.map(d => ({
        id: d.id,
        name: d.name,
        status: d.status,
        replicas: d.replicas,
        time: 'live',
        cost: '$0.05/hr',
        customer: d.customer,
        namespace: d.namespace
      })) || [])
    } catch (err) {
      console.error('Failed to fetch deployments:', err)
    }
  }

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  const showToast = (message, type = 'info') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 4000)
  }

  const addLog = (message, level = 'info') => {
    const now = new Date()
    const time = now.toLocaleTimeString('en-US', { hour12: false })
    setLogs(prev => [{ time, level, message }, ...prev].slice(0, 20))
  }

  const handleDeploy = async (service) => {
    setLoading(true)
    addLog(`Initiating deployment: ${service.name}`, 'info')
    
    setTimeout(() => {
      showToast(`${service.name} deployment triggered`, 'success')
      setShowDeployModal(false)
      setLoading(false)
      fetchDeployments()
    }, 2000)
  }

  const handleAction = (deployment, action) => {
    setSelectedDeployment(deployment)
    setSelectedAction(action)
    setShowActionModal(true)
  }

  const executeAction = async () => {
    setLoading(true)
    const { name } = selectedDeployment
    
    addLog(`Executing ${selectedAction} on ${name}`, 'info')
    
    setTimeout(() => {
      showToast(`${selectedAction} action completed on ${name}`, 'success')
      setShowActionModal(false)
      setLoading(false)
      fetchDeployments()
    }, 1500)
  }

  const filteredDeployments = deployments.filter(d =>
    d.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.customer?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const filteredLogs = logs.filter(l =>
    l.message.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className={`dashboard ${theme}`}>
      {toast && <Toast message={toast.message} type={toast.type} />}

      <header className="header">
        <div className="logo">
          <span className="logo-icon">🤖</span>
          <h1>LeBrickBot</h1>
        </div>
        <nav className="nav">
          <a 
            href="#deployments" 
            className={currentView === 'deployments' ? 'active' : ''}
            onClick={(e) => { e.preventDefault(); setCurrentView('deployments'); }}
          >
            Deployments
          </a>
          <a 
            href="#customers" 
            className={currentView === 'customers' ? 'active' : ''}
            onClick={(e) => { e.preventDefault(); setCurrentView('customers'); }}
          >
            Customers
          </a>
          <a 
            href="#integrations" 
            className={currentView === 'integrations' ? 'active' : ''}
            onClick={(e) => { e.preventDefault(); setCurrentView('integrations'); }}
          >
            Integrations
          </a>
          <a 
            href="#monitoring" 
            className={currentView === 'monitoring' ? 'active' : ''}
            onClick={(e) => { e.preventDefault(); setCurrentView('monitoring'); }}
          >
            Monitoring
          </a>
          <a 
            href="#settings"
            className={currentView === 'settings' ? 'active' : ''}
            onClick={(e) => { e.preventDefault(); setCurrentView('settings'); }}
          >
            Settings
          </a>
        </nav>
        <button className="theme-toggle" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>
      </header>

      {currentView === 'settings' ? (
        <SettingsPage />
      ) : currentView === 'integrations' ? (
        <IntegrationsDashboard />
      ) : currentView === 'customers' ? (
        <div className="customers-view">
          <div className="customers-header">
            <h2>👥 Customer Apps</h2>
            <p>Manage deployments for all your customers</p>
          </div>
          
          <div className="customers-grid">
            {customers.map(customer => (
              <div key={customer.id} className={`customer-card customer-${customer.status}`}>
                <div className="customer-header">
                  <h3>{customer.name}</h3>
                  <span className={`status-badge status-${customer.status}`}>
                    {customer.status}
                  </span>
                </div>
                
                <div className="customer-info">
                  <div className="info-row">
                    <span className="label">App:</span>
                    <span className="value">{customer.app}</span>
                  </div>
                  <div className="info-row">
                    <span className="label">Stack:</span>
                    <span className="value">{customer.stack}</span>
                  </div>
                  <div className="info-row">
                    <span className="label">Replicas:</span>
                    <span className="value">{customer.replicas}</span>
                  </div>
                  <div className="info-row">
                    <span className="label">Namespace:</span>
                    <span className="value">{customer.namespace}</span>
                  </div>
                </div>
                
                <div className="customer-endpoints">
                  <strong>Endpoints:</strong>
                  <div className="endpoints-list">
                    {customer.endpoints.map(ep => (
                      <span key={ep} className="endpoint-tag">{ep}</span>
                    ))}
                  </div>
                </div>
                
                <div className="customer-actions">
                  <a href={customer.url} target="_blank" rel="noopener noreferrer" className="btn-secondary">
                    🌐 Open App
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : currentView === 'monitoring' ? (
        <div className="monitoring-view">
          <div className="monitoring-header">
            <h2>📊 Monitoring Dashboard</h2>
            <p>Real-time metrics and observability</p>
          </div>
          <div className="monitoring-grid">
            <CostWidget />
            <AlertsPanel />
          </div>
        </div>
      ) : (
        <>
          <section className="hero">
            <h2>Freelance DevOps Engineer Dashboard</h2>
            <p>Manage multiple customer deployments with AI-powered automation</p>
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

          <section className="stats">
            {isInitialLoad ? (
              <>
                <div className="stat-card skeleton"></div>
                <div className="stat-card skeleton"></div>
                <div className="stat-card skeleton"></div>
                <div className="stat-card skeleton"></div>
              </>
            ) : (
              <>
                <div className="stat-card">
                  <div className="stat-value">{stats.deploymentsToday}</div>
                  <div className="stat-label">Customers</div>
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
              </>
            )}
          </section>

          <div className="content">
            <section className="section deployments-section">
              <div className="section-header">
                <h3>Active Deployments</h3>
                <input 
                  type="text"
                  placeholder="🔍 Search deployments..."
                  className="search-input"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              
              {filteredDeployments.length === 0 ? (
                <div className="empty-state">
                  <span className="empty-icon">📦</span>
                  <h4>No deployments found</h4>
                  <p>{searchQuery ? 'Try a different search' : 'Deploy your first service to get started'}</p>
                </div>
              ) : (
                <>
                  <div className="deployments-list">
                    {filteredDeployments.map(dep => (
                      <div key={dep.id} className="deployment-card">
                        <div className="deployment-header">
                          <div>
                            <span className="deployment-name">{dep.name}</span>
                            {dep.customer && <span className="deployment-customer">({dep.customer})</span>}
                          </div>
                          <span className={`deployment-status status-${dep.status}`}>{dep.status}</span>
                        </div>
                        <div className="deployment-meta">
                          <span className="deployment-time">⏱ {dep.time}</span>
                          <span className="deployment-replicas">📦 {dep.replicas} replica{dep.replicas > 1 ? 's' : ''}</span>
                          <span className="deployment-cost">💰 {dep.cost}</span>
                        </div>
                        <div className="deployment-actions">
                          <button className="action-btn action-scale" onClick={() => handleAction(dep, 'scale')} title="Scale Up">⬆️</button>
                          <button className="action-btn action-restart" onClick={() => handleAction(dep, 'restart')} title="Restart">🔄</button>
                          <button className="action-btn action-logs" onClick={() => handleAction(dep, 'logs')} title="View Logs">📋</button>
                          <button className="action-btn action-delete" onClick={() => handleAction(dep, 'delete')} title="Delete">🗑️</button>
                        </div>
                      </div>
                    ))}
                  </div>
                  <button className="btn-primary" onClick={() => setShowDeployModal(true)}>
                    🚀 Deploy New Service
                  </button>
                </>
              )}
            </section>

            <section className="section logs-section">
              <h3>Activity Logs</h3>
              <div className="logs-list">
                {filteredLogs.map((log, idx) => (
                  <div key={idx} className={`log-entry log-${log.level}`}>
                    <span className="log-time">{log.time}</span>
                    <span className="log-level">[{log.level.toUpperCase()}]</span>
                    <span className="log-message">{log.message}</span>
                  </div>
                ))}
              </div>
            </section>
          </div>
        </>
      )}

      <footer className="footer">
        <p>LeBrickBot v0.1.0 - Freelance DevOps Engineer Platform</p>
        <p>Managing {customers.length} customers • {stats.activeServices} active services</p>
      </footer>

      {showDeployModal && (
        <DeployModal 
          onClose={() => setShowDeployModal(false)}
          onDeploy={handleDeploy}
          loading={loading}
        />
      )}

      {showActionModal && selectedDeployment && (
        <ActionModal
          deployment={selectedDeployment}
          action={selectedAction}
          onClose={() => setShowActionModal(false)}
          onConfirm={executeAction}
          loading={loading}
        />
      )}
    </div>
  )
}

export default App
