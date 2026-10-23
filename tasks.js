// Tasks functionality for Smart Reminder System

// Constants
const TASKS_STORAGE_KEY = 'smart_reminder_system_tasks';

// DOM Elements
const tasksContainer = document.createElement('div');
tasksContainer.id = 'tasks-container';
tasksContainer.className = 'tasks-container';
tasksContainer.style.display = 'none'; // Hide by default

// Store for tasks
let tasks = [];

// Initialize tasks
function initTasks() {
    const main = document.querySelector('main');
    
    tasksContainer.innerHTML = `
        <div class="tasks-header">
            <h2>Task Management</h2>
        </div>
        
        <div class="tasks-content">
            <div class="task-form-container">
                <h3>Create New Task</h3>
                <form id="task-form">
                    <div class="form-group">
                        <label for="task-title">Task Title</label>
                        <input type="text" id="task-title" placeholder="Enter task title" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="task-description">Description</label>
                        <textarea id="task-description" placeholder="Enter task details"></textarea>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="task-due-date">Due Date</label>
                            <input type="date" id="task-due-date">
                        </div>
                        
                        <div class="form-group">
                            <label for="task-priority">Priority</label>
                            <select id="task-priority">
                                <option value="low">Low</option>
                                <option value="medium" selected>Medium</option>
                                <option value="high">High</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="task-related-reminder">Related Reminder</label>
                        <select id="task-related-reminder">
                            <option value="">None</option>
                            <!-- Will be populated dynamically -->
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Subtasks</label>
                        <div id="subtasks-container">
                            <!-- Subtasks will be added here -->
                        </div>
                        <button type="button" id="add-subtask" class="btn-secondary">Add Subtask</button>
                    </div>
                    
                    <button type="submit" class="btn-primary">Create Task</button>
                </form>
            </div>
            
            <div class="tasks-list-container">
                <div class="tasks-filter">
                    <select id="filter-task-status">
                        <option value="all">All Tasks</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                    </select>
                    
                    <select id="filter-task-priority">
                        <option value="all">All Priorities</option>
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                    </select>
                </div>
                
                <div id="tasks-list" class="tasks-list">
                    <!-- Tasks will be added here dynamically -->
                </div>
            </div>
        </div>
    `;
    
    main.appendChild(tasksContainer);
    
    // Load tasks
    loadTasks();
    
    // Setup event listeners
    setupTasksEventListeners();
    
    // Initial render
    renderTasks();
    populateRelatedReminderDropdown();
}

// Load tasks from localStorage
function loadTasks() {
    const storedTasks = localStorage.getItem(TASKS_STORAGE_KEY);
    tasks = storedTasks ? JSON.parse(storedTasks) : [];
}

// Save tasks to localStorage
function saveTasks() {
    localStorage.setItem(TASKS_STORAGE_KEY, JSON.stringify(tasks));
}

// Setup event listeners for tasks
function setupTasksEventListeners() {
    const taskForm = document.getElementById('task-form');
    const addSubtaskBtn = document.getElementById('add-subtask');
    const filterTaskStatus = document.getElementById('filter-task-status');
    const filterTaskPriority = document.getElementById('filter-task-priority');
    
    // Form submission
    taskForm.addEventListener('submit', handleTaskFormSubmit);
    
    // Add subtask button
    addSubtaskBtn.addEventListener('click', addSubtaskField);
    
    // Filter changes
    filterTaskStatus.addEventListener('change', renderTasks);
    filterTaskPriority.addEventListener('change', renderTasks);
}

// Add a subtask input field
function addSubtaskField() {
    const subtasksContainer = document.getElementById('subtasks-container');
    const subtaskIndex = subtasksContainer.children.length;
    
    const subtaskGroup = document.createElement('div');
    subtaskGroup.className = 'subtask-group';
    
    subtaskGroup.innerHTML = `
        <input type="text" class="subtask-input" placeholder="Enter subtask" name="subtask-${subtaskIndex}">
        <button type="button" class="remove-subtask"><i class="fas fa-times"></i></button>
    `;
    
    subtasksContainer.appendChild(subtaskGroup);
    
    // Add event listener to remove button
    subtaskGroup.querySelector('.remove-subtask').addEventListener('click', function() {
        subtasksContainer.removeChild(subtaskGroup);
    });
}

