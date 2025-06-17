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
 * Функция для форматирования логов в HTML
 * @param {Array} logLines - Массив строк лога
 * @returns {string} - Отформатированный HTML
 */
function formatLogLines(logLines) {
	if (!logLines || logLines.length === 0) {
		return '<div class="empty-log">Нет данных для отображения</div>'
	}

	let html = ''
	let inStepSection = false
	let currentStepHtml = ''

	logLines.forEach((line) => {
		// Пропускаем пустые строки
		if (!line.trim()) return

		// Обрабатываем заголовок лога
		if (line.includes('Детальное выполнение команды')) {
			html += `<div class="log-entry">`
			const parts = line.split(' - ')
			if (parts.length > 1) {
				html += `<div class="log-timestamp">${parts[0]}</div>`
				html += `<div class="log-title">${parts[1]}</div>`
			} else {
				html += `<div class="log-title">${line}</div>`
			}
			return
		}

		// Обрабатываем команду
		if (line.startsWith('Команда:')) {
			const command = line.replace('Команда:', '').trim()
			html += `<div class="log-command">${command}</div>`
			return
		}

		// Обрабатываем время начала и окончания
		if (line.startsWith('Время начала:') || line.startsWith('Время окончания:')) {
			const parts = line.split(':')
			const label = parts[0] + ':'
			const value = parts.slice(1).join(':').trim()
			html += `<div class="log-time"><span class="log-label">${label}</span> ${value}</div>`
			return
		}

		// Обрабатываем статус
		if (line.startsWith('Статус:')) {
			const status = line.replace('Статус:', '').trim().toLowerCase()
			const statusClass = status.includes('completed')
				? 'completed'
				: status.includes('failed')
				? 'failed'
				: status.includes('interrupted')
				? 'interrupted'
				: 'in-progress'

			html += `<div class="log-status ${statusClass}">${line}</div>`
			return
		}

		// Обрабатываем проценты выполнения и точности
		if (line.startsWith('Выполнение:') || line.startsWith('Точность:')) {
			html += `<div class="log-percentage">${line}</div>`
			return
		}

		// Обрабатываем начало секции шагов
		if (line === 'Шаги выполнения:') {
			html += `<div class="log-steps-title">${line}</div>`
			html += `<div class="log-steps">`
			inStepSection = true
			return
		}

		// Обрабатываем шаги
		if (inStepSection) {
			// Начало нового шага
			if (line.trim().startsWith('Шаг ')) {
				// Если у нас уже есть данные о текущем шаге, добавляем их
				if (currentStepHtml) {
					html += `<div class="log-step">${currentStepHtml}</div>`
					currentStepHtml = ''
				}

				currentStepHtml = `<div class="log-step-header">${line.trim()}</div>`
				currentStepHtml += `<div class="log-step-details">`
				return
			}

			// Обрабатываем содержимое шага
			if (currentStepHtml) {
				// Конец шага
				if (line.trim() === '---') {
					currentStepHtml += `</div>`
					html += `<div class="log-step">${currentStepHtml}</div>`
					currentStepHtml = ''
					return
				}

				// Обрабатываем статус шага
				if (line.trim().startsWith('Статус:')) {
					const status = line.replace('Статус:', '').trim().toLowerCase()
					const statusClass = status.includes('completed')
						? 'completed'
						: status.includes('failed')
						? 'failed'
						: status.includes('interrupted')
						? 'interrupted'
						: 'in-progress'

					currentStepHtml += `<div class="log-status ${statusClass}">${line.trim()}</div>`
					return
				}

				// Обрабатываем результат шага
				if (line.trim().startsWith('Результат:')) {
					currentStepHtml += `<div class="log-result">${line.trim()}</div>`
					return
				}

				// Обрабатываем ошибку шага
				if (line.trim().startsWith('Ошибка:')) {
					currentStepHtml += `<div class="log-error">${line.trim()}</div>`
					return
				}

				// Другие строки шага
				currentStepHtml += `<div>${line.trim()}</div>`
				return
			}
		}

		// Обрабатываем разделитель
		if (line.startsWith('-'.repeat(10))) {
			// Если мы были в секции шагов, закрываем её
			if (inStepSection) {
				// Добавляем последний шаг, если он есть
				if (currentStepHtml) {
					html += `<div class="log-step">${currentStepHtml}</div>`
					currentStepHtml = ''
				}
				html += `</div>` // Закрываем .log-steps
				inStepSection = false
			}

			html += `<div class="log-divider"></div>`
			html += `</div>` // Закрываем .log-entry
			return
		}

		// Другие строки
		html += `<div>${line}</div>`
	})

	// Если остался незакрытый шаг или секция
	if (inStepSection) {
		if (currentStepHtml) {
			html += `<div class="log-step">${currentStepHtml}</div>`
		}
		html += `</div>` // Закрываем .log-steps
	}

	return html
}

