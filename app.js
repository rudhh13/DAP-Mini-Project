// Constants for localStorage
const REMINDERS_STORAGE_KEY = 'smart_reminder_system_reminders';

// DOM Elements
const reminderForm = document.getElementById('reminder-form');
const remindersList = document.getElementById('reminders-list');
const filterPriority = document.getElementById('filter-priority');
const filterCategory = document.getElementById('filter-category');
const notification = document.getElementById('notification');
const notificationMessage = document.getElementById('notification-message');
const notificationClose = document.getElementById('notification-close');

// Store for reminders
let reminders = [];

// Initialize the application
function init() {
    loadReminders();
    renderReminders();
    setupEventListeners();
    setupNavigation();
    checkUpcomingReminders();
    
    // Initialize calendar, tasks and settings
    initCalendar();
    initTasks();
    initSettings();
    
    // Apply settings
    loadSettings();
    applySettings();
}

// Load reminders from localStorage
function loadReminders() {
    const storedReminders = localStorage.getItem(REMINDERS_STORAGE_KEY);
    reminders = storedReminders ? JSON.parse(storedReminders) : [];
}

// Save reminders to localStorage
function saveReminders() {
    localStorage.setItem(REMINDERS_STORAGE_KEY, JSON.stringify(reminders));
}

// Setup all event listeners
function setupEventListeners() {
    // Form submission
    reminderForm.addEventListener('submit', handleFormSubmit);
    
    // Filter changes
    filterPriority.addEventListener('change', renderReminders);
    filterCategory.addEventListener('change', renderReminders);
    
    // Notification close
    notificationClose.addEventListener('click', hideNotification);
}

// Set up navigation
function setupNavigation() {
    const navItems = document.querySelectorAll('.sidebar ul li');
    
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove active class from all items
            navItems.forEach(nav => nav.classList.remove('active'));
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Show corresponding view
            const text = this.textContent.trim();
            
            if (text.includes('Dashboard')) {
                showDashboardView();
            } else if (text.includes('Calendar')) {
                showCalendarView();
            } else if (text.includes('Tasks')) {
                showTasksView();
            } else if (text.includes('Settings')) {
                showSettingsView();
            }
        });
    });
}

// Handle form submission
function handleFormSubmit(e) {
    e.preventDefault();
    
    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;
    const date = document.getElementById('date').value;
    const time = document.getElementById('time').value;
    const priority = document.getElementById('priority').value;
    const category = document.getElementById('category').value;
    
    // Create reminder object
    const newReminder = {
        id: Date.now().toString(),
        title,
        description,
        datetime: `${date}T${time}`,
        priority,
        category,
        completed: false,
        createdAt: new Date().toISOString()
    };
    
    // Add to reminders array
    reminders.push(newReminder);
    saveReminders();
    
    // Reset form
    reminderForm.reset();
    
    // Show notification
    showNotification(`Reminder "${title}" added successfully!`);
    
    // Re-render reminders list
    renderReminders();
    
    // Schedule notification for this reminder
    scheduleReminderNotification(newReminder);
}

