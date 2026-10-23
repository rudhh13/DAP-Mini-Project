// Settings functionality for Smart Reminder System

// Constants
const SETTINGS_STORAGE_KEY = 'smart_reminder_system_settings';

// DOM Elements
const settingsContainer = document.createElement('div');
settingsContainer.id = 'settings-container';
settingsContainer.className = 'settings-container';
settingsContainer.style.display = 'none'; // Hide by default

// Default settings
const defaultSettings = {
    theme: 'system',
    notificationSound: 'default',
    defaultReminderTime: '09:00',
    defaultCategory: 'personal',
    defaultPriority: 'medium',
    showCompletedReminders: true,
    autoArchiveCompleted: false,
    reminderAdvanceNotice: 15, // minutes
    dateFormat: 'MM/DD/YYYY',
    timeFormat: '12h',
    colorAccent: '#4361ee' // Fixed accent color - no longer user configurable
};

// Available themes
const availableThemes = [
    { id: 'dark', name: 'Dark', icon: 'fa-moon' },
    { id: 'system', name: 'System Default', icon: 'fa-desktop' },
    { id: 'blue', name: 'Blue', icon: 'fa-palette', color: '#1a73e8' },
    { id: 'green', name: 'Green', icon: 'fa-palette', color: '#0f9d58' },
    { id: 'purple', name: 'Purple', icon: 'fa-palette', color: '#7e57c2' }
];

// Current settings
let settings = { ...defaultSettings };

// Initialize settings
function initSettings() {
    const main = document.querySelector('main');
    
    // Add theme color meta tag
    const metaThemeColor = document.createElement('meta');
    metaThemeColor.name = 'theme-color';
    metaThemeColor.content = settings.colorAccent;
    document.head.appendChild(metaThemeColor);
    
    settingsContainer.innerHTML = `
        <div class="settings-header">
            <h2>Settings</h2>
            <button id="reset-settings" class="btn-secondary">Reset to Defaults</button>
        </div>
        
        <div class="settings-content">
            <form id="settings-form">
                <div class="settings-section">
                    <h3>Theme</h3>
                    <p class="setting-note">Your system theme preference is automatically applied. Use the theme toggle in the header to temporarily switch between light and dark mode.</p>
                </div>
                
                <div class="settings-section">
                    <h3>Notifications</h3>
                    
                    <div class="form-group">
                        <label for="notification-sound">Notification Sound</label>
                        <select id="notification-sound">
                            <option value="default">Default</option>
                            <option value="bell">Bell</option>
                            <option value="chime">Chime</option>
                            <option value="silent">Silent</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="reminder-advance-notice">Reminder Advance Notice (minutes)</label>
                        <input type="number" id="reminder-advance-notice" min="0" max="60">
                    </div>
                </div>
                
                <div class="settings-section">
                    <h3>Default Values</h3>
                    
                    <div class="form-group">
                        <label for="default-reminder-time">Default Reminder Time</label>
                        <input type="time" id="default-reminder-time">
                    </div>
                    
                    <div class="form-group">
                        <label for="default-category">Default Category</label>
                        <select id="default-category">
                            <option value="work">Work</option>
                            <option value="personal">Personal</option>
                            <option value="health">Health</option>
                            <option value="finance">Finance</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="default-priority">Default Priority</label>
                        <select id="default-priority">
                            <option value="low">Low</option>
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                        </select>
                    </div>
                </div>
                
                <div class="settings-section">
                    <h3>Display Options</h3>
                    
                    <div class="form-group checkbox-group">
                        <input type="checkbox" id="show-completed-reminders">
                        <label for="show-completed-reminders">Show Completed Reminders</label>
                    </div>
                    
                    <div class="form-group checkbox-group">
                        <input type="checkbox" id="auto-archive-completed">
                        <label for="auto-archive-completed">Auto-Archive Completed Items (after 7 days)</label>
                    </div>
                    
                    <div class="form-group">
                        <label for="date-format">Date Format</label>
                        <select id="date-format">
                            <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                            <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                            <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="time-format">Time Format</label>
                        <select id="time-format">
                            <option value="12h">12-hour (AM/PM)</option>
                            <option value="24h">24-hour</option>
                        </select>
                    </div>
                </div>
                
                <div class="settings-section">
                    <h3>Data Management</h3>
                    
                    <div class="form-group button-group">
                        <button type="button" id="export-data" class="btn-secondary">Export Data</button>
                        <button type="button" id="import-data" class="btn-secondary">Import Data</button>
                    </div>
                    
                    <div class="form-group button-group">
                        <button type="button" id="clear-reminders" class="btn-danger">Clear All Reminders</button>
                        <button type="button" id="clear-tasks" class="btn-danger">Clear All Tasks</button>
                    </div>
                </div>
                
                <div class="settings-actions">
                    <button type="submit" class="btn-primary">Save Settings</button>
                </div>
            </form>
        </div>
    `;
    
    main.appendChild(settingsContainer);
    
    // Load settings
    loadSettings();
    
    // Setup event listeners
    setupSettingsEventListeners();
    
    // Initial render
    populateSettingsForm();
    
    // Apply theme based on system preference if set to system
    detectAndApplySystemTheme();
}