// Handle task form submission
function handleTaskFormSubmit(e) {
    e.preventDefault();
    
    const title = document.getElementById('task-title').value;
    const description = document.getElementById('task-description').value;
    const dueDate = document.getElementById('task-due-date').value;
    const priority = document.getElementById('task-priority').value;
    const relatedReminderId = document.getElementById('task-related-reminder').value;
    
    // Get subtasks
    const subtasksElements = document.querySelectorAll('.subtask-input');
    const subtasks = Array.from(subtasksElements).map(input => {
        return {
            text: input.value,
            completed: false
        };
    }).filter(subtask => subtask.text.trim() !== '');
    
    // Create task object
    const newTask = {
        id: Date.now().toString(),
        title,
        description,
        dueDate,
        priority,
        relatedReminderId,
        subtasks,
        completed: false,
        createdAt: new Date().toISOString()
    };
    
    // Add to tasks array
    tasks.push(newTask);
    saveTasks();
    
    // Reset form
    document.getElementById('task-form').reset();
    document.getElementById('subtasks-container').innerHTML = '';
    
    // Show notification
    showNotification(`Task "${title}" created successfully!`);
    
    // Re-render tasks list
    renderTasks();
}

// Populate related reminder dropdown
function populateRelatedReminderDropdown() {
    const relatedReminderSelect = document.getElementById('task-related-reminder');
    
    // Clear previous options except the first one
    while (relatedReminderSelect.options.length > 1) {
        relatedReminderSelect.remove(1);
    }
    
    // Add options for active reminders
    const activeReminders = reminders.filter(reminder => !reminder.completed);
    
    activeReminders.forEach(reminder => {
        const option = document.createElement('option');
        option.value = reminder.id;
        option.textContent = reminder.title;
        relatedReminderSelect.appendChild(option);
    });
}

// Render tasks to the DOM
function renderTasks() {
    const tasksList = document.getElementById('tasks-list');
    const statusFilter = document.getElementById('filter-task-status').value;
    const priorityFilter = document.getElementById('filter-task-priority').value;
    
    // Filter tasks
    let filteredTasks = tasks.filter(task => {
        const statusMatch = statusFilter === 'all' || 
                           (statusFilter === 'active' && !task.completed) || 
                           (statusFilter === 'completed' && task.completed);
        
        const priorityMatch = priorityFilter === 'all' || task.priority === priorityFilter;
        
        return statusMatch && priorityMatch;
    });
    
    // Sort tasks by due date (closest first)
    filteredTasks.sort((a, b) => {
        // If no due date, put at the end
        if (!a.dueDate) return 1;
        if (!b.dueDate) return -1;
        
        return new Date(a.dueDate) - new Date(b.dueDate);
    });
    
    // Clear the list
    tasksList.innerHTML = '';
    
    // Check if there are any tasks
    if (filteredTasks.length === 0) {
        tasksList.innerHTML = '<div class="no-tasks">No tasks found. Create a new task!</div>';
        return;
    }
    
    // Create HTML for each task
    filteredTasks.forEach(task => {
        const taskEl = document.createElement('div');
        taskEl.className = `task-item priority-${task.priority}`;
        if (task.completed) {
            taskEl.classList.add('completed');
        }
        
        // Format due date for display
        let dueDateDisplay = 'No due date';
        if (task.dueDate) {
            const dueDate = new Date(task.dueDate);
            dueDateDisplay = dueDate.toLocaleDateString('en-US', {
                weekday: 'short',
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        }
        
        // Build the related reminder text if any
        let relatedReminderText = '';
        if (task.relatedReminderId) {
            const relatedReminder = reminders.find(r => r.id === task.relatedReminderId);
            if (relatedReminder) {
                relatedReminderText = `
                    <div class="task-related-reminder">
                        <i class="fas fa-bell"></i> Related to: ${relatedReminder.title}
                    </div>
                `;
            }
        }
        
        // Build subtasks HTML
        let subtasksHtml = '';
        if (task.subtasks && task.subtasks.length > 0) {
            subtasksHtml = '<div class="task-subtasks">';
            task.subtasks.forEach((subtask, index) => {
                subtasksHtml += `
                    <div class="subtask-item">
                        <label class="subtask-checkbox">
                            <input type="checkbox" data-task-id="${task.id}" data-subtask-index="${index}" 
                                ${subtask.completed ? 'checked' : ''}>
                            <span class="subtask-text ${subtask.completed ? 'completed' : ''}">${subtask.text}</span>
                        </label>
                    </div>
                `;
            });
            subtasksHtml += '</div>';
        }
        
        taskEl.innerHTML = `
            <div class="task-header">
                <div class="task-title-status">
                    <label class="task-checkbox">
                        <input type="checkbox" class="task-complete-checkbox" data-id="${task.id}" 
                            ${task.completed ? 'checked' : ''}>
                        <h3>${task.title}</h3>
                    </label>
                </div>
                <div class="task-actions">
                    <button class="action-btn edit" data-id="${task.id}" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn delete" data-id="${task.id}" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <div class="task-content">
                <p class="task-description">${task.description || 'No description'}</p>
                ${subtasksHtml}
                <div class="task-meta">
                    ${relatedReminderText}
                    <span><i class="fas fa-calendar"></i> ${dueDateDisplay}</span>
                </div>
            </div>
        `;
        
        tasksList.appendChild(taskEl);
        
        // Add event listeners
        // Complete task
        taskEl.querySelector('.task-complete-checkbox').addEventListener('change', function() {
            toggleTaskComplete(task.id, this.checked);
        });
        
        // Edit task
        taskEl.querySelector('.edit').addEventListener('click', () => editTask(task.id));
        
        // Delete task
        taskEl.querySelector('.delete').addEventListener('click', () => deleteTask(task.id));
        
        // Subtask checkboxes
        const subtaskCheckboxes = taskEl.querySelectorAll('.subtask-item input[type="checkbox"]');
        subtaskCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const taskId = this.getAttribute('data-task-id');
                const subtaskIndex = parseInt(this.getAttribute('data-subtask-index'));
                toggleSubtaskComplete(taskId, subtaskIndex, this.checked);
            });
        });
    });
}

