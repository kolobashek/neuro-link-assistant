/**
 * Функция для обновления статуса нейросетей
 */
function updateAIModelsStatus() {
	console.log('Обновление статуса нейросетей...')
	fetch('/api/ai_models')
		.then((response) => response.json())
		.then((data) => {
			console.log('Получены данные о нейросетях:', data)
			const modelsContainer = document.getElementById('ai-models-list')
			if (!modelsContainer) {
				console.error('Элемент #ai-models-list не найден')
				return
			}

			if (data.error) {
				modelsContainer.innerHTML = `<div class="error">${data.error}</div>`
				return
			}

			if (!data.models || data.models.length === 0) {
				modelsContainer.innerHTML = '<div class="empty">Нет доступных нейросетей</div>'
				return
			}

			// Очищаем контейнер
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
                    <div class="model-name">${escapeHtml(model.name)}</div>
                    <div class="model-status">${statusText}</div>
                    ${model.is_current ? '<div class="current-badge">Текущая</div>' : ''}
                    ${
											model.error
												? `<div class="error-message">${escapeHtml(model.error)}</div>`
												: ''
										}
                    <div class="model-actions">
                        <button class="check-model-btn" data-model-id="${
													model.id
												}">Проверить</button>
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
			const modelsContainer = document.getElementById('ai-models-list')
			if (modelsContainer) {
				modelsContainer.innerHTML =
					'<div class="error">Ошибка при получении статуса нейросетей</div>'
			}
		})
}

/**
 * Функция для проверки доступности всех нейросетей
 */
function checkAIModelsAvailability() {
	const checkBtn = document.getElementById('check-ai-models-btn')
	if (checkBtn) {
		// Добавляем спиннер и блокируем кнопку
		const originalContent = checkBtn.innerHTML
		checkBtn.innerHTML = '<span class="spinner"></span> Проверка...'
		checkBtn.disabled = true

		fetch('/api/check_ai_models', {
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
			.finally(() => {
				// Восстанавливаем кнопку
				checkBtn.innerHTML = originalContent
				checkBtn.disabled = false
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
		// Добавляем спиннер и блокируем кнопку
		const originalContent = btn.innerHTML
		btn.innerHTML = '<span class="spinner"></span>'
		btn.disabled = true

		fetch(`/api/check_ai_model/${modelId}`, {
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
			.finally(() => {
				// Восстанавливаем кнопку
				btn.innerHTML = originalContent
				btn.disabled = false
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
