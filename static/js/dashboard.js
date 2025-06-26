/**
 * Модуль управления главной страницей (Dashboard)
 */
class Dashboard {
  constructor() {
    this.statusUpdateInterval = null;
    this.recentActivitiesCount = 5;
    this.init();
  }

  init() {
    console.log('Инициализация Dashboard...');
    this.initEventHandlers();
    this.loadInitialData();
    this.startStatusUpdates();
  }

  initEventHandlers() {
    // Обновление статуса
    const refreshBtn = document.getElementById('refresh-status');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => this.updateSystemStatus());
    }

    // Quick Chat форма
    const quickForm = document.getElementById('quick-chat-form');
    if (quickForm) {
      quickForm.addEventListener('submit', (e) => this.handleQuickCommand(e));
    }

    // Автодополнение
    const quickInput = document.getElementById('quick-input');
    if (quickInput) {
      quickInput.addEventListener('input', (e) => this.handleInputSuggestions(e));
      quickInput.addEventListener('keydown', (e) => this.handleInputKeydown(e));
    }

    // Быстрые действия
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
      btn.addEventListener('click', (e) => this.handleQuickAction(e));
    });

    // Фильтр активностей
    const activitiesFilter = document.getElementById('activities-filter');
    if (activitiesFilter) {
      activitiesFilter.addEventListener('change', (e) => this.filterRecentActivities(e.target.value));
    }

    // Отмена выполнения
    const cancelBtn = document.getElementById('quick-cancel-btn');
    if (cancelBtn) {
      cancelBtn.addEventListener('click', () => this.cancelExecution());
    }
  }

  async loadInitialData() {
    try {
      // Загружаем статус системы
      await this.updateSystemStatus();

      // Загружаем недавние активности
      await this.loadRecentActivities();

      // Загружаем статус задач
      await this.updateTasksStatus();

    } catch (error) {
      console.error('Ошибка загрузки данных Dashboard:', error);
      this.showNotification('Ошибка загрузки данных', 'error');
    }
  }

  async updateSystemStatus() {
    try {
      const response = await fetch('/api/system/status');
      if (!response.ok) throw new Error(`HTTP ${ response.status }`);

      const data = await response.json();

      // Обновляем UI статуса
      this.updateModelStatus(data.model);
      this.updateSystemMetrics(data.system);
      this.updateLastActivity(data.lastActivity);

    } catch (error) {
      console.error('Ошибка обновления статуса:', error);
      this.setErrorStatus();
    }
  }

  updateModelStatus(modelData) {
    const nameEl = document.getElementById('current-model-name');
    const statusEl = document.getElementById('model-status');

    if (nameEl && modelData) {
      nameEl.textContent = modelData.name || 'Не выбрана';
    }

    if (statusEl && modelData) {
      const indicator = statusEl.querySelector('.status-indicator');
      const text = statusEl.querySelector('.status-text');

      if (indicator) {
        indicator.className = `status-indicator ${ modelData.status || 'error' }`;
      }

      if (text) {
        text.textContent = this.getStatusText(modelData.status);
      }
    }
  }

  updateSystemMetrics(systemData) {
    const cpuEl = document.getElementById('cpu-usage');
    const ramEl = document.getElementById('ram-usage');

    if (cpuEl && systemData?.cpu) {
      cpuEl.textContent = `${ systemData.cpu }%`;
    }

    if (ramEl && systemData?.ram) {
      ramEl.textContent = `${ systemData.ram }%`;
    }
  }

  updateLastActivity(activityData) {
    const timeEl = document.getElementById('last-task-time');
    const resultEl = document.getElementById('last-task-result');

    if (timeEl && activityData) {
      timeEl.textContent = this.formatTime(activityData.time) || '--';
    }

    if (resultEl && activityData) {
      resultEl.textContent = activityData.result || '--';
      resultEl.className = `task-result ${ activityData.status || '' }`;
    }
  }

  async updateTasksStatus() {
    try {
      const response = await fetch('/api/tasks/recent?count=1');
      if (!response.ok) throw new Error(`HTTP ${ response.status }`);

      const data = await response.json();

      const countEl = document.getElementById('active-tasks-count');
      const queueEl = document.getElementById('tasks-queue');

      if (countEl) {
        countEl.textContent = data.active || 0;
      }

      if (queueEl) {
        queueEl.textContent = `${ data.queued || 0 } в очереди`;
      }

    } catch (error) {
      console.error('Ошибка обновления статуса задач:', error);
    }
  }

  async loadRecentActivities() {
    const activitiesList = document.getElementById('activities-list');
    if (!activitiesList) return;

    try {
      const response = await fetch(`/api/tasks/recent?count=${ this.recentActivitiesCount }`);
      if (!response.ok) throw new Error(`HTTP ${ response.status }`);

      const data = await response.json();

      if (data.success && data.activities?.length > 0) {
        this.renderActivities(data.activities);
      } else {
        this.renderEmptyActivities();
      }

    } catch (error) {
      console.error('Ошибка загрузки активности:', error);
      this.renderErrorActivities();
    }
  }

  renderActivities(activities) {
    const activitiesList = document.getElementById('activities-list');
    if (!activitiesList) return;

    activitiesList.innerHTML = '';

    activities.forEach(activity => {
      const item = document.createElement('div');
      item.className = 'activity-item';

      item.innerHTML = `
            <div class="activity-icon ${ activity.status }">
                <i class="fas ${ this.getActivityIcon(activity.status) }"></i>
            </div>
            <div class="activity-content">
                <div class="activity-text">${ this.escapeHtml(activity.description) }</div>
                <div class="activity-time">${ this.formatTime(activity.time) }</div>
                ${ activity.result ? `<div class="activity-result ${ activity.status }">${ this.escapeHtml(activity.result) }</div>` : '' }
            </div>
        `;

      activitiesList.appendChild(item);
    });
  }

  renderEmptyActivities() {
    const activitiesList = document.getElementById('activities-list');
    if (!activitiesList) return;

    activitiesList.innerHTML = `
        <div class="activity-item">
            <div class="activity-icon">
                <i class="fas fa-info-circle"></i>
            </div>
            <div class="activity-content">
                <div class="activity-text">Пока нет выполненных задач</div>
                <div class="activity-time">Создайте первую задачу!</div>
            </div>
        </div>
    `;
  }

  renderErrorActivities() {
    const activitiesList = document.getElementById('activities-list');
    if (!activitiesList) return;

    activitiesList.innerHTML = `
        <div class="activity-item">
            <div class="activity-icon error">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div class="activity-content">
                <div class="activity-text">Ошибка загрузки активности</div>
                <div class="activity-time">Попробуйте обновить страницу</div>
            </div>
        </div>
    `;
  }

  async handleQuickCommand(event) {
    event.preventDefault();

    const input = document.getElementById('quick-input');
    const command = input.value.trim();

    if (!command) return;

    // Показываем индикатор выполнения
    this.showExecutionStatus(true);
    this.updateProgress(0, 'Отправка команды...');

    try {
      // ✅ ИСПРАВЛЕНО: /api/query → /api/tasks/query
      const response = await fetch('/api/tasks/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: command })
      });

      if (!response.ok) throw new Error(`HTTP ${ response.status }`);

      const data = await response.json();

      // Обновляем прогресс
      this.updateProgress(50, 'Выполнение...');

      if (data.is_compound) {
        // Составная команда - показываем прогресс по шагам
        await this.handleCompoundCommand(data);
      } else {
        // Простая команда
        this.updateProgress(100, 'Завершено');
        this.addToRecentCommands(command, data.overall_status || 'completed');
      }

      // Очищаем поле ввода
      input.value = '';

      // Обновляем активности
      setTimeout(() => this.loadRecentActivities(), 1000);

    } catch (error) {
      console.error('Ошибка выполнения команды:', error);
      this.updateProgress(0, `Ошибка: ${ error.message }`);
      this.showNotification('Ошибка выполнения команды', 'error');
    } finally {
      // Скрываем статус через 3 секунды
      setTimeout(() => this.showExecutionStatus(false), 3000);
    }
  }

  async handleCompoundCommand(data) {
    if (!data.steps || data.steps.length === 0) return;

    let completedSteps = 0;
    const totalSteps = data.steps.length;

    for (const step of data.steps) {
      this.updateProgress(
        (completedSteps / totalSteps) * 100,
        `Шаг ${ step.number }: ${ step.description }`
      );

      // Эмуляция времени выполнения шага
      await new Promise(resolve => setTimeout(resolve, 1000));

      if (step.status === 'completed') {
        completedSteps++;
      }
    }

    this.updateProgress(100, 'Все шаги завершены');
  }

  handleInputSuggestions(event) {
    const input = event.target;
    const query = input.value.trim().toLowerCase();

    if (query.length < 2) {
      this.hideSuggestions();
      return;
    }

    // Простые предложения на основе популярных команд
    const suggestions = this.getSuggestions(query);
    this.showSuggestions(suggestions);
  }

  getSuggestions(query) {
    const commonCommands = [
      'открой браузер',
      'покажи файлы',
      'системная информация',
      'создай файл',
      'найди файл',
      'открой калькулятор',
      'открой блокнот',
      'покажи процессы',
      'очисти корзину',
      'проверь интернет'
    ];

    return commonCommands
      .filter(cmd => cmd.toLowerCase().includes(query))
      .slice(0, 5);
  }

  showSuggestions(suggestions) {
    const suggestionsEl = document.getElementById('input-suggestions');
    if (!suggestionsEl || suggestions.length === 0) {
      this.hideSuggestions();
      return;
    }

    suggestionsEl.innerHTML = '';

    suggestions.forEach(suggestion => {
      const item = document.createElement('div');
      item.className = 'suggestion-item';
      item.textContent = suggestion;
      item.addEventListener('click', () => this.applySuggestion(suggestion));
      suggestionsEl.appendChild(item);
    });

    suggestionsEl.style.display = 'block';
  }

  hideSuggestions() {
    const suggestionsEl = document.getElementById('input-suggestions');
    if (suggestionsEl) {
      suggestionsEl.style.display = 'none';
    }
  }

  applySuggestion(suggestion) {
    const input = document.getElementById('quick-input');
    if (input) {
      input.value = suggestion;
      input.focus();
    }
    this.hideSuggestions();
  }

  handleInputKeydown(event) {
    const suggestionsEl = document.getElementById('input-suggestions');

    if (event.key === 'Escape') {
      this.hideSuggestions();
    }

    if (event.key === 'ArrowDown' && suggestionsEl?.style.display === 'block') {
      event.preventDefault();
      const items = suggestionsEl.querySelectorAll('.suggestion-item');
      if (items.length > 0) {
        items[0].focus();
      }
    }
  }

  handleQuickAction(event) {
    const btn = event.currentTarget;
    const command = btn.dataset.command;

    if (command) {
      const input = document.getElementById('quick-input');
      if (input) {
        input.value = command;
        input.focus();
      }
    }
  }

  filterRecentActivities(filter) {
    const items = document.querySelectorAll('.activity-item');

    items.forEach(item => {
      const icon = item.querySelector('.activity-icon');
      if (!icon) return;

      const status = this.getItemStatus(icon);

      if (filter === 'all' || status === filter) {
        item.style.display = 'flex';
      } else {
        item.style.display = 'none';
      }
    });
  }

  showExecutionStatus(show) {
    const statusEl = document.getElementById('quick-execution-status');
    if (statusEl) {
      statusEl.style.display = show ? 'block' : 'none';
    }
  }

  updateProgress(percentage, text) {
    const fillEl = document.getElementById('quick-progress-fill');
    const textEl = document.getElementById('quick-progress-text');

    if (fillEl) {
      fillEl.style.width = `${ percentage }%`;
    }

    if (textEl) {
      textEl.textContent = text;
    }
  }

  cancelExecution() {
    // Здесь будет логика отмены выполнения
    this.showExecutionStatus(false);
    this.showNotification('Выполнение отменено', 'info');
  }

  addToRecentCommands(command, status) {
    const recentList = document.getElementById('recent-commands-list');
    if (!recentList) return;

    const item = document.createElement('div');
    item.className = 'recent-item';
    item.innerHTML = `
        <i class="fas ${ this.getActivityIcon(status) }"></i>
        <span>${ this.escapeHtml(command) }</span>
    `;

    // Добавляем в начало списка
    recentList.insertBefore(item, recentList.firstChild);

    // Ограничиваем количество элементов
    const items = recentList.querySelectorAll('.recent-item');
    if (items.length > 5) {
      items[items.length - 1].remove();
    }
  }

  startStatusUpdates() {
    // Обновляем статус каждые 30 секунд
    this.statusUpdateInterval = setInterval(() => {
      this.updateSystemStatus();
      this.updateTasksStatus();
    }, 30000);
  }

  stopStatusUpdates() {
    if (this.statusUpdateInterval) {
      clearInterval(this.statusUpdateInterval);
      this.statusUpdateInterval = null;
    }
  }

  // Утилиты
  getStatusText(status) {
    const statusTexts = {
      'ready': 'Готова',
      'busy': 'Занята',
      'error': 'Ошибка',
      'unavailable': 'Недоступна'
    };
    return statusTexts[status] || 'Неизвестно';
  }

  getActivityIcon(status) {
    const icons = {
      'success': 'fa-check-circle',
      'completed': 'fa-check-circle',
      'error': 'fa-exclamation-circle',
      'failed': 'fa-exclamation-circle',
      'running': 'fa-spinner fa-spin',
      'pending': 'fa-clock'
    };
    return icons[status] || 'fa-question-circle';
  }

  getItemStatus(iconEl) {
    if (iconEl.classList.contains('success')) return 'success';
    if (iconEl.classList.contains('error')) return 'error';
    if (iconEl.classList.contains('running')) return 'running';
    return 'all';
  }

  formatTime(timestamp) {
    if (!timestamp) return '';

    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'только что';
    if (diffMins < 60) return `${ diffMins } мин назад`;
    if (diffMins < 1440) return `${ Math.floor(diffMins / 60) } ч назад`;

    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  showNotification(message, type = 'info') {
    // Интеграция с системой уведомлений
    if (window.showNotification) {
      window.showNotification(message, type);
    } else {
      console.log(`${ type.toUpperCase() }: ${ message }`);
    }
  }

  setErrorStatus() {
    const statusEl = document.getElementById('model-status');
    if (statusEl) {
      statusEl.querySelector('.status-indicator').className = 'status-indicator error';
      statusEl.querySelector('.status-text').textContent = 'Ошибка';
    }
  }
}

// Инициализируем Dashboard при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
  if (document.body.classList.contains('dashboard-page') || window.location.pathname === '/') {
    window.dashboard = new Dashboard();
  }
});

// Экспортируем для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Dashboard;
}