// Load settings from localStorage
function loadSettings() {
    const storedSettings = localStorage.getItem(SETTINGS_STORAGE_KEY);
    if (storedSettings) {
        settings = { ...defaultSettings, ...JSON.parse(storedSettings) };
    }
}

// Save settings to localStorage
function saveSettings() {
    localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(settings));
    applySettings();
}

// Detect system theme preference
function detectAndApplySystemTheme() {
    // Force theme to system
    settings.theme = 'system';
    
    // Use matchMedia to detect system preference
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Apply appropriate theme based on system preference
    const themeToApply = prefersDarkScheme.matches ? 'dark' : 'blue';
    applyTheme(themeToApply);
    
    // Listen for changes in system theme
    prefersDarkScheme.addEventListener('change', (e) => {
        const newTheme = e.matches ? 'dark' : 'blue';
        applyTheme(newTheme);
    });
}

// Apply theme
function applyTheme(themeName) {
    // Remove all theme classes
    document.body.classList.remove('theme-light', 'theme-dark', 'theme-blue', 'theme-green', 'theme-purple');
    
    // Add the selected theme class
    document.body.classList.add(`theme-${themeName}`);
    
    // Update CSS variables for the accent color
    document.documentElement.style.setProperty('--primary-color', settings.colorAccent);
    document.documentElement.style.setProperty('--primary-light', adjustColor(settings.colorAccent, 20));
    document.documentElement.style.setProperty('--secondary-color', adjustColor(settings.colorAccent, -20));
    
    // Update theme color meta tag
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
        metaThemeColor.content = settings.colorAccent;
    }
    
    // Update theme toggle icon
    if (typeof updateThemeToggleIcon === 'function') {
        updateThemeToggleIcon();
    }
}

// Helper function to lighten or darken a color
function adjustColor(color, percent) {
    let R = parseInt(color.substring(1, 3), 16);
    let G = parseInt(color.substring(3, 5), 16);
    let B = parseInt(color.substring(5, 7), 16);

    R = parseInt(R * (100 + percent) / 100);
    G = parseInt(G * (100 + percent) / 100);
    B = parseInt(B * (100 + percent) / 100);

    R = (R < 255) ? R : 255;
    G = (G < 255) ? G : 255;
    B = (B < 255) ? B : 255;

    R = Math.max(0, R).toString(16).padStart(2, '0');
    G = Math.max(0, G).toString(16).padStart(2, '0');
    B = Math.max(0, B).toString(16).padStart(2, '0');

    return `#${R}${G}${B}`;
}

// Apply settings to the UI
function applySettings() {
    // Apply theme
    detectAndApplySystemTheme();
    
    // Update meta theme color
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
        metaThemeColor.content = settings.colorAccent;
    }
    
    // Other settings will be applied when needed in various parts of the app
}

