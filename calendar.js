// Calendar functionality for Smart Reminder System

// DOM Elements
const calendarContainer = document.createElement('div');
calendarContainer.className = 'calendar-container';
calendarContainer.style.display = 'none'; // Hide by default

// Current displayed date
let currentDate = new Date();
let selectedDate = new Date();

// Initialize calendar
function initCalendar() {
    const main = document.querySelector('main');
    
    calendarContainer.innerHTML = `
        <div class="calendar-header">
            <div class="calendar-nav">
                <button id="prev-month"><i class="fas fa-chevron-left"></i></button>
                <h2 id="calendar-title"></h2>
                <button id="next-month"><i class="fas fa-chevron-right"></i></button>
            </div>
            <button id="today-btn" class="btn-secondary">Today</button>
        </div>
        <div class="weekdays">
            <div>Sun</div>
            <div>Mon</div>
            <div>Tue</div>
            <div>Wed</div>
            <div>Thu</div>
            <div>Fri</div>
            <div>Sat</div>
        </div>
        <div id="calendar-days" class="calendar-days"></div>
        <div id="day-reminders" class="day-reminders">
            <h3>Reminders for <span id="selected-date"></span></h3>
            <ul id="date-reminders-list"></ul>
        </div>
    `;
    
    main.appendChild(calendarContainer);
    
    // Setup event listeners
    document.getElementById('prev-month').addEventListener('click', () => changeMonth(-1));
    document.getElementById('next-month').addEventListener('click', () => changeMonth(1));
    document.getElementById('today-btn').addEventListener('click', goToToday);
    
    // Initial render
    renderCalendar();
}

// Render the calendar for current month
function renderCalendar() {
    const calendarDays = document.getElementById('calendar-days');
    const calendarTitle = document.getElementById('calendar-title');
    
    // Set the calendar title
    calendarTitle.textContent = `${currentDate.toLocaleString('default', { month: 'long' })} ${currentDate.getFullYear()}`;
    
    // Clear previous days
    calendarDays.innerHTML = '';
    
    // Get first day of month and last day of month
    const firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    const lastDay = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
    
    // Get the day of the week the first day falls on (0-6)
    const firstDayIndex = firstDay.getDay();
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < firstDayIndex; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.className = 'calendar-day empty';
        calendarDays.appendChild(emptyDay);
    }
    
    // Add days of the month
    for (let i = 1; i <= lastDay.getDate(); i++) {
        const dayElement = document.createElement('div');
        dayElement.className = 'calendar-day';
        dayElement.textContent = i;
        
        // Check if this day has reminders
        const checkDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), i);
        const hasReminders = checkDateForReminders(checkDate);
        
        if (hasReminders) {
            const reminderDot = document.createElement('span');
            reminderDot.className = 'reminder-dot';
            dayElement.appendChild(reminderDot);
        }
        
        // Highlight today
        const today = new Date();
        if (i === today.getDate() && 
            currentDate.getMonth() === today.getMonth() && 
            currentDate.getFullYear() === today.getFullYear()) {
            dayElement.classList.add('today');
        }
        
        // Highlight selected date
        if (i === selectedDate.getDate() && 
            currentDate.getMonth() === selectedDate.getMonth() && 
            currentDate.getFullYear() === selectedDate.getFullYear()) {
            dayElement.classList.add('selected');
        }
        
        // Add click event to view reminders for this day
        dayElement.addEventListener('click', () => {
            // Update selected date
            selectedDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), i);
            
            // Remove selected class from all days
            document.querySelectorAll('.calendar-day').forEach(day => {
                day.classList.remove('selected');
            });
            
            // Add selected class to clicked day
            dayElement.classList.add('selected');
            
            // Show reminders for this day
            showRemindersForDate(selectedDate);
        });
        
        calendarDays.appendChild(dayElement);
    }
    
    // Show reminders for selected date
    showRemindersForDate(selectedDate);
}

// Change month (delta: -1 for previous, 1 for next)
function changeMonth(delta) {
    currentDate.setMonth(currentDate.getMonth() + delta);
    renderCalendar();
}

// Go to today
function goToToday() {
    currentDate = new Date();
    selectedDate = new Date();
    renderCalendar();
}

// Check if a date has any reminders
function checkDateForReminders(date) {
    const dateString = date.toISOString().split('T')[0];
    
    return reminders.some(reminder => {
        const reminderDate = new Date(reminder.datetime);
        return reminderDate.toISOString().split('T')[0] === dateString;
    });
}

// Show reminders for a specific date
function showRemindersForDate(date) {
    const dateRemindersList = document.getElementById('date-reminders-list');
    const selectedDateSpan = document.getElementById('selected-date');
    
    // Format selected date for display
    selectedDateSpan.textContent = date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    
    // Clear previous reminders
    dateRemindersList.innerHTML = '';
    
    // Get reminders for this date
    const dateString = date.toISOString().split('T')[0];
    const dateReminders = reminders.filter(reminder => {
        const reminderDate = new Date(reminder.datetime);
        return reminderDate.toISOString().split('T')[0] === dateString;
    });
    
    // Sort by time
    dateReminders.sort((a, b) => new Date(a.datetime) - new Date(b.datetime));
    
    // Display reminders
    if (dateReminders.length === 0) {
        dateRemindersList.innerHTML = '<li class="no-reminders">No reminders for this date</li>';
    } else {
        dateReminders.forEach(reminder => {
            const reminderItem = document.createElement('li');
            reminderItem.className = `reminder-item priority-${reminder.priority}`;
            if (reminder.completed) {
                reminderItem.classList.add('completed');
            }
            
            // Format time
            const reminderTime = new Date(reminder.datetime).toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit'
            });
            
            reminderItem.innerHTML = `
                <div class="reminder-details">
                    <h4>${reminder.title}</h4>
                    <div class="reminder-meta">
                        <span><i class="fas fa-clock"></i> ${reminderTime}</span>
                        <span><i class="fas fa-tag"></i> ${reminder.category}</span>
                    </div>
                </div>
                <div class="reminder-actions">
                    <button class="action-btn view" data-id="${reminder.id}" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn edit" data-id="${reminder.id}" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                </div>
            `;
            
            dateRemindersList.appendChild(reminderItem);
            
            // Add event listeners
            reminderItem.querySelector('.view').addEventListener('click', () => viewReminderDetails(reminder.id));
            reminderItem.querySelector('.edit').addEventListener('click', () => editReminder(reminder.id));
        });
    }
}

// View reminder details
function viewReminderDetails(id) {
    const reminder = reminders.find(r => r.id === id);
    if (!reminder) return;
    
    showNotification(`"${reminder.title}" - ${reminder.description || 'No description provided'}`);
}

// Show calendar view
function showCalendarView() {
    // Hide other views
    document.querySelector('.create-reminder').style.display = 'none';
    document.querySelector('.reminders-container').style.display = 'none';
    document.getElementById('tasks-container').style.display = 'none';
    document.getElementById('settings-container').style.display = 'none';
    
    // Show calendar
    calendarContainer.style.display = 'block';
    
    // Update calendar
    renderCalendar();
} 