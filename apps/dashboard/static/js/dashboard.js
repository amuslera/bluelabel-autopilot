/**
 * Agent Status Dashboard - JavaScript
 * Real-time dashboard for monitoring AI agent status and task progress
 */

class AgentDashboard {
    constructor() {
        this.apiBaseUrl = 'http://localhost:3000/api';
        this.refreshInterval = 30000; // 30 seconds
        this.refreshTimer = null;
        this.isConnected = false;
        this.agents = ['CA', 'CB', 'CC', 'WA', 'ARCH', 'BLUE'];
        this.agentInfo = {
            'CA': { name: 'Cursor AI Frontend', role: 'Frontend Development', color: '#3b82f6' },
            'CB': { name: 'Claude Code Backend', role: 'Backend Development', color: '#10b981' },
            'CC': { name: 'Claude Code Testing', role: 'Quality Assurance', color: '#f59e0b' },
            'WA': { name: 'Windsurf Infrastructure', role: 'Infrastructure', color: '#8b5cf6' },
            'ARCH': { name: 'Architecture Agent', role: 'System Architecture', color: '#ef4444' },
            'BLUE': { name: 'Blue Analysis', role: 'Data Analysis', color: '#06b6d4' }
        };
        
        this.init();
    }

    async init() {
        this.showLoading(true);
        this.setupEventListeners();
        await this.loadInitialData();
        this.startAutoRefresh();
        this.showLoading(false);
    }