// Render reminders to the DOM
function renderReminders() {
    // Get filter values
    const priorityFilter = filterPriority.value;
    const categoryFilter = filterCategory.value;
    
    // Filter reminders
    let filteredReminders = reminders.filter(reminder => {
        const priorityMatch = priorityFilter === 'all' || reminder.priority === priorityFilter;
        const categoryMatch = categoryFilter === 'all' || reminder.category === categoryFilter;
        
        // Filter by completed status based on settings
        if (!settings.showCompletedReminders && reminder.completed) {
            return false;
        }
        
        return priorityMatch && categoryMatch;
    });
    
    // Sort reminders by date (closest first)
    filteredReminders.sort((a, b) => new Date(a.datetime) - new Date(b.datetime));
    
    // Clear the list
    remindersList.innerHTML = '';
    
    // Check if there are any reminders
    if (filteredReminders.length === 0) {
        remindersList.innerHTML = '<li class="no-reminders">No reminders found. Create a new one!</li>';
        return;
    }
    
    // Create HTML for each reminder
    filteredReminders.forEach(reminder => {
        const reminderEl = document.createElement('li');
        reminderEl.className = `reminder-item priority-${reminder.priority}`;
        if (reminder.completed) {
            reminderEl.classList.add('completed');
        }
        
        // Format date and time for display
        const reminderDate = new Date(reminder.datetime);
        
        // Format based on settings
        let formattedDate;
        if (settings.dateFormat === 'MM/DD/YYYY') {
            formattedDate = reminderDate.toLocaleDateString('en-US', {
                weekday: 'short',
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } else if (settings.dateFormat === 'DD/MM/YYYY') {
            formattedDate = reminderDate.toLocaleDateString('en-GB', {
                weekday: 'short',
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } else {
            formattedDate = reminderDate.toISOString().split('T')[0];
        }
        
        let formattedTime;
        if (settings.timeFormat === '12h') {
            formattedTime = reminderDate.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit'
            });
        } else {
            formattedTime = reminderDate.toLocaleTimeString('en-GB', {
                hour: '2-digit',
                minute: '2-digit'
            });
        }
        
        reminderEl.innerHTML = `
            <div class="reminder-details">
                <h3>${reminder.title}</h3>
                <p>${reminder.description || 'No description'}</p>
                <div class="reminder-meta">
                    <span><i class="fas fa-calendar"></i> ${formattedDate}</span>
                    <span><i class="fas fa-clock"></i> ${formattedTime}</span>
                    <span><i class="fas fa-tag"></i> ${reminder.category}</span>
                </div>
            </div>
            <div class="reminder-actions">
                <button class="action-btn complete" data-id="${reminder.id}" title="Mark as ${reminder.completed ? 'incomplete' : 'complete'}">
                    <i class="fas fa-${reminder.completed ? 'undo' : 'check'}"></i>
                </button>
                <button class="action-btn edit" data-id="${reminder.id}" title="Edit">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="action-btn delete" data-id="${reminder.id}" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        // Add event listeners to the buttons
        remindersList.appendChild(reminderEl);
        
        // Complete button
        reminderEl.querySelector('.complete').addEventListener('click', () => toggleReminderComplete(reminder.id));
        
        // Edit button
        reminderEl.querySelector('.edit').addEventListener('click', () => editReminder(reminder.id));
        
        // Delete button
        reminderEl.querySelector('.delete').addEventListener('click', () => deleteReminder(reminder.id));
    });
}

// Toggle reminder completion status
function toggleReminderComplete(id) {
    const reminderIndex = reminders.findIndex(r => r.id === id);
    if (reminderIndex !== -1) {
        reminders[reminderIndex].completed = !reminders[reminderIndex].completed;
        saveReminders();
        renderReminders();
        
        const status = reminders[reminderIndex].completed ? 'completed' : 'marked as incomplete';
        showNotification(`Reminder ${status}!`);
    }
}

// Delete a reminder
function deleteReminder(id) {
    const reminderIndex = reminders.findIndex(r => r.id === id);
    if (reminderIndex !== -1) {
        const reminderTitle = reminders[reminderIndex].title;
        reminders.splice(reminderIndex, 1);
        saveReminders();
        renderReminders();
        showNotification(`Reminder "${reminderTitle}" deleted!`);
    }
}

// Edit a reminder
function editReminder(id) {
    const reminder = reminders.find(r => r.id === id);
    if (!reminder) return;
    
    // Fill the form with reminder data
    document.getElementById('title').value = reminder.title;
    document.getElementById('description').value = reminder.description || '';
    
    // Extract date and time from datetime
    const reminderDate = new Date(reminder.datetime);
    const dateString = reminderDate.toISOString().split('T')[0];
    const timeString = reminderDate.toTimeString().slice(0, 5);
    
    document.getElementById('date').value = dateString;
    document.getElementById('time').value = timeString;
    document.getElementById('priority').value = reminder.priority;
    document.getElementById('category').value = reminder.category;
    
    // Delete the old reminder
    deleteReminder(id);
    
    // Show dashboard view to edit
    showDashboardView();
    
    // Scroll to the form
    document.querySelector('.create-reminder').scrollIntoView({ behavior: 'smooth' });
    
    showNotification('Edit your reminder and submit to save changes');
}

// Show notification
function showNotification(message) {
    notificationMessage.textContent = message;
    notification.classList.add('show');
    
    // Auto-hide after 5 seconds
    setTimeout(hideNotification, 5000);
}

// Hide notification
function hideNotification() {
    notification.classList.remove('show');
}

// Check for upcoming reminders
function checkUpcomingReminders() {
    const now = new Date();
    const upcoming = reminders.filter(reminder => {
        if (reminder.completed) return false;
        
        const reminderTime = new Date(reminder.datetime);
        const timeDiff = reminderTime - now;
        
        // Check if reminder is due within the advance notice time
        const advanceNoticeMs = settings.reminderAdvanceNotice * 60 * 1000;
        return timeDiff > 0 && timeDiff <= advanceNoticeMs;
    });
    
    if (upcoming.length > 0) {
        upcoming.forEach(reminder => {
            showNotification(`Upcoming reminder: "${reminder.title}" in less than ${settings.reminderAdvanceNotice} minutes!`);
        });
    }
    
    // Check every minute
    setTimeout(checkUpcomingReminders, 60 * 1000);
}

// Schedule a browser notification for a reminder
function scheduleReminderNotification(reminder) {
    if (!("Notification" in window)) {
        return; // Browser doesn't support notifications
    }
    
    const reminderTime = new Date(reminder.datetime).getTime();
    const now = new Date().getTime();
    const timeUntilReminder = reminderTime - now;
    
    if (timeUntilReminder <= 0) return; // Reminder is in the past
    
    // Ask for permission if needed
    if (Notification.permission !== "granted" && Notification.permission !== "denied") {
        Notification.requestPermission();
    }
    
    // Schedule the notification
    setTimeout(() => {
        if (Notification.permission === "granted") {
            const notification = new Notification("Smart Reminder System", {
                body: `Reminder: ${reminder.title}`,
                icon: "https://cdn.iconscout.com/icon/free/png-256/free-reminder-1805234-1529640.png"
            });
            
            // Play sound if enabled
            if (settings.notificationSound !== 'silent') {
                playNotificationSound(settings.notificationSound);
            }
            
            // Close the notification after 10 seconds
            setTimeout(notification.close.bind(notification), 10000);
        }
    }, timeUntilReminder);
}

// Play notification sound
function playNotificationSound(sound) {
    let soundUrl;
    
    switch(sound) {
        case 'bell':
            soundUrl = 'https://assets.mixkit.co/sfx/preview/mixkit-bell-notification-933.mp3';
            break;
        case 'chime':
            soundUrl = 'https://assets.mixkit.co/sfx/preview/mixkit-software-interface-start-2574.mp3';
            break;
        default:
            soundUrl = 'https://assets.mixkit.co/sfx/preview/mixkit-positive-interface-beep-221.mp3';
    }
    
    const audio = new Audio(soundUrl);
    audio.play();
}

// Add sample reminders if none exist
function addSampleRemindersIfEmpty() {
    if (reminders.length === 0) {
        // Get tomorrow's date
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        tomorrow.setHours(10, 0, 0, 0);
        
        // Get today's date but 2 hours ahead
        const today = new Date();
        today.setHours(today.getHours() + 2, 0, 0, 0);
        
        // Sample reminders
        const sampleReminders = [
            {
                id: '1',
                title: 'Team Meeting',
                description: 'Weekly team status update meeting',
                datetime: tomorrow.toISOString(),
                priority: 'high',
                category: 'work',
                completed: false,
                createdAt: new Date().toISOString()
            },
            {
                id: '2',
                title: 'Gym Session',
                description: 'Upper body workout day',
                datetime: today.toISOString(),
                priority: 'medium',
                category: 'health',
                completed: false,
                createdAt: new Date().toISOString()
            }
        ];
        
        reminders = sampleReminders;
        saveReminders();
    }
}

// Show dashboard view (default view)
function showDashboardView() {
    // Show reminder form and list
    document.querySelector('.create-reminder').style.display = 'block';
    document.querySelector('.reminders-container').style.display = 'block';
    
    // Hide other views
    document.getElementsByClassName('calendar-container')[0].style.display = 'none';
    document.getElementById('tasks-container').style.display = 'none';
    document.getElementById('settings-container').style.display = 'none';
    
    // Re-render reminders
    renderReminders();
}

// Auto-archive completed reminders
function autoArchiveCompletedReminders() {
    if (!settings.autoArchiveCompleted) return;
    
    const now = new Date();
    const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    
    reminders = reminders.filter(reminder => {
        if (reminder.completed) {
            const completedDate = new Date(reminder.completedAt || reminder.datetime);
            return completedDate > sevenDaysAgo;
        }
        return true;
    });
    
    saveReminders();
}

// Initialize with sample data
addSampleRemindersIfEmpty();

// Initialize the app when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', init); 