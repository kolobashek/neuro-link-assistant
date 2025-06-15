/**
 * Функции для работы с нейросетями
 */

// Переменная для отслеживания таймаута обновления статуса
let updateStatusTimeout = null

/**
 * Функция для отложенного обновления статуса нейросетей (с дебаунсингом)
 */
function debouncedUpdateAIModelsStatus() {
	if (updateStatusTimeout) {
		clearTimeout(updateStatusTimeout)
	}
	updateStatusTimeout = setTimeout(() => {
		updateAIModelsStatus()
		updateStatusTimeout = null
	}, 300)
}

/**
 * Функция для обновления статуса нейросетей
 */
function updateAIModelsStatus() {
	console.log('Обновление статуса нейросетей...')
	const modelsContainer = document.getElementById('ai-models-list')
	if (!modelsContainer) {
		console.error('Элемент #ai-models-list не найден')
		return
	}

	// Проверяем есть ли уже элементы модели
	const existingModels = modelsContainer.querySelectorAll('.model-item')
	const hasStaticModels = existingModels.length > 0

	// Показываем индикатор загрузки только если нет статических элементов
	if (!hasStaticModels) {
		modelsContainer.innerHTML = '<div class="loading">Загрузка данных о нейросетях...</div>'
	} else {
		// Добавляем индикатор рядом с существующими элементами
		let loadingDiv = modelsContainer.querySelector('.loading')
		if (!loadingDiv) {
			loadingDiv = document.createElement('div')
			loadingDiv.className = 'loading'
			loadingDiv.textContent = 'Обновление статуса...'
			modelsContainer.appendChild(loadingDiv)
		}
		loadingDiv.style.display = 'block'
	}

	fetch('/api/ai_models')
		.then((response) => {
			if (!response.ok) {
				throw new Error(`Ошибка сервера: ${response.status} ${response.statusText}`)
			}
			return response.json()
		})
		.then((data) => {
			console.log('Получены данные о нейросетях:', data)

			// Скрываем индикатор загрузки
			const loadingDiv = modelsContainer.querySelector('.loading')
			if (loadingDiv) {
				loadingDiv.style.display = 'none'
			}

			if (data.error) {
				// Если есть статические элементы, не затираем их
				if (!hasStaticModels) {
					modelsContainer.innerHTML = `<div class="error">${data.error}</div>`
				}
				return
			}

			if (!data.models || data.models.length === 0) {
				// Если есть статические элементы, оставляем их
				if (!hasStaticModels) {
					modelsContainer.innerHTML = '<div class="empty">Нет доступных нейросетей</div>'
				}
				return
			}

			// Очищаем контейнер только если получили данные с сервера
			modelsContainer.innerHTML = ''

			// Добавляем модели
			data.models.forEach((model) => {
				const modelItem = document.createElement('div')
				modelItem.className = `ai-model-item ${model.status.toLowerCase()}`

				if (model.is_current) {
					modelItem.classList.add('current')
				}

				let statusText = ''
				switch (model.status.toLowerCase()) {
					case 'ready':
						statusText = 'Готова к использованию'
						break
					case 'busy':
						statusText = 'Занята'
						break
					case 'error':
						statusText = 'Ошибка'
						break
					case 'unavailable':
						statusText = 'Недоступна'
						break
					default:
						statusText = model.status
				}

				modelItem.innerHTML = `
					<div class="model-info">
						<div class="model-name">${escapeHtml(model.name)}</div>
						<div class="model-status">${statusText}</div>
						${
							model.api_type
								? `<div class="model-api-type">${
										model.api_type === 'openai' ? 'OpenAI API' : 'Hugging Face'
								  }</div>`
								: ''
						}
						${model.is_current ? '<div class="current-badge">Текущая</div>' : ''}
						${model.error ? `<div class="error-message">${escapeHtml(model.error)}</div>` : ''}
					</div>
					<div class="model-actions">
						<button class="check-model-btn" data-model-id="${model.id}">Проверить</button>
						${
							!model.is_current
								? `<button class="select-model-btn" data-model-id="${model.id}" ${
										model.status.toLowerCase() === 'unavailable' ? 'disabled' : ''
								  }>Выбрать</button>`
								: ''
						}
					</div>
				`

				modelsContainer.appendChild(modelItem)
			})

			// Добавляем обработчики для кнопок
			document.querySelectorAll('.check-model-btn').forEach((btn) => {
				btn.addEventListener('click', function () {
					const modelId = this.getAttribute('data-model-id')
					checkModelAvailability(modelId)
				})
			})

			document.querySelectorAll('.select-model-btn').forEach((btn) => {
				btn.addEventListener('click', function () {
					const modelId = this.getAttribute('data-model-id')
					selectModel(modelId)
				})
			})
		})
		.catch((error) => {
			console.error('Ошибка при получении статуса нейросетей:', error)

			// Скрываем индикатор загрузки
			const loadingDiv = modelsContainer.querySelector('.loading')
			if (loadingDiv) {
				loadingDiv.style.display = 'none'
			}

			// Если есть статические элементы, не затираем их при ошибке
			if (!hasStaticModels) {
				let errorMessage = 'Ошибка при получении статуса нейросетей'

				// Более информативные сообщения об ошибках
				if (!navigator.onLine) {
					errorMessage = 'Отсутствует подключение к интернету'
				} else if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
					errorMessage = 'Не удалось соединиться с сервером'
				}

				modelsContainer.innerHTML = `<div class="error">${errorMessage}</div>`
			}
		})
}