/**
 * Функция для отображения подробностей команды
 * @param {string} timestamp - Временная метка команды
 */
function showCommandDetails(timestamp) {
	// Показываем индикатор загрузки в модальном окне
	const modal = document.getElementById('details-modal')
	const detailsContent = document.getElementById('command-details')

	if (!modal || !detailsContent) {
		console.error('Элементы модального окна не найдены')
		return
	}

	detailsContent.innerHTML = '<div class="loading">Загрузка подробностей...</div>'
	modal.style.display = 'block'

	fetch(`/api/detailed_history/${timestamp}`)
		.then((response) => response.json())
		.then((data) => {
			if (data.error) {
				detailsContent.innerHTML = `<div class="error">${data.error}</div>`
			} else if (!data.details || data.details.length === 0) {
				detailsContent.innerHTML =
					'<div class="empty-log">Подробная информация о команде не найдена</div>'
			} else {
				// Форматируем детальную информацию
				detailsContent.innerHTML = formatLogLines(data.details)
			}
		})
		.catch((error) => {
			console.error('Ошибка при получении подробностей команды:', error)
			detailsContent.innerHTML = `<div class="error">Ошибка при получении подробностей команды: ${error.message}</div>`
		})
}

/**
 * Функция для экспорта логов в файл
 * @param {string} type - Тип логов (history, detailed)
 */
