class ModelsManager {
  constructor() {
    this.currentTab = 'active-models';
    this.activeModels = [];
    this.catalogModels = [];
    this.searchResults = [];

    this.init();
  }

  init() {
    this.bindEvents();
    this.loadActiveModels();
    this.loadCatalogModels();
    this.updateTabCounts();
  }

  bindEvents() {
    // Переключение табов
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.switchTab(e.target.closest('.tab-btn').dataset.tab);
      });
    });

    // Поиск в каталоге
    const catalogSearch = document.getElementById('catalog-search');
    if (catalogSearch) {
      catalogSearch.addEventListener('input', this.debounce(() => {
        this.filterCatalog();
      }, 300));
    }

    // Фильтры каталога
    document.getElementById('provider-filter')?.addEventListener('change', () => this.filterCatalog());
    document.getElementById('status-filter')?.addEventListener('change', () => this.filterCatalog());

    // HuggingFace поиск
    document.getElementById('hf-search-btn')?.addEventListener('click', () => this.searchHuggingFace());
    document.getElementById('hf-search-input')?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.searchHuggingFace();
    });

    // Действия с моделями
    document.addEventListener('click', (e) => {
      if (e.target.matches('.btn-select')) {
        this.selectModel(e.target.dataset.modelId);
      } else if (e.target.matches('.btn-config')) {
        this.configureModel(e.target.dataset.modelId);
      } else if (e.target.matches('.btn-remove')) {
        this.removeModel(e.target.dataset.modelId);
      } else if (e.target.matches('.btn-add-model')) {
        this.addHuggingFaceModel(e.target.dataset.modelId);
      }
    });

    // Обновление данных
    document.getElementById('refresh-active')?.addEventListener('click', () => this.loadActiveModels());
    document.getElementById('check-all')?.addEventListener('click', () => this.checkAllModels());
  }

  switchTab(tabId) {
    // Обновляем кнопки табов
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tab === tabId);
    });

    // Обновляем панели
    document.querySelectorAll('.tab-panel').forEach(panel => {
      panel.classList.toggle('active', panel.id === tabId);
    });

    this.currentTab = tabId;

    // Загружаем данные при необходимости
    if (tabId === 'catalog-models' && this.catalogModels.length === 0) {
      this.loadCatalogModels();
    }
  }

  async loadActiveModels() {
    const grid = document.getElementById('active-models-grid');
    grid.innerHTML = '<div class="loading-placeholder"><i class="fas fa-spinner fa-spin"></i>Загрузка активных моделей...</div>';

    try {
      const response = await fetch('/api/models/active');
      const data = await response.json();

      if (data.success) {
        this.activeModels = data.models;
        this.renderActiveModels();
      } else {
        this.showError(grid, 'Ошибка загрузки активных моделей: ' + data.error);
      }
    } catch (error) {
      this.showError(grid, 'Ошибка соединения: ' + error.message);
    }

    this.updateTabCounts();
  }

  async loadCatalogModels() {
    const grid = document.getElementById('catalog-models-grid');
    grid.innerHTML = '<div class="loading-placeholder"><i class="fas fa-spinner fa-spin"></i>Загрузка каталога моделей...</div>';

    try {
      const response = await fetch('/api/models/catalog');
      const data = await response.json();

      if (data.success) {
        this.catalogModels = data.models;
        this.renderCatalogModels();
      } else {
        this.showError(grid, 'Ошибка загрузки каталога: ' + data.error);
      }
    } catch (error) {
      this.showError(grid, 'Ошибка соединения: ' + error.message);
    }

    this.updateTabCounts();
  }

  renderActiveModels() {
    const grid = document.getElementById('active-models-grid');

    if (this.activeModels.length === 0) {
      grid.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-robot"></i>
                    <h3>Нет активных моделей</h3>
                    <p>Добавьте модели из каталога или найдите новые в разделе поиска</p>
                </div>
            `;
      return;
    }

    grid.innerHTML = this.activeModels.map(model => `
            <div class="model-card active-card" data-model-id="${ model.id }">
                <div class="model-header">
                    <div class="model-info">
                        <h3 class="model-name">${ model.name }</h3>
                        <p class="model-description">${ model.description || 'Описание отсутствует' }</p>
                        <div class="model-meta">
                            <span class="meta-item">
                                <i class="fas fa-building"></i>
                                ${ model.provider }
                            </span>
                            <span class="meta-item">
                                <i class="fas fa-tag"></i>
                                ${ model.model_type || 'Неизвестный тип' }
                            </span>
                            ${ model.is_api ? '<span class="meta-item"><i class="fas fa-cloud"></i>API</span>' : '<span class="meta-item"><i class="fas fa-desktop"></i>Локальная</span>' }
                        </div>
                    </div>
                </div>
                <div class="model-status">
                    <span class="status-badge ${ this.getStatusClass(model.status) }">
                        <i class="fas ${ this.getStatusIcon(model.status) }"></i>
                        ${ this.getStatusText(model.status) }
                    </span>
                </div>
                <div class="model-actions">
                    <button class="btn btn-select" data-model-id="${ model.id }"
                            ${ model.status !== 'ready' ? 'disabled' : '' }>
                        <i class="fas fa-check"></i> Выбрать
                    </button>
                    <button class="btn btn-config" data-model-id="${ model.id }">
                        <i class="fas fa-cog"></i> Настройки
                    </button>
                    <button class="btn btn-remove" data-model-id="${ model.id }">
                        <i class="fas fa-trash"></i> Удалить
                    </button>
                </div>
            </div>
        `).join('');
  }

  renderCatalogModels(filteredModels = null) {
    const grid = document.getElementById('catalog-models-grid');
    const models = filteredModels || this.catalogModels;

    if (models.length === 0) {
      grid.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-database"></i>
                    <h3>Модели не найдены</h3>
                    <p>Попробуйте изменить фильтры поиска</p>
                </div>
            `;
      return;
    }

    grid.innerHTML = models.map(model => `
            <div class="model-card ${ model.status === 'unavailable' ? 'unavailable' : '' }" data-model-id="${ model.id }">
                <div class="model-header">
                    <div class="model-info">
                        <h3 class="model-name">${ model.name }</h3>
                        <p class="model-description">${ model.description || 'Описание отсутствует' }</p>
                        <div class="model-meta">
                            <span class="meta-item">
                                <i class="fas fa-building"></i>
                                ${ model.provider }
                            </span>
                            ${ model.downloads ? `<span class="meta-item"><i class="fas fa-download"></i>${ this.formatNumber(model.downloads) }</span>` : '' }
                            ${ model.likes ? `<span class="meta-item"><i class="fas fa-heart"></i>${ model.likes }</span>` : '' }
                        </div>
                    </div>
                </div>
                <div class="model-status">
                    <span class="status-badge ${ this.getStatusClass(model.status) }">
                        <i class="fas ${ this.getStatusIcon(model.status) }"></i>
                        ${ this.getStatusText(model.status) }
                    </span>
                </div>
                <div class="model-actions">
                    <button class="btn btn-select" data-model-id="${ model.id }"
                            ${ model.status !== 'ready' ? 'disabled' : '' }>
                        <i class="fas fa-plus"></i> Добавить
                    </button>
                    <button class="btn btn-config" data-model-id="${ model.id }">
                        <i class="fas fa-info"></i> Подробнее
                    </button>
                </div>
            </div>
        `).join('');
  }

  filterCatalog() {
    const searchTerm = document.getElementById('catalog-search').value.toLowerCase();
    const providerFilter = document.getElementById('provider-filter').value;
    const statusFilter = document.getElementById('status-filter').value;

    const filtered = this.catalogModels.filter(model => {
      const matchesSearch = !searchTerm ||
        model.name.toLowerCase().includes(searchTerm) ||
        (model.description && model.description.toLowerCase().includes(searchTerm));

      const matchesProvider = !providerFilter || model.provider === providerFilter;
      const matchesStatus = !statusFilter || model.status === statusFilter;

      return matchesSearch && matchesProvider && matchesStatus;
    });

    this.renderCatalogModels(filtered);
  }

  async searchHuggingFace() {
    const input = document.getElementById('hf-search-input');
    const btn = document.getElementById('hf-search-btn');
    const resultsContainer = document.getElementById('hf-search-results');

    const query = input.value.trim();

    if (query.length < 2) {
      this.showNotification('Введите минимум 2 символа для поиска', 'warning');
      return;
    }

    // Состояние загрузки
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Поиск...';

    const textGenOnly = document.getElementById('search-text-gen').checked;
    const popularOnly = document.getElementById('search-popular').checked;

    try {
      let url = `/api/models/search?q=${ encodeURIComponent(query) }&limit=20`;
      if (textGenOnly) url += '&filter=text-generation';
      if (popularOnly) url += '&min_downloads=1000';

      const response = await fetch(url);
      const data = await response.json();

      if (data.success) {
        this.searchResults = data.models;
        this.renderSearchResults();
      } else {
        this.showError(resultsContainer, data.error);
      }
    } catch (error) {
      this.showError(resultsContainer, 'Ошибка поиска: ' + error.message);
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-search"></i> Поиск';
    }
  }

  renderSearchResults() {
    const container = document.getElementById('hf-search-results');

    if (this.searchResults.length === 0) {
      container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-search"></i>
                    <h3>Ничего не найдено</h3>
                    <p>Попробуйте изменить запрос или снять фильтры</p>
                </div>
            `;
      return;
    }

    container.innerHTML = `
            <div class="results-header">
                <h4>Результаты поиска</h4>
                <span class="badge">Найдено: ${ this.searchResults.length }</span>
            </div>
            <div class="models-grid">
                ${ this.searchResults.map(model => `
                    <div class="hf-model-card">
                        <div class="hf-model-header">
                            <h5 class="hf-model-title">${ model.name }</h5>
                            <button class="btn-add-model" data-model-id="${ model.id }">
                                ➕ Добавить
                            </button>
                        </div>
                        <p><strong>ID:</strong> ${ model.id }</p>
                        <p><strong>Автор:</strong> ${ model.author }</p>
                        <div class="hf-model-stats">
                            <span><i class="fas fa-download"></i> ${ this.formatNumber(model.downloads) }</span>
                            <span><i class="fas fa-heart"></i> ${ model.likes }</span>
                            ${ model.pipeline_tag ? `<span><i class="fas fa-tag"></i> ${ model.pipeline_tag }</span>` : '' }
                        </div>
                        <p class="model-description">${ model.description || '' }</p>
                        <a href="${ model.url }" target="_blank" class="btn btn-link">
                            <i class="fas fa-external-link-alt"></i> Открыть на HuggingFace
                        </a>
                    </div>
                `).join('') }
            </div>
        `;
  }

  async selectModel(modelId) {
    try {
      const response = await fetch('/api/models/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_id: modelId })
      });

      const data = await response.json();

      if (data.success) {
        this.showNotification('Модель успешно выбрана', 'success');
        this.loadActiveModels();
      } else {
        this.showNotification('Ошибка выбора модели: ' + data.error, 'error');
      }
    } catch (error) {
      this.showNotification('Ошибка соединения: ' + error.message, 'error');
    }
  }

  configureModel(modelId) {
    // Открываем модальное окно настроек
    const modal = document.getElementById('model-config-modal');
    const title = document.getElementById('config-modal-title');
    const body = document.getElementById('config-modal-body');

    title.textContent = `Настройка модели: ${ modelId }`;
    body.innerHTML = '<div class="loading-placeholder"><i class="fas fa-spinner fa-spin"></i>Загрузка настроек...</div>';

    modal.classList.add('active');

    // Загружаем настройки
    this.loadModelConfig(modelId);
  }

  async loadModelConfig(modelId) {
    try {
      const response = await fetch(`/api/models/${ modelId }/config`);
      const data = await response.json();

      if (data.success) {
        this.renderModelConfig(data.config);
      } else {
        document.getElementById('config-modal-body').innerHTML =
          `<div class="error-state">Ошибка загрузки настроек: ${ data.error }</div>`;
      }
    } catch (error) {
      document.getElementById('config-modal-body').innerHTML =
        `<div class="error-state">Ошибка соединения: ${ error.message }</div>`;
    }
  }

  /* Продолжение renderModelConfig */

  renderModelConfig(config) {
    const body = document.getElementById('config-modal-body');
    body.innerHTML = `
            <form id="model-config-form">
                <div class="form-group">
                    <label>API ключ:</label>
                    <input type="password" name="api_key" value="${ config.api_key || '' }" class="form-control">
                </div>
                <div class="form-group">
                    <label>Температура (0-1):</label>
                    <input type="number" name="temperature" step="0.1" min="0" max="1"
                           value="${ config.temperature || 0.7 }" class="form-control">
                </div>
                <div class="form-group">
                    <label>Максимальное количество токенов:</label>
                    <input type="number" name="max_tokens" min="1" max="4000"
                           value="${ config.max_tokens || 150 }" class="form-control">
                </div>
                <div class="form-group">
                    <label>Top P (0-1):</label>
                    <input type="number" name="top_p" step="0.1" min="0" max="1"
                           value="${ config.top_p || 0.9 }" class="form-control">
                </div>
                <div class="form-group">
                    <label>Частотный штраф (0-2):</label>
                    <input type="number" name="frequency_penalty" step="0.1" min="0" max="2"
                           value="${ config.frequency_penalty || 0 }" class="form-control">
                </div>
                <div class="form-group">
                    <label>Штраф за повторение (0-2):</label>
                    <input type="number" name="presence_penalty" step="0.1" min="0" max="2"
                           value="${ config.presence_penalty || 0 }" class="form-control">
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" name="is_active" ${ config.is_active ? 'checked' : '' }>
                        Активная модель
                    </label>
                </div>
            </form>
        `;
  }

  async removeModel(modelId) {
    if (!confirm('Вы уверены, что хотите удалить эту модель?')) {
      return;
    }

    try {
      const response = await fetch(`/api/models/${ modelId }`, {
        method: 'DELETE'
      });

      const data = await response.json();

      if (data.success) {
        this.showNotification('Модель успешно удалена', 'success');
        this.loadActiveModels();
        this.loadCatalogModels();
      } else {
        this.showNotification('Ошибка удаления модели: ' + data.error, 'error');
      }
    } catch (error) {
      this.showNotification('Ошибка соединения: ' + error.message, 'error');
    }
  }

  async addHuggingFaceModel(modelId) {
    const btn = event.target;
    const originalText = btn.textContent;

    btn.disabled = true;
    btn.textContent = '⏳ Добавление...';

    try {
      const response = await fetch('/api/models/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_id: modelId })
      });

      const data = await response.json();

      if (data.success) {
        btn.textContent = '✅ Добавлено';
        btn.style.background = 'var(--success-color)';
        this.showNotification(`Модель ${ modelId } успешно добавлена!`, 'success');

        // Обновляем списки
        setTimeout(() => {
          this.loadActiveModels();
          this.loadCatalogModels();
        }, 1000);
      } else {
        btn.textContent = '❌ Ошибка';
        btn.style.background = 'var(--error-color)';
        this.showNotification(`Ошибка добавления: ${ data.error }`, 'error');

        setTimeout(() => {
          btn.textContent = originalText;
          btn.style.background = '';
          btn.disabled = false;
        }, 3000);
      }
    } catch (error) {
      btn.textContent = '❌ Ошибка';
      btn.style.background = 'var(--error-color)';
      this.showNotification('Ошибка соединения: ' + error.message, 'error');

      setTimeout(() => {
        btn.textContent = originalText;
        btn.style.background = '';
        btn.disabled = false;
      }, 3000);
    }
  }

  async checkAllModels() {
    const btn = document.getElementById('check-all');
    const originalText = btn.textContent;

    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Проверка...';

    try {
      const response = await fetch('/api/models/check-all', {
        method: 'POST'
      });

      const data = await response.json();

      if (data.success) {
        this.showNotification(`Проверка завершена. Доступно: ${ data.available }, Недоступно: ${ data.unavailable }`, 'info');
        this.loadActiveModels();
      } else {
        this.showNotification('Ошибка проверки моделей: ' + data.error, 'error');
      }
    } catch (error) {
      this.showNotification('Ошибка соединения: ' + error.message, 'error');
    } finally {
      btn.disabled = false;
      btn.innerHTML = originalText;
    }
  }

  updateTabCounts() {
    const activeCount = document.getElementById('active-count');
    const catalogCount = document.getElementById('catalog-count');

    if (activeCount) {
      activeCount.textContent = this.activeModels.length;
    }
    if (catalogCount) {
      catalogCount.textContent = this.catalogModels.length;
    }
  }

  // Утилитарные методы
  getStatusClass(status) {
    const statusMap = {
      'ready': 'status-ready',
      'busy': 'status-busy',
      'unavailable': 'status-unavailable',
      'error': 'status-error',
      'loading': 'status-loading'
    };
    return statusMap[status] || 'status-unavailable';
  }

  getStatusIcon(status) {
    const iconMap = {
      'ready': 'fa-check-circle',
      'busy': 'fa-clock',
      'unavailable': 'fa-times-circle',
      'error': 'fa-exclamation-triangle',
      'loading': 'fa-spinner'
    };
    return iconMap[status] || 'fa-question-circle';
  }

  getStatusText(status) {
    const textMap = {
      'ready': 'Готов',
      'busy': 'Занят',
      'unavailable': 'Недоступен',
      'error': 'Ошибка',
      'loading': 'Загрузка'
    };
    return textMap[status] || 'Неизвестно';
  }

  formatNumber(num) {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  }

  showError(container, message) {
    container.innerHTML = `
            <div class="error-state">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Ошибка</h3>
                <p>${ message }</p>
                <button class="btn btn-primary" onclick="location.reload()">Перезагрузить</button>
            </div>
        `;
  }

  showNotification(message, type = 'info') {
    // Создаем уведомление
    const notification = document.createElement('div');
    notification.className = `notification notification-${ type }`;
    notification.innerHTML = `
            <i class="fas ${ this.getNotificationIcon(type) }"></i>
            <span>${ message }</span>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

    // Добавляем в контейнер уведомлений
    let container = document.getElementById('notifications');
    if (!container) {
      container = document.createElement('div');
      container.id = 'notifications';
      container.className = 'notifications-container';
      document.body.appendChild(container);
    }

    container.appendChild(notification);

    // Автоматическое скрытие через 5 секунд
    setTimeout(() => {
      if (notification.parentElement) {
        notification.remove();
      }
    }, 5000);
  }

  getNotificationIcon(type) {
    const iconMap = {
      'success': 'fa-check-circle',
      'error': 'fa-exclamation-circle',
      'warning': 'fa-exclamation-triangle',
      'info': 'fa-info-circle'
    };
    return iconMap[type] || 'fa-info-circle';
  }

  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
  window.modelsManager = new ModelsManager();

  // Сохранение настроек модели
  document.getElementById('save-config')?.addEventListener('click', async () => {
    const form = document.getElementById('model-config-form');
    const formData = new FormData(form);
    const config = Object.fromEntries(formData);

    try {
      const response = await fetch(`/api/models/${ config.model_id }/config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });

      const data = await response.json();

      if (data.success) {
        window.modelsManager.showNotification('Настройки сохранены', 'success');
        document.getElementById('model-config-modal').classList.remove('active');
        window.modelsManager.loadActiveModels();
      } else {
        window.modelsManager.showNotification('Ошибка сохранения: ' + data.error, 'error');
      }
    } catch (error) {
      window.modelsManager.showNotification('Ошибка соединения: ' + error.message, 'error');
    }
  });
});