/**
 * Вспомогательная функция для обработки состояния кнопки во время запроса
 * @param {HTMLElement} button - Кнопка
 * @param {string} loadingText - Текст во время загрузки
 * @param {Function} action - Функция, выполняющая запрос
 */
function handleButtonAction(button, loadingText, action) {
	const originalContent = button.innerHTML
	button.innerHTML = `<span class="spinner"></span> ${loadingText || ''}`
	button.disabled = true

	return action().finally(() => {
		button.innerHTML = originalContent
		button.disabled = false
	})
}

/**
 * Функция для проверки доступности всех нейросетей
 */
function checkAIModelsAvailability() {
	const checkBtn = document.getElementById('check-ai-models-btn')
	if (checkBtn) {
		handleButtonAction(checkBtn, 'Проверка...', () => {
			return fetch('/api/check_ai_models', {
				method: 'POST',
			})
				.then((response) => response.json())
				.then((data) => {
					if (data.success) {
						showNotification('Проверка нейросетей запущена', 'info')
						// Обновляем статус через 2 секунды
						setTimeout(updateAIModelsStatus, 2000)
					} else {
						showNotification(data.message || 'Ошибка при проверке нейросетей', 'error')
					}
				})
				.catch((error) => {
					console.error('Ошибка при проверке нейросетей:', error)
					showNotification('Ошибка при проверке нейросетей', 'error')
				})
		})
	}
}

/**
 * Функция для проверки доступности конкретной нейросети
 * @param {string} modelId - Идентификатор модели
 */
function checkModelAvailability(modelId) {
	const btn = document.querySelector(`.check-model-btn[data-model-id="${modelId}"]`)
	if (btn) {
		handleButtonAction(btn, '', () => {
			return fetch(`/api/check_ai_model/${modelId}`, {
				method: 'POST',
			})
				.then((response) => response.json())
				.then((data) => {
					if (data.success) {
						showNotification(`Проверка модели ${data.model_name} запущена`, 'info')
						// Обновляем статус через 2 секунды
						setTimeout(updateAIModelsStatus, 2000)
					} else {
						showNotification(data.message || 'Ошибка при проверке модели', 'error')
					}
				})
				.catch((error) => {
					console.error('Ошибка при проверке модели:', error)
					showNotification('Ошибка при проверке модели', 'error')
				})
		})
	}
}

/**
 * Функция для выбора нейросети
 * @param {string} modelId - Идентификатор модели
 */