    setupEventListeners() {
        // Refresh button
        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.refreshData();
        });

        // Expand all agents button
        document.getElementById('expand-all').addEventListener('click', () => {
            this.expandAllAgents();
        });

        // History filter
        document.getElementById('history-filter').addEventListener('change', (e) => {
            this.filterHistory(e.target.value);
        });

        // Export history button
        document.getElementById('export-history').addEventListener('click', () => {
            this.exportHistory();
        });

        // Modal controls
        document.getElementById('modal-close').addEventListener('click', () => {
            this.hideError();
        });

        document.getElementById('retry-connection').addEventListener('click', () => {
            this.hideError();
            this.refreshData();
        });

        // Auto-refresh on page visibility
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && !this.refreshTimer) {
                this.startAutoRefresh();
            } else if (document.hidden) {
                this.stopAutoRefresh();
            }
        });
    }

    async loadInitialData() {
        try {
            await Promise.all([
                this.loadSystemOverview(),
                this.loadAgentStatuses(),
                this.loadTaskHistory(),
                this.loadPerformanceMetrics()
            ]);
            this.updateConnectionStatus(true);
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.updateConnectionStatus(false);
            this.showError('Failed to load dashboard data', error.message);
        }
    }

    async refreshData() {
        try {
            await this.loadInitialData();
            this.updateLastRefresh();
        } catch (error) {
            console.error('Refresh failed:', error);
            this.updateConnectionStatus(false);
        }
    }

    async loadSystemOverview() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/system/overview`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            this.updateSystemOverview(data);
        } catch (error) {
            // Fallback to mock data for development
            const mockData = {
                total_tasks: 7,
                completed_tasks: 3,
                in_progress_tasks: 1,
                completion_rate: 43
            };
            this.updateSystemOverview(mockData);
        }
    }

    updateSystemOverview(data) {
        document.getElementById('total-tasks').textContent = data.total_tasks || 0;
        document.getElementById('completed-tasks').textContent = data.completed_tasks || 0;
        document.getElementById('progress-tasks').textContent = data.in_progress_tasks || 0;
        document.getElementById('efficiency-rate').textContent = `${data.completion_rate || 0}%`;

        // Update progress bar
        const progressBar = document.getElementById('main-progress-bar');
        const progressText = document.getElementById('progress-text');
        const percentage = data.completion_rate || 0;
        
        progressBar.style.width = `${percentage}%`;
        progressText.textContent = `${percentage}% Complete`;
    }

    async loadAgentStatuses() {
        const agentsGrid = document.getElementById('agents-grid');
        agentsGrid.innerHTML = '';

        for (const agentId of this.agents) {
            try {
                const response = await fetch(`${this.apiBaseUrl}/agents/${agentId}/status`);
                let agentData;
                
                if (response.ok) {
                    agentData = await response.json();
                } else {
                    // Fallback to mock data
                    agentData = this.getMockAgentData(agentId);
                }
                
                const agentCard = this.createAgentCard(agentId, agentData);
                agentsGrid.appendChild(agentCard);
            } catch (error) {
                console.error(`Failed to load ${agentId} status:`, error);
                const agentCard = this.createAgentCard(agentId, this.getMockAgentData(agentId));
                agentsGrid.appendChild(agentCard);
            }
        }
    }

    getMockAgentData(agentId) {
        const mockStatuses = ['working', 'ready', 'idle'];
        const status = mockStatuses[Math.floor(Math.random() * mockStatuses.length)];
        
        return {
            status: status,
            current_task: status === 'working' ? `TASK-165${agentId.charCodeAt(0)}` : null,
            pending_tasks: Math.floor(Math.random() * 3),
            completed_tasks: Math.floor(Math.random() * 10) + 1,
            success_rate: Math.floor(Math.random() * 20) + 80,
            avg_duration: (Math.random() * 3 + 1).toFixed(1)
        };
    }

    createAgentCard(agentId, data) {
        const agentInfo = this.agentInfo[agentId];
        const card = document.createElement('div');
        card.className = 'agent-card fade-in';
        
        const statusClass = this.getStatusClass(data.status);
        const statusIcon = this.getStatusIcon(data.status);
        
        card.innerHTML = `
            <div class="agent-header">
                <div class="agent-info">
                    <div class="agent-avatar" style="background: ${agentInfo.color}">
                        ${agentId}
                    </div>
                    <div class="agent-details">
                        <h4>${agentInfo.name}</h4>
                        <div class="agent-role">${agentInfo.role}</div>
                    </div>
                </div>
                <div class="agent-status ${statusClass}">
                    <i class="${statusIcon}"></i>
                    <span>${data.status.charAt(0).toUpperCase() + data.status.slice(1)}</span>
                </div>
            </div>
            
            ${data.current_task ? `
                <div class="current-task">
                    <strong>Current Task:</strong> ${data.current_task}
                </div>
            ` : ''}
            
            <div class="agent-stats">
                <div class="stat-item">
                    <div class="stat-value">${data.pending_tasks || 0}</div>
                    <div class="stat-label">Pending</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${data.completed_tasks || 0}</div>
                    <div class="stat-label">Completed</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${data.success_rate || 0}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${data.avg_duration || 0}h</div>
                    <div class="stat-label">Avg Duration</div>
                </div>
            </div>
        `;
        
        return card;
    }

    getStatusClass(status) {
        const statusMap = {
            'working': 'status-working',
            'ready': 'status-ready',
            'idle': 'status-idle',
            'error': 'status-error'
        };
        return statusMap[status] || 'status-idle';
    }

    getStatusIcon(status) {
        const iconMap = {
            'working': 'fas fa-cog fa-spin',
            'ready': 'fas fa-check-circle',
            'idle': 'fas fa-pause-circle',
            'error': 'fas fa-exclamation-triangle'
        };
        return iconMap[status] || 'fas fa-circle';
    }

    async loadTaskHistory() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/tasks/history`);
            let historyData;
            
            if (response.ok) {
                historyData = await response.json();
            } else {
                historyData = this.getMockHistoryData();
            }
            
            this.updateTaskHistory(historyData);
        } catch (error) {
            console.error('Failed to load task history:', error);
            this.updateTaskHistory(this.getMockHistoryData());
        }
    }

    getMockHistoryData() {
        const tasks = [
            { id: 'TASK-165D', title: 'Morning kickoff automation', agent: 'CA', status: 'completed', duration: '3.2h', timestamp: new Date(Date.now() - 3600000) },
            { id: 'TASK-165C', title: 'Task completion scripts', agent: 'CC', status: 'completed', duration: '2.1h', timestamp: new Date(Date.now() - 7200000) },
            { id: 'TASK-165B', title: 'Outbox format standardization', agent: 'CB', status: 'completed', duration: '0.5h', timestamp: new Date(Date.now() - 10800000) },
            { id: 'TASK-165E', title: 'Agent performance metrics', agent: 'CB', status: 'in_progress', duration: '1.5h', timestamp: new Date(Date.now() - 1800000) },
            { id: 'TASK-165F', title: 'Integration test suite', agent: 'CC', status: 'pending', duration: null, timestamp: new Date() }
        ];
        
        return { tasks: tasks };
    }

    updateTaskHistory(data) {
        const timeline = document.getElementById('history-timeline');
        timeline.innerHTML = '';
        
        if (!data.tasks || data.tasks.length === 0) {
            timeline.innerHTML = '<div class="no-data">No recent task activity</div>';
            return;
        }
        
        data.tasks.forEach(task => {
            const historyItem = this.createHistoryItem(task);
            timeline.appendChild(historyItem);
        });
    }

    createHistoryItem(task) {
        const item = document.createElement('div');
        item.className = 'history-item fade-in';
        item.dataset.agent = task.agent;
        
        const iconClass = task.status === 'completed' ? 'completed' : 'pending';
        const icon = task.status === 'completed' ? 'fas fa-check' : 'fas fa-clock';
        const timeAgo = this.getTimeAgo(task.timestamp);
        
        item.innerHTML = `
            <div class="history-icon ${iconClass}">
                <i class="${icon}"></i>
            </div>
            <div class="history-content">
                <div class="history-title">${task.title}</div>
                <div class="history-meta">
                    <span class="history-agent">${task.agent}</span>
                    <span class="history-task-id">${task.id}</span>
                    ${task.duration ? `<span class="history-duration">${task.duration}</span>` : ''}
                    <span class="history-time">${timeAgo}</span>
                </div>
            </div>
        `;
        
        return item;
    }

    getTimeAgo(timestamp) {
        const now = new Date();
        const diff = now - new Date(timestamp);
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 0) return `${days}d ago`;
        if (hours > 0) return `${hours}h ago`;
        if (minutes > 0) return `${minutes}m ago`;
        return 'Just now';
    }

    async loadPerformanceMetrics() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/metrics/performance`);
            let metricsData;
            
            if (response.ok) {
                metricsData = await response.json();
            } else {
                metricsData = this.getMockMetricsData();
            }
            
            this.updatePerformanceMetrics(metricsData);
        } catch (error) {
            console.error('Failed to load performance metrics:', error);
            this.updatePerformanceMetrics(this.getMockMetricsData());
        }
    }

    getMockMetricsData() {
        return {
            avg_duration: 2.4,
            success_rate: 92,
            tasks_week: 15,
            active_agents: 4
        };
    }

    updatePerformanceMetrics(data) {
        document.getElementById('avg-duration').textContent = `${data.avg_duration || 0} hours`;
        document.getElementById('success-rate').textContent = `${data.success_rate || 0}%`;
        document.getElementById('tasks-week').textContent = data.tasks_week || 0;
        document.getElementById('active-agents').textContent = data.active_agents || 0;
    }

    filterHistory(agentFilter) {
        const historyItems = document.querySelectorAll('.history-item');
        
        historyItems.forEach(item => {
            if (agentFilter === 'all' || item.dataset.agent === agentFilter) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    }

    exportHistory() {
        const historyItems = document.querySelectorAll('.history-item:not([style*="display: none"])');
        const data = [];
        
        historyItems.forEach(item => {
            const title = item.querySelector('.history-title').textContent;
            const meta = item.querySelector('.history-meta').textContent;
            data.push(`${title} - ${meta}`);
        });
        
        const csvContent = "data:text/csv;charset=utf-8," + 
            "Task,Details\n" + 
            data.map(row => `"${row.split(' - ')[0]}","${row.split(' - ')[1]}"`).join('\n');
        
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', `task_history_${new Date().toISOString().split('T')[0]}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    expandAllAgents() {
        const agentCards = document.querySelectorAll('.agent-card');
        const button = document.getElementById('expand-all');
        const isExpanded = button.textContent.includes('Collapse');
        
        agentCards.forEach(card => {
            if (isExpanded) {
                card.classList.remove('expanded');
            } else {
                card.classList.add('expanded');
            }
        });
        
        button.innerHTML = isExpanded ? 
            '<i class="fas fa-expand-arrows-alt"></i> Expand All' :
            '<i class="fas fa-compress-arrows-alt"></i> Collapse All';
    }

    updateConnectionStatus(connected) {
        this.isConnected = connected;
        const statusElement = document.getElementById('connection-status');
        const statusIcon = statusElement.querySelector('i');
        const statusText = statusElement.querySelector('span');
        
        statusElement.className = `connection-status ${connected ? 'connected' : 'disconnected'}`;
        statusIcon.className = 'fas fa-circle';
        statusText.textContent = connected ? 'Connected' : 'Disconnected';
    }

    updateLastRefresh() {
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        document.getElementById('last-updated').textContent = `Last updated: ${timeString}`;
    }

    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        overlay.classList.toggle('active', show);
    }

    showError(message, details = '') {
        const modal = document.getElementById('error-modal');
        const errorDetails = document.getElementById('error-details');
        
        errorDetails.textContent = details;
        modal.classList.add('active');
    }

    hideError() {
        const modal = document.getElementById('error-modal');
        modal.classList.remove('active');
    }

    startAutoRefresh() {
        this.stopAutoRefresh(); // Clear any existing timer
        this.refreshTimer = setInterval(() => {
            this.refreshData();
        }, this.refreshInterval);
    }

    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    // Public API for external control
    setRefreshInterval(interval) {
        this.refreshInterval = interval;
        if (this.refreshTimer) {
            this.startAutoRefresh();
        }
    }

    async forceRefresh() {
        await this.refreshData();
    }

    getConnectionStatus() {
        return this.isConnected;
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.agentDashboard = new AgentDashboard();
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AgentDashboard;
} 