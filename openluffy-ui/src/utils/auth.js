/**
 * Authentication utilities for OpenLuffy
 */

/**
 * Check if user is authenticated
 * @returns {boolean} True if user has valid auth token
 */
export function isAuthenticated() {
  const token = localStorage.getItem('authToken')
  if (!token) return false

  try {
    // Decode JWT to check expiration (without verification - just checking if expired)
    const payload = JSON.parse(atob(token.split('.')[1]))
    const exp = payload.exp * 1000 // Convert to milliseconds
    
    // Check if token is expired
    if (Date.now() >= exp) {
      // Token expired, clear it
      logout()
      return false
    }
    
    return true
  } catch (err) {
    // Invalid token format
    logout()
    return false
  }
}

/**
 * Get current user from localStorage
 * @returns {object|null} User object or null
 */
export function getCurrentUser() {
  try {
    const userJson = localStorage.getItem('user')
    return userJson ? JSON.parse(userJson) : null
  } catch (err) {
    return null
  }
}

/**
 * Get auth token
 * @returns {string|null} Auth token or null
 */
export function getAuthToken() {
  return localStorage.getItem('authToken')
}

/**
 * Get refresh token
 * @returns {string|null} Refresh token or null
 */
export function getRefreshToken() {
  return localStorage.getItem('refreshToken')
}

/**
 * Logout user - clear all auth data
 */
export function logout() {
  localStorage.removeItem('authToken')
  localStorage.removeItem('refreshToken')
  localStorage.removeItem('user')
}

/**
 * Store auth tokens and user data
 * @param {string} accessToken - JWT access token
 * @param {string} refreshToken - JWT refresh token
 * @param {object} user - User object
 */
export function setAuthData(accessToken, refreshToken, user) {
  localStorage.setItem('authToken', accessToken)
  localStorage.setItem('refreshToken', refreshToken)
  localStorage.setItem('user', JSON.stringify(user))
}
