/**
 * Функции для работы с историей команд
 */

/**
 * Функция для обновления истории команд
 */
function updateCommandHistory() {
	console.log('Обновление истории команд...')

	// Показываем индикатор загрузки
	const historyContainer = document.getElementById('history-list')
	if (!historyContainer) {
		console.error('Элемент #history-list не найден')
		return
	}

	historyContainer.innerHTML =
		'<tr><td colspan="6" class="empty-history">История загружается...</td></tr>'

	fetch('/api/history')
		.then((response) => {
			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`)
			}
			return response.json()
		})
		.then((data) => {
			console.log('Получены данные истории:', data)

			if (data.error) {
				historyContainer.innerHTML = `<tr><td colspan="6" class="error">${data.error}</td></tr>`
				return
			}

			if (!data.history || data.history.length === 0) {
				historyContainer.innerHTML =
					'<tr><td colspan="6" class="empty-history">История команд пуста</td></tr>'
				return
			}

			// Очищаем таблицу
			historyContainer.innerHTML = ''

			// Добавляем записи
			data.history.forEach((entry) => {
				const row = document.createElement('tr')
				row.className = 'history-row'

				// Определяем класс для статуса
				const statusClass = entry.status?.includes('completed')
					? 'status-completed'
					: entry.status?.includes('failed')
					? 'status-failed'
					: entry.status?.includes('interrupted')
					? 'status-interrupted'
					: 'status-in-progress'

				row.innerHTML = `
					<td>${formatDateTime(entry.timestamp)}</td>
					<td>${escapeHtml(entry.command) || 'Н/Д'}</td>
					<td class="${statusClass}">${entry.status || 'Н/Д'}</td>
					<td>${entry.completion || 'Н/Д'}</td>
					<td>${entry.accuracy || 'Н/Д'}</td>
					<td>
						<button class="history-action-btn view-details" data-timestamp="${entry.timestamp}">
							<span class="material-icons" style="font-size: 14px; margin-right: 2px;">info</span> Подробности
						</button>
						<button class="history-action-btn repeat-command" data-command="${escapeHtml(entry.command)}">
							<span class="material-icons" style="font-size: 14px; margin-right: 2px;">replay</span> Повторить
						</button>
					</td>
				`

				historyContainer.appendChild(row)
			})

			// Добавляем обработчики для кнопок
			document.querySelectorAll('.view-details').forEach((btn) => {
				btn.addEventListener('click', function () {
					const timestamp = this.getAttribute('data-timestamp')
					showCommandDetails(timestamp)
				})
			})

			document.querySelectorAll('.repeat-command').forEach((btn) => {
				btn.addEventListener('click', function () {
					const command = this.getAttribute('data-command')
					document.getElementById('user-input').value = command
					document.getElementById('query-form').dispatchEvent(new Event('submit'))
				})
			})
		})
		.catch((error) => {
			console.error('Ошибка при загрузке истории:', error)
			historyContainer.innerHTML = `<tr><td colspan="6" class="empty-history">Ошибка загрузки истории: ${error.message}</td></tr>`
		})
}

/**
 * Функция для отображения подробностей команды
 * @param {string} timestamp - Временная метка команды
 */
function showCommandDetails(timestamp) {
	const modal = document.getElementById('details-modal')
	const detailsContent = document.getElementById('command-details')

	if (!modal || !detailsContent) {
		console.error('Элементы модального окна не найдены')
		return
	}

	detailsContent.textContent = 'Загрузка подробностей...'
	modal.style.display = 'block'

	fetch(`/api/detailed_history/${timestamp}`)
		.then((response) => {
			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`)
			}

			// Проверка типа контента
			const contentType = response.headers.get('content-type')
			if (!contentType || !contentType.includes('application/json')) {
				throw new Error('Получен неверный формат данных (не JSON)')
			}

			return response.json()
		})
		.then((data) => {
			if (data.error) {
				detailsContent.textContent = `Ошибка: ${data.error}`
			} else if (data.details && data.details.length > 0) {
				detailsContent.textContent = data.details.join('\n')
			} else {
				detailsContent.textContent = 'Подробная информация отсутствует'
			}
		})
		.catch((error) => {
			console.error('Ошибка при получении подробностей команды:', error)
			detailsContent.textContent = `Ошибка загрузки подробностей: ${error.message}`
		})
}

/**
 * Инициализация обработчиков событий для истории
 */
function initHistoryHandlers() {
	// Обновление истории
	const refreshHistoryBtn = document.getElementById('refresh-history')
	if (refreshHistoryBtn) {
		refreshHistoryBtn.addEventListener('click', updateCommandHistory)
	}

	// Очистка отображения истории
	const clearHistoryDisplayBtn = document.getElementById('clear-history-display')
	if (clearHistoryDisplayBtn) {
		clearHistoryDisplayBtn.addEventListener('click', function () {
			const historyList = document.getElementById('history-list')
			if (historyList) {
				historyList.innerHTML =
					'<tr><td colspan="6" class="empty-history">История очищена</td></tr>'
			}
		})
	}

	// Создание резервной копии истории
	const backupHistoryBtn = document.getElementById('backup-history')
	if (backupHistoryBtn) {
		backupHistoryBtn.addEventListener('click', function () {
			if (confirm('Создать резервную копию истории команд?')) {
				fetch('/api/clear_history', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify({ backup_only: true }),
				})
					.then((response) => response.json())
					.then((data) => {
						if (data.status === 'success') {
							showNotification(`${data.message} (${data.backup_timestamp})`, 'success')
							updateCommandHistory() // Обновляем отображение истории
						} else {
							showNotification(`Ошибка: ${data.error}`, 'error')
						}
					})
					.catch((error) => {
						showNotification(`Ошибка: ${error.message}`, 'error')
					})
			}
		})
	}

	// Полная очистка истории
	const clearHistoryBtn = document.getElementById('clear-history')
	if (clearHistoryBtn) {
		clearHistoryBtn.addEventListener('click', function () {
			if (
				confirm(
					'Вы уверены, что хотите полностью очистить историю команд? Это действие нельзя отменить.'
				)
			) {
				fetch('/api/clear_history', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify({ backup_only: false }),
				})
					.then((response) => response.json())
					.then((data) => {
						if (data.status === 'success') {
							showNotification(data.message, 'success')
							updateCommandHistory() // Обновляем отображение истории
						} else {
							showNotification(`Ошибка: ${data.error}`, 'error')
						}
					})
					.catch((error) => {
						showNotification(`Ошибка: ${error.message}`, 'error')
					})
			}
		})
	}

	// Закрытие модальных окон
	const closeModalBtns = document.querySelectorAll('.close-modal')
	closeModalBtns.forEach((btn) => {
		btn.addEventListener('click', function () {
			const detailsModal = document.getElementById('details-modal')
			if (detailsModal) {
				detailsModal.style.display = 'none'
			}
		})
	})

	// Закрытие модальных окон при клике вне содержимого
	window.addEventListener('click', function (e) {
		const detailsModal = document.getElementById('details-modal')
		if (e.target === detailsModal) {
			detailsModal.style.display = 'none'
		}
	})
}

// Экспортируем функции для использования в других модулях
window.historyModule = {
	updateCommandHistory,
	showCommandDetails,
	initHistoryHandlers,
}