// Populate settings form with current values
function populateSettingsForm() {
    // Theme and accent color are no longer user-configurable options
    
    // Notification settings
    document.getElementById('notification-sound').value = settings.notificationSound;
    document.getElementById('reminder-advance-notice').value = settings.reminderAdvanceNotice;
    
    // Default values
    document.getElementById('default-reminder-time').value = settings.defaultReminderTime;
    document.getElementById('default-category').value = settings.defaultCategory;
    document.getElementById('default-priority').value = settings.defaultPriority;
    
    // Display options
    document.getElementById('show-completed-reminders').checked = settings.showCompletedReminders;
    document.getElementById('auto-archive-completed').checked = settings.autoArchiveCompleted;
    document.getElementById('date-format').value = settings.dateFormat;
    document.getElementById('time-format').value = settings.timeFormat;
}

// Update theme preview based on current settings
function updateThemePreview() {
    const previewLight = document.querySelector('.preview-light');
    const previewDark = document.querySelector('.preview-dark');
    
    if (previewLight && previewDark) {
        // Update header color
        previewLight.querySelector('.preview-header').style.backgroundColor = settings.colorAccent;
        previewDark.querySelector('.preview-header').style.backgroundColor = settings.colorAccent;
        
        // Update sidebar selected item
        previewLight.querySelector('.preview-sidebar').innerHTML = 
            `<div class="preview-nav-item"></div>
             <div class="preview-nav-item" style="background-color: ${adjustColor(settings.colorAccent, 20)}"></div>
             <div class="preview-nav-item"></div>`;
        
        previewDark.querySelector('.preview-sidebar').innerHTML = 
            `<div class="preview-nav-item"></div>
             <div class="preview-nav-item" style="background-color: ${adjustColor(settings.colorAccent, 20)}"></div>
             <div class="preview-nav-item"></div>`;
        
        // Update main content with more detailed preview elements
        previewLight.querySelector('.preview-main').innerHTML = 
            `<div class="preview-card">
                <div class="preview-priority" style="background-color: ${settings.colorAccent}"></div>
                <div style="width: 100%">
                    <div style="height: 12px; width: 60%; background-color: #e9ecef; border-radius: 4px; margin-bottom: 8px;"></div>
                    <div style="height: 8px; width: 40%; background-color: #e9ecef; border-radius: 4px;"></div>
                </div>
             </div>`;
        
        previewDark.querySelector('.preview-main').innerHTML = 
            `<div class="preview-card">
                <div class="preview-priority" style="background-color: ${settings.colorAccent}"></div>
                <div style="width: 100%">
                    <div style="height: 12px; width: 60%; background-color: #495057; border-radius: 4px; margin-bottom: 8px;"></div>
                    <div style="height: 8px; width: 40%; background-color: #495057; border-radius: 4px;"></div>
                </div>
             </div>`;
             
        // Update the active theme indicators
        document.querySelectorAll('.preview-item').forEach(item => item.classList.remove('active-preview'));
        if (settings.theme === 'dark' || settings.theme === 'system') {
            previewDark.classList.add('active-preview');
        } else {
            previewLight.classList.add('active-preview');
        }
    }
}

// Setup event listeners for settings
function setupSettingsEventListeners() {
    const settingsForm = document.getElementById('settings-form');
    const resetSettingsBtn = document.getElementById('reset-settings');
    const exportDataBtn = document.getElementById('export-data');
    const importDataBtn = document.getElementById('import-data');
    const clearRemindersBtn = document.getElementById('clear-reminders');
    const clearTasksBtn = document.getElementById('clear-tasks');
    
    // Form submission
    settingsForm.addEventListener('submit', handleSettingsFormSubmit);
    
    // Reset settings
    resetSettingsBtn.addEventListener('click', resetSettings);
    
    // Data management
    exportDataBtn.addEventListener('click', exportData);
    importDataBtn.addEventListener('click', importData);
    clearRemindersBtn.addEventListener('click', clearReminders);
    clearTasksBtn.addEventListener('click', clearTasks);
}