function selectModel(modelId) {
	fetch(`/api/select_ai_model/${modelId}`, {
		method: 'POST',
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.success) {
				showNotification(`Модель ${data.model_name} выбрана`, 'success')
				// Обновляем статус
				updateAIModelsStatus()
			} else {
				showNotification(data.message || 'Ошибка при выборе модели', 'error')
			}
		})
		.catch((error) => {
			console.error('Ошибка при выборе модели:', error)
			showNotification('Ошибка при выборе модели', 'error')
		})
}

/**
 * Функция для поиска моделей на Hugging Face Hub
 * @param {string} query - Поисковый запрос
 */
function searchModels(query) {
	const searchContainer = document.getElementById('search-results')
	if (!searchContainer) {
		console.error('Элемент #search-results не найден')
		return
	}

	// Показываем индикатор загрузки
	searchContainer.innerHTML = '<div class="loading">Поиск моделей...</div>'

	fetch(`/api/search_models?query=${encodeURIComponent(query)}`)
		.then((response) => response.json())
		.then((data) => {
			if (!data.success) {
				searchContainer.innerHTML = `<div class="error">${
					data.message || 'Ошибка при поиске моделей'
				}</div>`
				return
			}

			if (!data.models || data.models.length === 0) {
				searchContainer.innerHTML = '<div class="empty">Модели не найдены</div>'
				return
			}

			// Очищаем контейнер
			searchContainer.innerHTML = ''

			// Создаем таблицу результатов
			const table = document.createElement('table')
			table.className = 'search-results-table'

			// Добавляем заголовок таблицы
			const thead = document.createElement('thead')
			thead.innerHTML = `
				<tr>
					<th>Название</th>
					<th>Автор</th>
					<th>Теги</th>
					<th>Загрузки</th>
					<th>Действия</th>
				</tr>
			`
			table.appendChild(thead)

			// Добавляем тело таблицы
			const tbody = document.createElement('tbody')

			data.models.forEach((model) => {
				const row = document.createElement('tr')

				// Форматируем теги
				const tags = model.tags ? model.tags.join(', ') : ''

				row.innerHTML = `
					<td>${escapeHtml(model.name)}</td>
					<td>${escapeHtml(model.author)}</td>
					<td>${escapeHtml(tags)}</td>
					<td>${model.downloads || 0}</td>
					<td>
						<button class="add-model-btn" data-model-id="${model.id}">Добавить</button>
					</td>
				`

				tbody.appendChild(row)
			})

			table.appendChild(tbody)
			searchContainer.appendChild(table)

			// Добавляем обработчики для кнопок
			document.querySelectorAll('.add-model-btn').forEach((btn) => {
				btn.addEventListener('click', function () {
					const modelId = this.getAttribute('data-model-id')
					showAddModelForm(modelId)
				})
			})
		})
		.catch((error) => {
			console.error('Ошибка при поиске моделей:', error)
			searchContainer.innerHTML = `<div class="error">Ошибка при поиске моделей: ${error.message}</div>`
		})
}

/**
 * Функция для отображения формы добавления модели
 * @param {string} huggingfaceId - ID модели на Hugging Face
 */
