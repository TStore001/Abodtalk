// Configuration
const API_BASE_URL = 'https://Abodtalk.pythonanywhere.com/api';';
let isConnected = false;
let refreshInterval = null;

// DOM Elements
const elements = {
    statusIndicator: document.getElementById('statusIndicator'),
    toggleBot: document.getElementById('toggleBot'),
    currentBalance: document.getElementById('currentBalance'),
    totalTrades: document.getElementById('totalTrades'),
    winRate: document.getElementById('winRate'),
    totalProfit: document.getElementById('totalProfit'),
    tradeHistoryBody: document.getElementById('tradeHistoryBody'),
    notificationsContainer: document.getElementById('notificationsContainer'),
    analysisContainer: document.getElementById('analysisContainer'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    toastContainer: document.getElementById('toastContainer'),
    refreshHistory: document.getElementById('refreshHistory'),
    refreshNotifications: document.getElementById('refreshNotifications'),
    markAllRead: document.getElementById('markAllRead'),
    analyzeMarket: document.getElementById('analyzeMarket')
};

// Utility Functions
function showLoading() {
    elements.loadingOverlay.classList.add('show');
}

function hideLoading() {
    elements.loadingOverlay.classList.remove('show');
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas ${getToastIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    elements.toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 5000);
}

function getToastIcon(type) {
    switch (type) {
        case 'success': return 'fa-check-circle';
        case 'error': return 'fa-exclamation-circle';
        case 'warning': return 'fa-exclamation-triangle';
        default: return 'fa-info-circle';
    }
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    }).format(amount);
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('ar-EG', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'الآن';
    if (diffInSeconds < 3600) return `منذ ${Math.floor(diffInSeconds / 60)} دقيقة`;
    if (diffInSeconds < 86400) return `منذ ${Math.floor(diffInSeconds / 3600)} ساعة`;
    return `منذ ${Math.floor(diffInSeconds / 86400)} يوم`;
}

// API Functions
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'حدث خطأ في الطلب');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

async function getStatus() {
    return await apiRequest('/trading/status');
}

async function startBot() {
    return await apiRequest('/trading/start', { method: 'POST' });
}

async function stopBot() {
    return await apiRequest('/trading/stop', { method: 'POST' });
}

async function getTradeHistory() {
    return await apiRequest('/trading/trade_history');
}

async function getNotifications() {
    return await apiRequest('/trading/notifications');
}

async function getStatistics() {
    return await apiRequest('/trading/statistics');
}

async function analyzeMarket() {
    return await apiRequest('/trading/analyze');
}

async function markNotificationRead(notificationId) {
    return await apiRequest(`/trading/notifications/${notificationId}/read`, { method: 'POST' });
}

// UI Update Functions
function updateStatus(status) {
    isConnected = status.status === 'running';
    
    if (isConnected) {
        elements.statusIndicator.classList.add('connected');
        elements.statusIndicator.querySelector('.status-text').textContent = 'متصل ويعمل';
        elements.toggleBot.innerHTML = '<i class="fas fa-stop"></i> إيقاف البوت';
        elements.toggleBot.classList.remove('btn-primary');
        elements.toggleBot.classList.add('btn-secondary');
    } else {
        elements.statusIndicator.classList.remove('connected');
        elements.statusIndicator.querySelector('.status-text').textContent = 'غير متصل';
        elements.toggleBot.innerHTML = '<i class="fas fa-play"></i> تشغيل البوت';
        elements.toggleBot.classList.remove('btn-secondary');
        elements.toggleBot.classList.add('btn-primary');
    }
}

function updateStatistics(stats) {
    elements.currentBalance.textContent = formatCurrency(stats.current_balance || 0);
    elements.totalTrades.textContent = stats.total_trades || 0;
    elements.winRate.textContent = `${(stats.win_rate || 0).toFixed(1)}%`;
    elements.totalProfit.textContent = formatCurrency(stats.total_profit || 0);
    
    // Update profit color
    if (stats.total_profit > 0) {
        elements.totalProfit.style.color = '#22c55e';
    } else if (stats.total_profit < 0) {
        elements.totalProfit.style.color = '#ef4444';
    } else {
        elements.totalProfit.style.color = '#1f2937';
    }
}