// Handle settings form submission
function handleSettingsFormSubmit(e) {
    e.preventDefault();
    
    // Update settings object with form values
    // Note: theme and colorAccent are no longer included as they're fixed
    settings.notificationSound = document.getElementById('notification-sound').value;
    settings.reminderAdvanceNotice = parseInt(document.getElementById('reminder-advance-notice').value);
    settings.defaultReminderTime = document.getElementById('default-reminder-time').value;
    settings.defaultCategory = document.getElementById('default-category').value;
    settings.defaultPriority = document.getElementById('default-priority').value;
    settings.showCompletedReminders = document.getElementById('show-completed-reminders').checked;
    settings.autoArchiveCompleted = document.getElementById('auto-archive-completed').checked;
    settings.dateFormat = document.getElementById('date-format').value;
    settings.timeFormat = document.getElementById('time-format').value;
    
    // Always enforce system theme
    settings.theme = 'system';
    
    // Save settings
    saveSettings();
    
    // Show notification
    showNotification('Settings saved successfully!');
}

// Reset settings to defaults
function resetSettings() {
    if (confirm('Are you sure you want to reset all settings to default values?')) {
        settings = { ...defaultSettings };
        saveSettings();
        populateSettingsForm();
        showNotification('Settings reset to defaults!');
    }
}

// Export data as JSON
function exportData() {
    const exportData = {
        reminders: reminders,
        tasks: tasks,
        settings: settings
    };
    
    const dataStr = JSON.stringify(exportData);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
    
    const exportFileName = `smart_reminder_system_export_${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileName);
    linkElement.click();
    
    showNotification('Data exported successfully!');
}

// Import data from JSON
function importData() {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.json';
    
    fileInput.addEventListener('change', e => {
        const file = e.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.readAsText(file);
        
        reader.onload = e => {
            try {
                const importedData = JSON.parse(e.target.result);
                
                if (importedData.reminders) reminders = importedData.reminders;
                if (importedData.tasks) tasks = importedData.tasks;
                if (importedData.settings) settings = { ...defaultSettings, ...importedData.settings };
                
                // Save everything
                saveReminders();
                saveTasks();
                saveSettings();
                
                // Update UI
                renderReminders();
                renderTasks();
                populateSettingsForm();
                
                showNotification('Data imported successfully!');
            } catch (error) {
                showNotification('Error importing data: Invalid file format');
                console.error('Import error:', error);
            }
        };
    });
    
    fileInput.click();
}

// Clear all reminders
function clearReminders() {
    if (confirm('Are you sure you want to delete ALL reminders? This cannot be undone!')) {
        reminders = [];
        saveReminders();
        renderReminders();
        showNotification('All reminders have been deleted!');
    }
}

// Clear all tasks
function clearTasks() {
    if (confirm('Are you sure you want to delete ALL tasks? This cannot be undone!')) {
        tasks = [];
        saveTasks();
        renderTasks();
        showNotification('All tasks have been deleted!');
    }
}

// Quick theme switcher (toggle between dark and blue based on current theme)
function toggleTheme() {
    // Toggle between dark and blue themes
    if (document.body.classList.contains('theme-dark')) {
        applyTheme('blue');
    } else {
        applyTheme('dark');
    }
    
    // We don't save this preference as we're still using system theme
    // Theme will revert to system preference on page refresh
}

// Show settings view
function showSettingsView() {
    // Hide other views
    document.querySelector('.create-reminder').style.display = 'none';
    document.querySelector('.reminders-container').style.display = 'none';
    document.getElementsByClassName('calendar-container')[0].style.display = 'none';
    document.getElementById('tasks-container').style.display = 'none';
    
    // Show settings
    settingsContainer.style.display = 'block';
} 