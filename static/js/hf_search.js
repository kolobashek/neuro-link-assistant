class HFModelSearch {
    constructor() {
        this.searchInput = document.getElementById('hf-search-input');
        this.searchBtn = document.getElementById('hf-search-btn');
        this.resultsContainer = document.getElementById('hf-search-results');
        this.resultsList = document.getElementById('results-list');
        this.resultsCount = document.getElementById('results-count');

        this.bindEvents();
    }

    bindEvents() {
        this.searchBtn.addEventListener('click', () => this.performSearch());
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });
    }

    async performSearch() {
        const query = this.searchInput.value.trim();

        if (query.length < 2) {
            alert('Введите минимум 2 символа для поиска');
            return;
        }

        this.searchBtn.disabled = true;
        this.searchBtn.textContent = '🔄 Поиск...';

        try {
            const response = await fetch(`/api/models/search?q=${encodeURIComponent(query)}&limit=20`);
            const data = await response.json();

            if (data.success) {
                this.displayResults(data.models, data.total);
            } else {
                this.showError(data.error);
            }
        } catch (error) {
            this.showError('Ошибка соединения: ' + error.message);
        } finally {
            this.searchBtn.disabled = false;
            this.searchBtn.textContent = '🔍 Поиск';
        }
    }

    displayResults(models, total) {
        this.resultsCount.textContent = `Найдено: ${total}`;
        this.resultsContainer.style.display = 'block';

        this.resultsList.innerHTML = models.map(model => `
            <div class="model-item">
                <div class="model-header">
                    <h5>${model.name}</h5>
                    <button class="add-model-btn" onclick="hfSearch.addModel('${model.id}')">
                        ➕ Добавить
                    </button>
                </div>
                <p><strong>ID:</strong> ${model.id}</p>
                <p><strong>Автор:</strong> ${model.author}</p>
                <div class="model-stats">
                    <span>⬇️ ${model.downloads.toLocaleString()}</span>
                    <span>❤️ ${model.likes}</span>
                    <span>🏷️ ${model.pipeline_tag || 'N/A'}</span>
                </div>
                <p class="model-description">${model.description}</p>
                <a href="${model.url}" target="_blank" class="btn btn-link">🔗 Открыть на HuggingFace</a>
            </div>
        `).join('');
    }

    async addModel(modelId) {
        const btn = event.target;
        const originalText = btn.textContent;

        btn.disabled = true;
        btn.textContent = '⏳ Добавление...';

        try {
            const response = await fetch('/api/models/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ model_id: modelId })
            });

            const data = await response.json();

            if (data.success) {
                btn.textContent = '✅ Добавлено';
                btn.style.background = '#28a745';
                alert(`Модель ${modelId} успешно добавлена!`);
            } else {
                btn.textContent = '❌ Ошибка';
                btn.style.background = '#dc3545';
                alert(`Ошибка: ${data.error}`);
                setTimeout(() => {
                    btn.textContent = originalText;
                    btn.style.background = '';
                    btn.disabled = false;
                }, 3000);
            }
        } catch (error) {
            btn.textContent = '❌ Ошибка';
            alert('Ошибка соединения: ' + error.message);
        }
    }

    showError(message) {
        this.resultsContainer.style.display = 'block';
        this.resultsList.innerHTML = `<div class="alert alert-danger">${message}</div>`;
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.hfSearch = new HFModelSearch();
});
