/**
 * Функция для обновления истории команд
 */
function updateCommandHistory() {
	console.log('Обновление истории команд...')
	fetch('/api/history')
		.then((response) => response.json())
		.then((data) => {
			console.log('Получены данные истории:', data)
			const historyContainer = document.getElementById('history-list')
			if (!historyContainer) {
				console.error('Элемент #history-list не найден')
				return
			}

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
				row.className = `status-${entry.status === 'completed' ? 'success' : 'error'}`

				row.innerHTML = `
                    <td>${formatDateTime(entry.timestamp) || 'Н/Д'}</td>
                    <td>${escapeHtml(entry.command) || 'Н/Д'}</td>
                    <td>${entry.status || 'Н/Д'}</td>
                    <td>${entry.completion || 'Н/Д'}</td>
                    <td>${entry.accuracy || 'Н/Д'}</td>
                    <td>
                        <button class="view-details-btn" data-timestamp="${entry.timestamp}">
                            <span class="material-icons">info</span>
                        </button>
                        <button class="repeat-command-btn" data-command="${escapeHtml(
													entry.command
												)}">
                            <span class="material-icons">replay</span>
                        </button>
                    </td>
                `

				historyContainer.appendChild(row)
			})

			// Добавляем обработчики для кнопок
			document.querySelectorAll('.view-details-btn').forEach((btn) => {
				btn.addEventListener('click', function () {
					const timestamp = this.getAttribute('data-timestamp')
					showCommandDetails(timestamp)
				})
			})

			document.querySelectorAll('.repeat-command-btn').forEach((btn) => {
				btn.addEventListener('click', function () {
					const command = this.getAttribute('data-command')
					document.getElementById('user-input').value = command
					document.getElementById('query-form').dispatchEvent(new Event('submit'))
				})
			})
		})
		.catch((error) => {
			console.error('Ошибка при получении истории команд:', error)
			const historyContainer = document.getElementById('history-list')
			if (historyContainer) {
				historyContainer.innerHTML =
					'<tr><td colspan="6" class="error">Ошибка при получении истории команд</td></tr>'
			}
		})
}

/**
 * Функция для отображения подробностей команды
 * @param {string} timestamp - Временная метка команды
 */
function showCommandDetails(timestamp) {
	fetch(`/api/detailed_history/${timestamp}`)
		.then((response) => response.json())
		.then((data) => {
			const modal = document.getElementById('details-modal')
			const detailsContent = document.getElementById('command-details')

			if (data.error) {
				detailsContent.textContent = `Ошибка: ${data.error}`
			} else {
				detailsContent.textContent = data.details.join('\n')
			}

			// Показываем модальное окно
			modal.style.display = 'block'
		})
		.catch((error) => {
			console.error('Ошибка при получении подробностей команды:', error)
			showNotification('Ошибка при получении подробностей команды', 'error')
		})
}