function updateTradeHistory(trades) {
    if (!trades || trades.length === 0) {
        elements.tradeHistoryBody.innerHTML = `
            <div class="no-data">
                <i class="fas fa-chart-line"></i>
                <p>لا توجد صفقات بعد</p>
            </div>
        `;
        return;
    }
    
    const tradesHtml = trades.map(trade => `
        <div class="trade-row">
            <div class="trade-cell">${formatDateTime(trade.timestamp)}</div>
            <div class="trade-cell">${trade.pair}</div>
            <div class="trade-cell">
                <span class="trade-direction ${trade.direction.toLowerCase()}">
                    ${trade.direction === 'CALL' ? 'شراء' : 'بيع'}
                </span>
            </div>
            <div class="trade-cell">${formatCurrency(trade.amount)}</div>
            <div class="trade-cell">
                <span class="trade-result ${trade.result.toLowerCase()}">
                    ${trade.result === 'WIN' ? 'ربح' : 'خسارة'}
                </span>
            </div>
            <div class="trade-cell">
                <span class="${trade.profit >= 0 ? 'profit-positive' : 'profit-negative'}">
                    ${formatCurrency(trade.profit)}
                </span>
            </div>
        </div>
    `).join('');
    
    elements.tradeHistoryBody.innerHTML = tradesHtml;
}

function updateNotifications(notifications) {
    if (!notifications || notifications.length === 0) {
        elements.notificationsContainer.innerHTML = `
            <div class="no-data">
                <i class="fas fa-bell-slash"></i>
                <p>لا توجد إشعارات</p>
            </div>
        `;
        return;
    }
    
    const notificationsHtml = notifications.map(notification => `
        <div class="notification-item ${notification.read ? '' : 'unread'}" 
             onclick="markAsRead(${notification.id})">
            <div class="notification-header">
                <span class="notification-type ${notification.type}">
                    ${getNotificationTypeText(notification.type)}
                </span>
                <span class="notification-time">${formatTimeAgo(notification.timestamp)}</span>
            </div>
            <div class="notification-message">${notification.message}</div>
        </div>
    `).join('');
    
    elements.notificationsContainer.innerHTML = notificationsHtml;
}

function getNotificationTypeText(type) {
    switch (type) {
        case 'high_confidence_signal': return 'إشارة قوية';
        case 'trade_executed': return 'تم التنفيذ';
        case 'info': return 'معلومات';
        default: return 'إشعار';
    }
}

function updateAnalysis(analysis) {
    if (!analysis || !analysis.analysis) {
        elements.analysisContainer.innerHTML = `
            <div class="no-data">
                <i class="fas fa-chart-area"></i>
                <p>اضغط على "تحليل الآن" لبدء تحليل السوق</p>
            </div>
        `;
        return;
    }
    
    const analysisHtml = Object.entries(analysis.analysis).map(([pair, data]) => {
        if (data.error) {
            return `
                <div class="analysis-card">
                    <h3><i class="fas fa-exclamation-triangle"></i> ${pair}</h3>
                    <p style="color: #ef4444;">${data.error}</p>
                </div>
            `;
        }
        
        const strategies = data.strategies || {};
        const consensus = data.consensus || {};
        
        return `
            <div class="analysis-card">
                <h3><i class="fas fa-chart-line"></i> ${pair}</h3>
                <div style="margin-bottom: 15px;">
                    <strong>السعر الحالي:</strong> ${data.current_price?.toFixed(5) || 'غير متاح'}
                </div>
                
                <div style="margin-bottom: 15px;">
                    <strong>الإجماع:</strong>
                    <span class="strategy-signal ${consensus.signal?.toLowerCase() || 'hold'}">
                        ${getSignalText(consensus.signal)} 
                        (${(consensus.confidence || 0).toFixed(1)}%)
                    </span>
                </div>
                
                <div class="analysis-strategies">
                    ${Object.entries(strategies).map(([strategyName, strategyData]) => `
                        <div class="strategy-item">
                            <span>${getStrategyName(strategyName)}</span>
                            <span class="strategy-signal ${strategyData.signal?.toLowerCase() || 'hold'}">
                                ${getSignalText(strategyData.signal)}
                            </span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }).join('');
    
    elements.analysisContainer.innerHTML = analysisHtml;
}

