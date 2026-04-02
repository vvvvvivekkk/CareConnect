// API Base URL - use relative path for unified deployment
const API_URL = '/api';

// Get token from localStorage
function getToken() {
    return localStorage.getItem('token');
}

// Get user from localStorage
function getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

// Save auth data
function saveAuth(token, user) {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
}

// Clear auth data
function clearAuth() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
}

// Check if user is authenticated
function isAuthenticated() {
    return !!getToken();
}

// Redirect to login if not authenticated
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

// Logout
function logout() {
    clearAuth();
    window.location.href = '/login';
}

// API Call Helper
async function apiCall(endpoint, options = {}) {
    const token = getToken();
    
    const config = {
        ...options,
        headers: {
            ...options.headers,
        }
    };
    
    // Add auth header if token exists
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Add content type for JSON if body is present and not FormData
    if (options.body && !(options.body instanceof FormData)) {
        config.headers['Content-Type'] = 'application/json';
    }
    
    try {
        const response = await fetch(`${API_URL}${endpoint}`, config);
        
        // Handle 401 - redirect to login
        if (response.status === 401) {
            clearAuth();
            window.location.href = '/login';
            throw new Error('Unauthorized');
        }
        
        // Parse response
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Something went wrong');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Show Alert
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    // Insert at top of container
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// Format Date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Format Time
function formatTime(timeString) {
    const [hours, minutes] = timeString.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
}

// Show Loading Spinner
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="spinner"></div>';
    }
}

// Hide Loading Spinner
function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '';
    }
}

// Initialize Navigation
function initNavigation() {
    const user = getUser();
    if (user) {
        const userInfo = document.getElementById('user-info');
        if (userInfo) {
            userInfo.innerHTML = `
                <span>Welcome, ${user.name}</span>
                <button onclick="logout()" class="btn-logout">Logout</button>
            `;
        }
    }
}

// Export functions for use in other files
window.API_URL = API_URL;
window.getToken = getToken;
window.getUser = getUser;
window.saveAuth = saveAuth;
window.clearAuth = clearAuth;
window.isAuthenticated = isAuthenticated;
window.requireAuth = requireAuth;
window.logout = logout;
window.apiCall = apiCall;
window.showAlert = showAlert;
window.formatDate = formatDate;
window.formatTime = formatTime;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.initNavigation = initNavigation;