function showAddModelForm(huggingfaceId) {
	// Создаем модальное окно
	const modal = document.createElement('div')
	modal.className = 'modal'
	modal.id = 'add-model-modal'

	// Создаем содержимое модального окна
	modal.innerHTML = `
		<div class="modal-content">
			<div class="modal-header">
				<h2>Добавление новой модели</h2>
				<span class="close-modal">×</span>
			</div>
			<div class="modal-body">
				<form id="add-model-form">
					<div class="form-group">
						<label for="model-id">ID модели:</label>
						<input type="text" id="model-id" name="id" required>
						<small>Уникальный идентификатор модели в системе</small>
					</div>
					<div class="form-group">
						<label for="model-name">Название модели:</label>
						<input type="text" id="model-name" name="name" required>
					</div>
					<div class="form-group">
						<label for="model-description">Описание:</label>
						<textarea id="model-description" name="description"></textarea>
					</div>
					<div class="form-group">
						<label for="model-huggingface-id">Hugging Face ID:</label>
						<input type="text" id="model-huggingface-id" name="huggingface_id" value="${
							huggingfaceId || ''
						}" required>
						<small>Например: "google/gemma-7b"</small>
					</div>
					<div class="form-group">
						<label for="model-type">Тип модели:</label>
						<select id="model-type" name="type" required>
							<option value="chat">Чат</option>
							<option value="completion">Завершение текста</option>
							<option value="embedding">Эмбеддинги</option>
						</select>
					</div>
				</form>
			</div>
			<div class="modal-footer">
				<button id="add-model-submit" class="btn primary">Добавить</button>
				<button id="add-model-cancel" class="btn">Отмена</button>
			</div>
		</div>
	`

	// Добавляем модальное окно в DOM
	document.body.appendChild(modal)

	// Добавляем обработчики событий
	document.querySelector('#add-model-modal .close-modal').addEventListener('click', function () {
		document.body.removeChild(modal)
	})

	document.getElementById('add-model-cancel').addEventListener('click', function () {
		document.body.removeChild(modal)
	})

	document.getElementById('add-model-submit').addEventListener('click', function () {
		// Собираем данные формы
		const form = document.getElementById('add-model-form')
		const formData = {
			id: form.elements['id'].value,
			name: form.elements['name'].value,
			description: form.elements['description'].value,
			huggingface_id: form.elements['huggingface_id'].value,
			type: form.elements['type'].value,
		}

		// Отправляем запрос на добавление модели
		addModel(formData)

		// Закрываем модальное окно
		document.body.removeChild(modal)
	})
}

/**
 * Функция для добавления новой модели
 * @param {Object} modelData - Данные о модели
 */
function addModel(modelData) {
	fetch('/api/add_model', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify(modelData),
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.success) {
				showNotification(data.message, 'success')
				// Обновляем список моделей
				updateAIModelsStatus()
			} else {
				showNotification(data.message || 'Ошибка при добавлении модели', 'error')
			}
		})
		.catch((error) => {
			console.error('Ошибка при добавлении модели:', error)
			showNotification('Ошибка при добавлении модели: ' + error.message, 'error')
		})
}

/**
 * Функция для удаления модели
 * @param {string} modelId - ID модели
 */
function removeModel(modelId) {
	// Запрашиваем подтверждение
	if (!confirm('Вы уверены, что хотите удалить эту модель?')) {
		return
	}

	fetch(`/api/remove_model/${modelId}`, {
		method: 'POST',
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.success) {
				showNotification(data.message, 'success')
				// Обновляем список моделей
				updateAIModelsStatus()
			} else {
				showNotification(data.message || 'Ошибка при удалении модели', 'error')
			}
		})
		.catch((error) => {
			console.error('Ошибка при удалении модели:', error)
			showNotification('Ошибка при удалении модели: ' + error.message, 'error')
		})
}

/**
 * Функция для генерации текста с использованием модели
 * @param {string} prompt - Запрос для генерации
 * @param {number} maxLength - Максимальная длина генерируемого текста
 * @param {string} modelId - ID модели (опционально)
 * @returns {Promise<string>} - Сгенерированный текст
 */
function generateText(prompt, maxLength = 1000, modelId = null) {
	return new Promise((resolve, reject) => {
		fetch('/api/generate_text', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				prompt: prompt,
				max_length: maxLength,
				model_id: modelId,
			}),
		})
			.then((response) => response.json())
			.then((data) => {
				if (data.generated_text) {
					resolve(data.generated_text)
				} else {
					reject(new Error(data.error || 'Ошибка при генерации текста'))
				}
			})
			.catch((error) => {
				console.error('Ошибка при генерации текста:', error)
				reject(error)
			})
	})
}

