/**
 * Theme Toggle Functionality for Mess Management System
 * Handles dark mode switching and persistence
 */

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', function () {
    initializeTheme();
    attachToggleListeners();
});

/**
 * Initialize theme based on user preference or system preference
 */
function initializeTheme() {
    // Try to get saved theme from localStorage first
    let savedTheme = localStorage.getItem('theme');

    // If no saved theme, get from user profile data attribute on body
    if (!savedTheme) {
        const userDarkMode = document.body.dataset.userDarkMode;
        savedTheme = (userDarkMode === 'true') ? 'dark' : 'light';
    }

    // Apply the theme
    applyTheme(savedTheme);
}

/**
 * Apply theme to the page
 * @param {string} theme - 'light' or 'dark'
 */
function applyTheme(theme) {
    if (theme === 'dark') {
        document.body.setAttribute('data-theme', 'dark');
        updateToggleIcon('dark');
    } else {
        document.body.setAttribute('data-theme', 'light');
        updateToggleIcon('light');
    }

    // Save to localStorage
    localStorage.setItem('theme', theme);
}

/**
 * Toggle between light and dark themes
 */
function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    applyTheme(newTheme);

    // Save to backend if user is authenticated
    saveThemePreference(newTheme);
}

/**
 * Update the toggle icon based on active theme
 * @param {string} theme - 'light' or 'dark'
 */
function updateToggleIcon(theme) {
    const iconElement = document.getElementById('theme-icon');
    if (!iconElement) return;

    if (theme === 'dark') {
        iconElement.textContent = '🌙'; // Moon icon for dark mode
    } else {
        iconElement.textContent = '☀️'; // Sun icon for light mode
    }
}

/**
 * Attach event listeners to theme toggle buttons
 */
function attachToggleListeners() {
    const toggleButtons = document.querySelectorAll('.theme-toggle');

    toggleButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            toggleTheme();
        });
    });
}

/**
 * Save theme preference to backend via AJAX
 * @param {string} theme - 'light' or 'dark'
 */
function saveThemePreference(theme) {
    // Get CSRF token
    const csrftoken = getCookie('csrftoken');

    // Send AJAX request to save preference
    fetch('/user/save-theme-preference/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            dark_mode: theme === 'dark'
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Theme preference saved successfully');
            }
        })
        .catch(error => {
            console.error('Error saving theme preference:', error);
        });
}

/**
 * Get CSRF token from cookies
 * @param {string} name - Cookie name
 * @returns {string} Cookie value
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Keyboard shortcut for theme toggle (Ctrl/Cmd + Shift + D)
 */
document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
        e.preventDefault();
        toggleTheme();
    }
});
