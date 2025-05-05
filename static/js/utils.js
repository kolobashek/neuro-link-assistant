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
		const date = new Date(dateString)
		return date.toLocaleString('ru-RU', {
			day: '2-digit',
			month: '2-digit',
			year: 'numeric',
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit',
		})
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