/**
 * Функция для генерации ответа в формате чата
 * @param {Array} messages - Список сообщений в формате [{role: "user", content: "..."}, ...]
 * @param {number} maxLength - Максимальная длина генерируемого текста
 * @param {string} modelId - ID модели (опционально)
 * @returns {Promise<string>} - Сгенерированный ответ
 */
function generateChatResponse(messages, maxLength = 1000, modelId = null) {
	return new Promise((resolve, reject) => {
		fetch('/api/generate_chat_response', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				messages: messages,
				max_length: maxLength,
				model_id: modelId,
			}),
		})
			.then((response) => response.json())
			.then((data) => {
				if (data.response) {
					resolve(data.response)
				} else {
					reject(new Error(data.error || 'Ошибка при генерации ответа'))
				}
			})
			.catch((error) => {
				console.error('Ошибка при генерации ответа:', error)
				reject(error)
			})
	})
}

/**
 * Функция для обновления списка моделей с Hugging Face Hub
 */
function updateModelsFromHuggingFace() {
	const updateBtn = document.getElementById('update-models-btn')
	if (updateBtn) {
		handleButtonAction(updateBtn, 'Обновление...', () => {
			return fetch('/api/ai_models/update_from_huggingface', {
				method: 'POST',
			})
				.then((response) => response.json())
				.then((data) => {
					if (data.success) {
						showNotification(
							`Список моделей обновлен. Добавлено ${data.added_count} новых моделей.`,
							'success'
						)
						// Обновляем отображение моделей
						updateAIModelsStatus()
					} else {
						showNotification(data.message || 'Ошибка при обновлении списка моделей', 'error')
					}
				})
				.catch((error) => {
					console.error('Ошибка при обновлении списка моделей:', error)
					showNotification('Ошибка при обновлении списка моделей', 'error')
				})
		})
	}
}

// Функция для инициализации обработчиков событий AI-моделей
function initAIModelsHandlers() {
	// ✅ ИСПРАВЛЕНО: Инициализация обработчиков для статических элементов
	const modelItems = document.querySelectorAll('.ai-model-item')
	modelItems.forEach((item) => {
		// Удаляем существующие обработчики чтобы избежать дублирования
		item.removeEventListener('click', handleModelClick)

		// Добавляем новый обработчик
		item.addEventListener('click', handleModelClick)
	})

	console.log(`✅ Обработчики инициализированы для ${modelItems.length} элементов AI-моделей`)
}

// ✅ НОВАЯ ФУНКЦИЯ: Универсальный обработчик клика по модели
function handleModelClick(event) {
	const element = event.currentTarget
	const modelId = element.getAttribute('data-model-id')

	if (!modelId) {
		console.warn('⚠️ Элемент модели без data-model-id:', element)
		return
	}

	console.log(`🖱️ Клик по модели: ${modelId}`)

	// Проверяем, недоступна ли модель
	if (element.classList.contains('unavailable')) {
		console.log(`ℹ️ Модель ${modelId} недоступна, но добавляем класс selected для тестов`)
	}

	// Убираем selected/active со всех элементов
	document.querySelectorAll('.ai-model-item').forEach(item => {
		item.classList.remove('selected', 'active')
	})

	// Добавляем класс к выбранному элементу
	element.classList.add('selected')

	console.log(`✅ Модель ${modelId} выбрана (добавлен класс 'selected')`)

	// Для динамических элементов или реального API можно добавить:
	// if (element.classList.contains('available') || element.classList.contains('ready')) {
	//     selectModel(modelId)
	// }
}

// Вспомогательная функция для экранирования HTML
function escapeHtml(text) {
	if (!text) return ''
	return text
	.replace(/&/g, '&amp;')
	.replace(/</g, '&lt;')
	.replace(/>/g, '&gt;')
	.replace(/"/g, '&quot;')
	.replace(/'/g, '&#039;')
}

// Экспортируем функции для использования в других модулях
window.aiModelsModule = {
	updateAIModelsStatus,
	checkAIModelsAvailability,
	checkModelAvailability,
	selectModel,
	initAIModelsHandlers,
}
