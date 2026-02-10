import { useState, useEffect } from 'react'
import { useCustomer } from '../contexts/CustomerContext'
import './TopNavbar.css'

function TopNavbar({ onCreateNew }) {
  const { customers, selectedCustomer, selectCustomer } = useCustomer()
  const [systemStatus, setSystemStatus] = useState({ healthy: true, loading: true })
  const [notifications, setNotifications] = useState([])
  const [showNotifications, setShowNotifications] = useState(false)

  useEffect(() => {
    // Check system health
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => {
        setSystemStatus({ healthy: data.status === 'healthy', loading: false })
      })
      .catch(() => {
        setSystemStatus({ healthy: false, loading: false })
      })

    // Fetch notifications (pending approvals count)
    fetch('http://localhost:8000/pending-approvals')
      .then(res => res.json())
      .then(data => {
        if (data.approvals && data.approvals.length > 0) {
          setNotifications(data.approvals)
        }
      })
      .catch(err => console.error('Failed to fetch notifications:', err))
  }, [])

  const notificationCount = notifications.length

  return (
    <nav className="top-navbar">
      <div className="navbar-section navbar-left">
        <div className="navbar-brand">
          <span className="brand-icon">🏴‍☠️</span>
          <div className="brand-text">
            <span className="brand-name">Luffy</span>
            <span className="brand-subtitle">Straw Hat DevOps</span>
          </div>
        </div>
        
        {/* CUSTOMER TABS - SINGLE SOURCE OF TRUTH */}
        <div className="customer-tabs">
          <button
            className={`customer-tab ${!selectedCustomer ? 'active' : ''}`}
            onClick={() => selectCustomer(null)}
          >
            <span className="tab-icon">🏠</span>
            <span className="tab-label">All Customers</span>
          </button>
          {customers.map(customer => (
            <button
              key={customer.id}
              className={`customer-tab ${selectedCustomer === customer.id ? 'active' : ''}`}
              onClick={() => selectCustomer(customer.id)}
            >
              <span className="tab-icon">{customer.icon || '🏢'}</span>
              <span className="tab-label">{customer.name}</span>
              <span className="tab-stack">{customer.stack}</span>
            </button>
          ))}
          
          {/* CREATE NEW CUSTOMER BUTTON */}
          <button className="customer-tab create-tab" onClick={onCreateNew}>
            <span className="tab-icon">+</span>
            <span className="tab-label">Create Customer</span>
          </button>
        </div>
      </div>

      <div className="navbar-section navbar-right">
        {/* System Status */}
        <div className={`status-indicator ${systemStatus.healthy ? 'healthy' : 'unhealthy'}`}>
          <span className="status-dot"></span>
          <span className="status-text">
            {systemStatus.loading ? 'Checking...' : systemStatus.healthy ? 'All Systems Operational' : 'System Issues Detected'}
          </span>
        </div>

        {/* Notifications */}
        <div className="navbar-notifications">
          <button 
            className="notification-btn"
            onClick={() => setShowNotifications(!showNotifications)}
            title="Notifications"
          >
            🔔
            {notificationCount > 0 && (
              <span className="notification-badge">{notificationCount}</span>
            )}
          </button>
          
          {showNotifications && (
            <div className="notification-dropdown">
              <div className="notification-header">
                <h3>Notifications</h3>
                {notificationCount > 0 && (
                  <span className="notification-count">{notificationCount} pending</span>
                )}
              </div>
              <div className="notification-list">
                {notificationCount === 0 ? (
                  <div className="notification-empty">
                    <span>✅</span>
                    <p>All caught up!</p>
                  </div>
                ) : (
                  notifications.map((approval, idx) => (
                    <div key={idx} className="notification-item">
                      <div className="notification-icon">🚀</div>
                      <div className="notification-content">
                        <p className="notification-title">
                          Production Approval Required
                        </p>
                        <p className="notification-detail">
                          {approval.customer} - {approval.deployment}
                        </p>
                        <span className="notification-time">Waiting for approval</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="navbar-actions">
          <a 
            href="http://argocd.local" 
            target="_blank" 
            rel="noopener noreferrer"
            className="action-btn"
            title="ArgoCD"
          >
            <span>🐙</span>
          </a>
          <a 
            href="https://github.com/lebrick07/lebrickbot" 
            target="_blank" 
            rel="noopener noreferrer"
            className="action-btn"
            title="GitHub Repository"
          >
            <span>📦</span>
          </a>
        </div>

        {/* User Profile */}
        <div className="navbar-user">
          <div className="user-avatar">⚔️</div>
          <div className="user-info">
            <span className="user-name">Captain LeBrick</span>
            <span className="user-role">Straw Hat Crew</span>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default TopNavbar
