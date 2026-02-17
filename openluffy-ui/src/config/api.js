/**
 * API Configuration
 * 
 * Determines the correct backend API URL based on environment
 */

// Get API base URL from environment or use smart defaults
export const API_BASE_URL = (() => {
  // If explicitly set via environment variable (build time)
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  
  // Smart defaults based on hostname
  const hostname = window.location.hostname
  
  // Development (localhost)
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000'
  }
  
  // Production/Staging - use same hostname, port 8000
  // Works for dev.openluffy.local, preprod.openluffy.local, openluffy.local
  return `http://${hostname}:8000`
})()

console.log(`[API Config] Using backend URL: ${API_BASE_URL}`)
