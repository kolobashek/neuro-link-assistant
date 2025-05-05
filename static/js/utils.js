/**
 * Утилиты для работы с интерфейсом и данными
 */

/**
 * Функция для отображения уведомлений
 * @param {string} message - Текст уведомления
 * @param {string} type - Тип уведомления (success, error, warning, info)
 * @param {number} duration - Длительность отображения в мс (0 - не скрывать)
 */
function showNotification(message, type = 'info', duration = 3000) {
	// Проверяем, существует ли контейнер для уведомлений
	let notificationContainer = document.getElementById('notification-container')
	if (!notificationContainer) {
		notificationContainer = document.createElement('div')
		notificationContainer.id = 'notification-container'
		notificationContainer.style.position = 'fixed'
		notificationContainer.style.top = '20px'
		notificationContainer.style.right = '20px'
		notificationContainer.style.zIndex = '1000'
		document.body.appendChild(notificationContainer)
	}

	// Создаем уведомление
	const notification = document.createElement('div')
	notification.className = `notification ${type}`

	// Если сообщение содержит переносы строк, используем pre для форматирования
	if (message.includes('\n')) {
		const pre = document.createElement('pre')
		pre.textContent = message
		pre.style.margin = '0'
		pre.style.whiteSpace = 'pre-wrap'
		pre.style.fontSize = '0.9em'
		notification.appendChild(pre)
	} else {
		notification.textContent = message
	}

	// Добавляем кнопку закрытия
	const closeButton = document.createElement('span')
	closeButton.innerHTML = '×'
	closeButton.style.position = 'absolute'
	closeButton.style.top = '5px'
	closeButton.style.right = '10px'
	closeButton.style.cursor = 'pointer'
	closeButton.style.fontSize = '16px'
	closeButton.style.fontWeight = 'bold'
	closeButton.onclick = function () {
		notificationContainer.removeChild(notification)
	}

	notification.style.position = 'relative'
	notification.appendChild(closeButton)

	// Добавляем уведомление в контейнер
	notificationContainer.appendChild(notification)

	// Автоматически удаляем уведомление через указанное время
	if (duration > 0) {
		setTimeout(() => {
			if (notification.parentNode === notificationContainer) {
				notificationContainer.removeChild(notification)
			}
		}, duration)
	}
}

/**
 * Функция для форматирования даты и времени
 * @param {string} dateString - Строка с датой в формате ISO
 * @returns {string} - Отформатированная дата и время
 */
function formatDateTime(dateString) {
	if (!dateString) return 'Н/Д'

	try {
		// Если это ISO строка, преобразуем в более читаемый формат
		if (typeof dateString === 'string') {
			// Удаляем миллисекунды, если они есть
			dateString = dateString.split('.')[0]

			// Преобразуем формат даты
			const parts = dateString.split(' - ')
			if (parts.length > 0) {
				const datePart = parts[0]

				// Пробуем разные форматы даты
				let date
				if (datePart.includes('T')) {
					// ISO формат
					date = new Date(datePart)
				} else {
					// Формат логгера
					const [year, month, day, time] = datePart.split(/[-\s:]/)
					date = new Date(`${year}-${month}-${day}T${time}`)
				}

				if (!isNaN(date.getTime())) {
					return date.toLocaleString('ru-RU', {
						year: 'numeric',
						month: '2-digit',
						day: '2-digit',
						hour: '2-digit',
						minute: '2-digit',
						second: '2-digit',
					})
				}
			}
		}

		// Если не удалось преобразовать, возвращаем как есть
		return dateString
	} catch (e) {
		console.error('Ошибка форматирования даты:', e)
		return dateString
	}
}

/**
 * Функция для экранирования HTML
 * @param {string} text - Текст для экранирования
 * @returns {string} - Экранированный текст
 */
function escapeHtml(text) {
	if (!text) return ''

	return text
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		.replace(/"/g, '&quot;')
		.replace(/'/g, '&#039;')
}

/**
 * Функция для получения текущего времени в формате ЧЧ:ММ
 * @returns {string} - Текущее время
 */
function getCurrentTime() {
	const now = new Date()
	return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

/**
 * Функция для получения текстового описания типа сообщения
 * @param {string} type - Тип сообщения
 * @returns {string} - Текстовое описание
 */
function getMessageTypeText(type) {
	switch (type) {
		case 'user':
			return 'Вы'
		case 'assistant':
			return 'Ассистент'
		case 'system':
			return 'Система'
		case 'error':
			return 'Ошибка'
		default:
			return type
	}
}

/**
 * Функция для получения текстового описания статуса
 * @param {string} status - Статус
 * @returns {string} - Текстовое описание
 */
function getStatusText(status) {
	switch (status) {
		case 'completed':
			return 'Выполнено'
		case 'failed':
			return 'Ошибка'
		case 'interrupted':
			return 'Прервано'
		case 'in_progress':
			return 'Выполняется'
		case 'pending':
			return 'Ожидание'
		default:
			return status
	}
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