function getSignalText(signal) {
    switch (signal) {
        case 'CALL': return 'شراء';
        case 'PUT': return 'بيع';
        case 'HOLD': return 'انتظار';
        default: return 'غير محدد';
    }
}

function getStrategyName(strategyName) {
    const names = {
        'trend_following': 'تتبع الاتجاه',
        'range_trading': 'تداول النطاق',
        'breakout': 'الاختراق',
        'swing_trading': 'التداول المتأرجح',
        'scalping': 'المضاربة السريعة'
    };
    return names[strategyName] || strategyName;
}

// Event Handlers
async function toggleBotStatus() {
    try {
        showLoading();
        
        if (isConnected) {
            await stopBot();
            showToast('تم إيقاف البوت بنجاح', 'success');
            clearInterval(refreshInterval);
            refreshInterval = null;
        } else {
            await startBot();
            showToast('تم تشغيل البوت بنجاح', 'success');
            startAutoRefresh();
        }
        
        await refreshStatus();
    } catch (error) {
        showToast(`خطأ: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

async function refreshTradeHistory() {
    try {
        const response = await getTradeHistory();
        updateTradeHistory(response.data);
    } catch (error) {
        showToast(`خطأ في تحديث سجل التداول: ${error.message}`, 'error');
    }
}

async function refreshNotifications() {
    try {
        const response = await getNotifications();
        updateNotifications(response.data);
    } catch (error) {
        showToast(`خطأ في تحديث الإشعارات: ${error.message}`, 'error');
    }
}

async function refreshStatistics() {
    try {
        const response = await getStatistics();
        updateStatistics(response.data);
    } catch (error) {
        console.error('Error refreshing statistics:', error);
    }
}

async function refreshStatus() {
    try {
        const response = await getStatus();
        updateStatus(response);
    } catch (error) {
        console.error('Error refreshing status:', error);
    }
}

async function performMarketAnalysis() {
    try {
        showLoading();
        const response = await analyzeMarket();
        updateAnalysis(response.data);
        showToast('تم تحليل السوق بنجاح', 'success');
    } catch (error) {
        showToast(`خطأ في تحليل السوق: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

async function markAsRead(notificationId) {
    try {
        await markNotificationRead(notificationId);
        await refreshNotifications();
    } catch (error) {
        showToast(`خطأ في تمييز الإشعار: ${error.message}`, 'error');
    }
}

async function markAllNotificationsRead() {
    try {
        const response = await getNotifications();
        const unreadNotifications = response.data.filter(n => !n.read);
        
        for (const notification of unreadNotifications) {
            await markNotificationRead(notification.id);
        }
        
        await refreshNotifications();
        showToast('تم تمييز جميع الإشعارات كمقروءة', 'success');
    } catch (error) {
        showToast(`خطأ في تمييز الإشعارات: ${error.message}`, 'error');
    }
}

function startAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    
    refreshInterval = setInterval(async () => {
        if (isConnected) {
            await refreshStatus();
            await refreshStatistics();
            await refreshTradeHistory();
            await refreshNotifications();
        }
    }, 10000); // Refresh every 10 seconds
}

// Event Listeners
elements.toggleBot.addEventListener('click', toggleBotStatus);
elements.refreshHistory.addEventListener('click', refreshTradeHistory);
elements.refreshNotifications.addEventListener('click', refreshNotifications);
elements.markAllRead.addEventListener('click', markAllNotificationsRead);
elements.analyzeMarket.addEventListener('click', performMarketAnalysis);

// Initialize Application
async function initializeApp() {
    try {
        showLoading();
        
        // Load initial data
        await refreshStatus();
        await refreshStatistics();
        await refreshTradeHistory();
        await refreshNotifications();
        
        showToast('تم تحميل التطبيق بنجاح', 'success');
    } catch (error) {
        showToast(`خطأ في تحميل التطبيق: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// Add CSS animation for slideOut
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(-100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Start the application
document.addEventListener('DOMContentLoaded', initializeApp);