function exportLogs(type) {
	// Показываем уведомление о начале экспорта
	showNotification('Подготовка логов для экспорта...', 'info')

	// Определяем URL в зависимости от типа логов
	const url = type === 'detailed' ? '/api/export_detailed_logs' : '/api/export_history_logs'

	fetch(url)
		.then((response) => {
			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`)
			}
			return response.blob()
		})
		.then((blob) => {
			// Создаем ссылку для скачивания
			const url = window.URL.createObjectURL(blob)
			const a = document.createElement('a')
			a.style.display = 'none'
			a.href = url

			// Определяем имя файла
			const date = new Date().toISOString().replace(/[:.]/g, '-')
			a.download = type === 'detailed' ? `detailed_logs_${date}.txt` : `command_history_${date}.txt`

			// Добавляем ссылку в DOM, кликаем по ней и удаляем
			document.body.appendChild(a)
			a.click()
			window.URL.revokeObjectURL(url)
			document.body.removeChild(a)

			showNotification('Логи успешно экспортированы', 'success')
		})
		.catch((error) => {
			console.error('Ошибка при экспорте логов:', error)
			showNotification(`Ошибка при экспорте логов: ${error.message}`, 'error')
		})
}

/**
 * Функция для очистки истории команд
 * @param {boolean} backupOnly - Только создать резервную копию без очистки
 */
function clearHistory(backupOnly = false) {
	const action = backupOnly ? 'создать резервную копию' : 'очистить'
	const confirmMessage = backupOnly
		? 'Создать резервную копию истории команд?'
		: 'Вы уверены, что хотите полностью очистить историю команд? Это действие нельзя отменить.'

	if (confirm(confirmMessage)) {
		// Показываем уведомление о начале процесса
		showNotification(`Выполняется запрос: ${action} историю команд...`, 'info')

		fetch('/api/clear_history', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ backup_only: backupOnly }),
		})
			.then((response) => response.json())
			.then((data) => {
				if (data.status === 'success') {
					showNotification(data.message, 'success')

					// Если это была полная очистка, обновляем отображение истории
					if (!backupOnly) {
						updateCommandHistory()
					}
				} else {
					showNotification(`Ошибка: ${data.error}`, 'error')
				}
			})
			.catch((error) => {
				console.error(`Ошибка при выполнении операции: ${action} историю`, error)
				showNotification(`Ошибка: ${error.message}`, 'error')
			})
	}
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

// Добавляем обработчики для кнопок экспорта
document.addEventListener('DOMContentLoaded', function () {
	// Кнопка экспорта истории
	const exportHistoryBtn = document.getElementById('export-history')
	if (exportHistoryBtn) {
		exportHistoryBtn.addEventListener('click', function () {
			exportLogs('history')
		})
	}

	// Добавляем кнопку экспорта детальных логов в модальное окно
	const detailsModal = document.getElementById('details-modal')
	if (detailsModal) {
		const modalFooter = detailsModal.querySelector('.modal-footer')
		if (modalFooter) {
			// Проверяем, не добавлена ли уже кнопка
			if (!modalFooter.querySelector('#export-detailed')) {
				const exportBtn = document.createElement('button')
				exportBtn.id = 'export-detailed'
				exportBtn.className = 'btn'
				exportBtn.innerHTML = '<span class="material-icons">download</span> Экспорт логов'
				exportBtn.addEventListener('click', function () {
					exportLogs('detailed')
				})

				// Вставляем кнопку перед кнопкой закрытия
				modalFooter.insertBefore(exportBtn, modalFooter.firstChild)
			}
		}
	}
})

// Добавляем обработчики для кнопок управления историей
document.addEventListener('DOMContentLoaded', function () {
	// Кнопка обновления истории
	const refreshHistoryBtn = document.getElementById('refresh-history')
	if (refreshHistoryBtn) {
		refreshHistoryBtn.addEventListener('click', updateCommandHistory)
	}

	// Кнопка очистки отображения истории
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

	// Кнопка создания резервной копии истории
	const backupHistoryBtn = document.getElementById('backup-history')
	if (backupHistoryBtn) {
		backupHistoryBtn.addEventListener('click', function () {
			clearHistory(true) // true = только резервная копия
		})
	}

	// Кнопка полной очистки истории
	const clearHistoryBtn = document.getElementById('clear-history')
	if (clearHistoryBtn) {
		clearHistoryBtn.addEventListener('click', function () {
			clearHistory(false) // false = полная очистка
		})
	}
})

// Экспортируем функции для использования в других модулях
window.historyModule = {
	updateCommandHistory,
	showCommandDetails,
	initHistoryHandlers,
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 History.js загружен');
    console.log('🔍 Current URL:', window.location.href);

    // Обработчик клика по элементам истории
    function attachHistoryClickHandlers() {
        const historyItems = document.querySelectorAll('.history-item');
        console.log(`🔍 Найдено элементов истории: ${historyItems.length}`);

        historyItems.forEach((item, index) => {
            // Удаляем предыдущий обработчик если есть
            item.removeEventListener('click', handleHistoryClick);

            // Добавляем новый обработчик
            item.addEventListener('click', handleHistoryClick);
            item.style.cursor = 'pointer'; // Показываем что элемент кликабельный

            const historyId = item.getAttribute('data-history-id');
            console.log(`✅ Обработчик добавлен к элементу ${index}: ${historyId}`);
        });
    }

    function handleHistoryClick(event) {
        console.log('🔍 Клик по элементу истории');
        console.log('🔍 Event target:', event.target);
        console.log('🔍 Current element:', this);

        // Предотвращаем всплытие если клик по кнопке
        if (event.target.tagName === 'BUTTON') {
            console.log('🔍 Клик по кнопке, игнорируем');
            return;
        }

        const historyId = this.getAttribute('data-history-id');
        console.log(`🔍 History ID: ${historyId}`);

        if (historyId) {
            const newUrl = `/history/${historyId}`;
            console.log(`🔍 Переход к: ${newUrl}`);
            // Переход к детальной странице истории
            window.location.href = newUrl;
        } else {
            console.warn('⚠️ Не найден data-history-id для элемента');
        }
    }

    // Запускаем при загрузке
    attachHistoryClickHandlers();

    // Переподключаем обработчики при обновлении истории
    document.addEventListener('historyUpdated', function() {
        console.log('🔄 История обновлена, переподключаем обработчики');
        attachHistoryClickHandlers();
    });
});