// Toggle task completion status
function toggleTaskComplete(id, isCompleted) {
    const taskIndex = tasks.findIndex(t => t.id === id);
    if (taskIndex !== -1) {
        tasks[taskIndex].completed = isCompleted;
        saveTasks();
        renderTasks();
        
        const status = isCompleted ? 'completed' : 'marked as active';
        showNotification(`Task ${status}!`);
    }
}

// Toggle subtask completion
function toggleSubtaskComplete(taskId, subtaskIndex, isCompleted) {
    const taskIndex = tasks.findIndex(t => t.id === taskId);
    if (taskIndex !== -1 && tasks[taskIndex].subtasks && subtaskIndex < tasks[taskIndex].subtasks.length) {
        tasks[taskIndex].subtasks[subtaskIndex].completed = isCompleted;
        saveTasks();
        renderTasks();
    }
}

// Delete a task
function deleteTask(id) {
    const taskIndex = tasks.findIndex(t => t.id === id);
    if (taskIndex !== -1) {
        const taskTitle = tasks[taskIndex].title;
        tasks.splice(taskIndex, 1);
        saveTasks();
        renderTasks();
        showNotification(`Task "${taskTitle}" deleted!`);
    }
}

// Edit a task
function editTask(id) {
    const task = tasks.find(t => t.id === id);
    if (!task) return;
    
    // Show editing form (could implement a modal or replace with form)
    showNotification('Editing task functionality to be implemented');
    
    // For now, just log the task
    console.log('Edit task:', task);
}

// Show tasks view
function showTasksView() {
    // Hide other views
    document.querySelector('.create-reminder').style.display = 'none';
    document.querySelector('.reminders-container').style.display = 'none';
    document.getElementsByClassName('calendar-container')[0].style.display = 'none';
    document.getElementById('settings-container').style.display = 'none';
    
    // Show tasks
    tasksContainer.style.display = 'block';
    
    // Update related reminders dropdown
    populateRelatedReminderDropdown();
} 