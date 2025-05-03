document.addEventListener('DOMContentLoaded', function () {
	// Элементы формы и результатов
	const queryForm = document.getElementById('query-form')
	const userInput = document.getElementById('user-input')
	const responseText = document.getElementById('response-text')
	const executionResult = document.getElementById('execution-result')
	const responseContainer = document.getElementById('response-container')
	const interruptBtn = document.getElementById('interrupt-btn')

	// Элементы истории
	const refreshHistoryBtn = document.getElementById('refresh-history')
	const clearHistoryDisplayBtn = document.getElementById('clear-history-display')
	const historyList = document.getElementById('history-list')

	// Элементы модальных окон
	const detailsModal = document.getElementById('details-modal')
	const closeModalBtns = document.querySelectorAll('.close-modal')
	const commandDetails = document.getElementById('command-details')

	// Элементы фильтрации команд
	const commandFilter = document.getElementById('command-filter')
	const commandCards = document.querySelectorAll('.command-card')

	// Переменная для отслеживания выполнения команды
	let commandInProgress = false

	// Инициализация интерфейса
	initUI()

	// Загружаем историю при загрузке страницы
	loadHistory()

	// Глобальные переменные для отслеживания состояния выполнения команды
	let commandExecutionInProgress = false
	let commandProgressInterval = null
	let commandProgressValue = 0

	// Получаем ссылки на элементы управления
	const commandControls = document.getElementById('command-controls')
	const interruptButton = document.getElementById('interrupt-command')
	const progressBar = document.getElementById('progress-bar-fill')
	const progressPercentage = document.getElementById('progress-percentage')

	// Функция для показа элементов управления командой
	function showCommandControls() {
		commandControls.style.display = 'flex'
		commandExecutionInProgress = true
		commandProgressValue = 0
		updateProgressBar(0)

		// Запускаем анимацию прогресса
		startProgressAnimation()
	}

	// Функция для скрытия элементов управления командой
	function hideCommandControls() {
		commandControls.style.display = 'none'
		commandExecutionInProgress = false

		// Останавливаем анимацию прогресса
		stopProgressAnimation()
	}

	// Функция для обновления индикатора прогресса
	function updateProgressBar(percentage) {
		progressBar.style.width = `${percentage}%`
		progressPercentage.textContent = `${percentage}%`
	}

	// Функция для анимации прогресса
	function startProgressAnimation() {
		// Останавливаем предыдущую анимацию, если она была
		stopProgressAnimation()

		// Запускаем новую анимацию
		commandProgressInterval = setInterval(() => {
			// Увеличиваем прогресс медленно, чтобы показать, что команда выполняется
			if (commandProgressValue < 90) {
				commandProgressValue += 0.5
				updateProgressBar(Math.round(commandProgressValue))
			}
		}, 100)
	}

	// Функция для остановки анимации прогресса
	function stopProgressAnimation() {
		if (commandProgressInterval) {
			clearInterval(commandProgressInterval)
			commandProgressInterval = null
		}
	}

	// Функция для прерывания выполнения команды
	function interruptCommand() {
		if (!commandExecutionInProgress) return

		// Показываем подтверждение
		if (confirm('Вы уверены, что хотите прервать выполнение текущей команды?')) {
			// Отправляем запрос на прерывание
			fetch('/interrupt_command', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
			})
				.then((response) => response.json())
				.then((data) => {
					console.log('Ответ на запрос прерывания:', data)

					// Показываем сообщение пользователю
					addMessage('Выполнение команды прервано пользователем', 'system')

					// Обновляем индикатор прогресса
					updateProgressBar(100)

					// Скрываем элементы управления через небольшую задержку
					setTimeout(hideCommandControls, 1500)
				})
				.catch((error) => {
					console.error('Ошибка при прерывании команды:', error)
					addMessage(`Ошибка при прерывании команды: ${error.message}`, 'error')
				})
		}
	}

	// Добавляем обработчик для кнопки прерывания
	interruptButton.addEventListener('click', interruptCommand)

	// Модифицируем функцию отправки запроса, чтобы показывать/скрывать элементы управления
	document.getElementById('query-form').addEventListener('submit', function (e) {
		e.preventDefault()

		const userInput = document.getElementById('user-input').value.trim()
		if (!userInput) return

		// Добавляем сообщение пользователя в чат
		addMessage(userInput, 'user')

		// Очищаем поле ввода
		document.getElementById('user-input').value = ''

		// Показываем элементы управления командой
		showCommandControls()

		// Отправляем запрос на сервер
		fetch('/query', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ input: userInput }),
		})
			.then((response) => response.json())
			.then((data) => {
				console.log('Ответ сервера:', data)

				// Добавляем ответ в чат
				addMessage(data.response, 'assistant')

				// Если есть результат выполнения, добавляем его
				if (data.execution_result) {
					addMessage(data.execution_result, 'system')
				}

				// Обновляем индикатор прогресса
				if (data.completion_percentage) {
					updateProgressBar(data.completion_percentage)
				} else {
					updateProgressBar(100) // Если нет данных о прогрессе, считаем выполненным
				}

				// Скрываем элементы управления через небольшую задержку
				setTimeout(hideCommandControls, 1500)

				// Обновляем историю команд
				loadHistory()
			})
			.catch((error) => {
				console.error('Ошибка при отправке запроса:', error)
				addMessage(`Ошибка при отправке запроса: ${error.message}`, 'error')

				// Скрываем элементы управления
				hideCommandControls()
			})
	})

	// Обработка клика по кнопке прерывания
	interruptBtn.addEventListener('click', function () {
		if (!commandInProgress) return

		// Отправляем запрос на прерывание
		fetch('/interrupt_command', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ interrupt: true }),
		})
			.then((response) => response.json())
			.then((data) => {
				// Отображаем сообщение о прерывании
				responseText.innerHTML += `<p style="color: #f57c00;">${data.message}</p>`
			})
			.catch((error) => {
				console.error('Ошибка при прерывании команды:', error)
			})
	})

	// Обработка клика по карточке команды
	commandCards.forEach((card) => {
		card.addEventListener('click', function () {
			const command = this.getAttribute('data-command')
			userInput.value = command
			userInput.focus()

			// Опционально: автоматически отправить форму
			queryForm.dispatchEvent(new Event('submit'))
		})
	})

	// Фильтрация команд
	commandFilter.addEventListener('input', function () {
		const filterText = this.value.toLowerCase()

		commandCards.forEach((card) => {
			const commandText = card.getAttribute('data-command').toLowerCase()
			const alternatives =
				card.querySelector('.command-alternatives')?.textContent.toLowerCase() || ''

			if (commandText.includes(filterText) || alternatives.includes(filterText)) {
				card.style.display = 'flex'
			} else {
				card.style.display = 'none'
			}
		})
	})

	// Закрытие модальных окон
	closeModalBtns.forEach((btn) => {
		btn.addEventListener('click', function () {
			detailsModal.style.display = 'none'
		})
	})

	// Закрытие модальных окон при клике вне содержимого
	window.addEventListener('click', function (e) {
		if (e.target === detailsModal) {
			detailsModal.style.display = 'none'
		}
	})

	// Обновление истории
	refreshHistoryBtn.addEventListener('click', loadHistory)

	// Очистка отображения истории
	clearHistoryDisplayBtn.addEventListener('click', function () {
		historyList.innerHTML = '<tr><td colspan="6" class="empty-history">История очищена</td></tr>'
	})

	// Добавляем обработчики для кнопок управления историей
	const backupHistoryBtn = document.getElementById('backup-history')
	const clearHistoryBtn = document.getElementById('clear-history')

	// Создание резервной копии истории
	backupHistoryBtn.addEventListener('click', function () {
		if (confirm('Создать резервную копию истории команд?')) {
			fetch('/clear_history', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ backup_only: true }),
			})
				.then((response) => response.json())
				.then((data) => {
					if (data.status === 'success') {
						alert(`${data.message} (${data.backup_timestamp})`)
						loadHistory() // Обновляем отображение истории
					} else {
						alert(`Ошибка: ${data.error}`)
					}
				})
				.catch((error) => {
					alert(`Ошибка: ${error.message}`)
				})
		}
	})

	// Полная очистка истории
	clearHistoryBtn.addEventListener('click', function () {
		if (
			confirm(
				'Вы уверены, что хотите полностью очистить историю команд? Это действие нельзя отменить.'
			)
		) {
			fetch('/clear_history', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ backup_only: false }),
			})
				.then((response) => response.json())
				.then((data) => {
					if (data.status === 'success') {
						alert(data.message)
						loadHistory() // Обновляем отображение истории
					} else {
						alert(`Ошибка: ${data.error}`)
					}
				})
				.catch((error) => {
					alert(`Ошибка: ${error.message}`)
				})
		}
	})

	// Функция загрузки истории
	function loadHistory() {
		// Показываем индикатор загрузки
		historyList.innerHTML =
			'<tr><td colspan="6" class="empty-history">История загружается...</td></tr>'

		fetch('/history')
			.then((response) => {
				if (!response.ok) {
					throw new Error(`HTTP error! Status: ${response.status}`)
				}
				return response.json()
			})
			.then((data) => {
				console.log('Получены данные истории:', data) // Отладочный вывод

				if (data.error) {
					historyList.innerHTML = `<tr><td colspan="6" class="empty-history">Ошибка: ${data.error}</td></tr>`
					return
				}

				if (!data.history || data.history.length === 0) {
					historyList.innerHTML =
						'<tr><td colspan="6" class="empty-history">История пуста</td></tr>'
					return
				}

				// Очищаем текущую историю
				historyList.innerHTML = ''

				// Добавляем записи истории
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
						<td>${formatTimestamp(entry.timestamp)}</td>
						<td>${entry.command || 'Н/Д'}</td>
						<td class="${statusClass}">${entry.status || 'Н/Д'}</td>
						<td>${entry.completion || 'Н/Д'}</td>
						<td>${entry.accuracy || 'Н/Д'}</td>
						<td>
							<button class="history-action-btn view-details" data-timestamp="${entry.timestamp}">
								<span class="material-icons" style="font-size: 14px; margin-right: 2px;">info</span> Подробности
							</button>
							<button class="history-action-btn repeat-command" data-command="${entry.command}">
								<span class="material-icons" style="font-size: 14px; margin-right: 2px;">replay</span> Повторить
							</button>
						</td>
					`

					historyList.appendChild(row)
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
				console.error('Ошибка при загрузке истории:', error) // Отладочный вывод
				historyList.innerHTML = `<tr><td colspan="6" class="empty-history">Ошибка загрузки истории: ${error.message}</td></tr>`
			})
	}

	// Функция отображения подробной информации о команде
	function showCommandDetails(timestamp) {
		commandDetails.textContent = 'Загрузка подробностей...'
		detailsModal.style.display = 'block'

		fetch(`/detailed_history/${timestamp}`)
			.then((response) => response.json())
			.then((data) => {
				if (data.error) {
					commandDetails.textContent = `Ошибка: ${data.error}`
				} else {
					commandDetails.textContent = data.details.join('\n')
				}
			})
			.catch((error) => {
				commandDetails.textContent = `Ошибка загрузки подробностей: ${error.message}`
			})
	}

	// Функция форматирования временной метки
	function formatTimestamp(timestamp) {
		if (!timestamp) return 'Н/Д'

		try {
			// Если это ISO строка, преобразуем в более читаемый формат
			if (typeof timestamp === 'string') {
				// Удаляем миллисекунды, если они есть
				timestamp = timestamp.split('.')[0]

				// Преобразуем формат даты
				const parts = timestamp.split(' - ')
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
			return timestamp
		} catch (e) {
			console.error('Ошибка форматирования даты:', e)
			return timestamp
		}
	}

	// Функция для отображения прогресса выполнения составной команды
	function displayCompoundCommandProgress(data) {
		// Создаем контейнер для информации о шагах
		const stepsContainer = document.createElement('div')
		stepsContainer.className = 'steps-container'

		// Добавляем заголовок
		const stepsHeader = document.createElement('div')
		stepsHeader.className = 'steps-header'
		stepsHeader.innerHTML = `
			<h4>Выполнение команды (${data.completion_percentage.toFixed(1)}% завершено)</h4>
			<div class="progress-bar">
				<div class="progress-bar-fill" style="width: ${data.completion_percentage}%;"></div>
			</div>
		`
		stepsContainer.appendChild(stepsHeader)

		// Добавляем информацию о каждом шаге
		const stepsList = document.createElement('div')
		stepsList.className = 'steps-list'

		data.steps.forEach((step) => {
			const stepItem = document.createElement('div')
			stepItem.className = `step-item step-${step.status}`

			// Определяем иконку для статуса
			let statusIcon = ''
			if (step.status === 'completed') {
				statusIcon = '<span class="material-icons step-icon">check_circle</span>'
			} else if (step.status === 'failed') {
				statusIcon = '<span class="material-icons step-icon">error</span>'
			} else if (step.status === 'interrupted') {
				statusIcon = '<span class="material-icons step-icon">stop_circle</span>'
			} else if (step.status === 'in_progress') {
				statusIcon = '<span class="material-icons step-icon">hourglass_top</span>'
			} else {
				statusIcon = '<span class="material-icons step-icon">pending</span>'
			}

			// Формируем содержимое элемента шага
			stepItem.innerHTML = `
				<div class="step-header">
					${statusIcon}
					<span class="step-number">Шаг ${step.number}:</span>
					<span class="step-description">${step.description}</span>
				</div>
				<div class="step-details">
					${step.result ? `<div class="step-result">${step.result}</div>` : ''}
					${step.error ? `<div class="step-error">${step.error}</div>` : ''}
				</div>
			`

			stepsList.appendChild(stepItem)
		})

		stepsContainer.appendChild(stepsList)

		// Добавляем итоговую информацию
		const stepsFooter = document.createElement('div')
		stepsFooter.className = 'steps-footer'
		stepsFooter.innerHTML = `
			<div class="steps-stats">
				<div class="stat-item">
					<span class="stat-label">Статус:</span>
					<span class="stat-value status-${data.overall_status}">${getStatusText(data.overall_status)}</span>
				</div>
				<div class="stat-item">
					<span class="stat-label">Выполнение:</span>
					<span class="stat-value">${data.completion_percentage.toFixed(1)}%</span>
				</div>
				<div class="stat-item">
					<span class="stat-label">Точность:</span>
					<span class="stat-value">${data.accuracy_percentage.toFixed(1)}%</span>
				</div>
			</div>
		`
		stepsContainer.appendChild(stepsFooter)

		return stepsContainer
	}

	// Функция для получения текстового описания статуса
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

	// Модифицируем функцию добавления сообщения, чтобы поддерживать отображение составных команд
	function addMessage(message, type, data = null) {
		const messagesContainer = document.getElementById('messages')
		const messageElement = document.createElement('div')
		messageElement.className = `message ${type}-message`

		// Определяем иконку для типа сообщения
		let iconHtml = ''
		if (type === 'user') {
			iconHtml = '<span class="material-icons message-icon">person</span>'
		} else if (type === 'assistant') {
			iconHtml = '<span class="material-icons message-icon">smart_toy</span>'
		} else if (type === 'system') {
			iconHtml = '<span class="material-icons message-icon">info</span>'
		} else if (type === 'error') {
			iconHtml = '<span class="material-icons message-icon">error</span>'
		}

		// Создаем содержимое сообщения
		const messageContent = document.createElement('div')
		messageContent.className = 'message-content'

		// Если это составная команда, отображаем прогресс выполнения
		if (type === 'assistant' && data && data.is_compound) {
			messageContent.innerHTML = `<p>${message}</p>`
			messageContent.appendChild(displayCompoundCommandProgress(data))
		} else {
			messageContent.innerHTML = `<p>${message}</p>`
		}

		// Собираем сообщение
		messageElement.innerHTML = `
			<div class="message-header">
				${iconHtml}
				<span class="message-type">${getMessageTypeText(type)}</span>
				<span class="message-time">${getCurrentTime()}</span>
			</div>
		`
		messageElement.appendChild(messageContent)

		// Добавляем сообщение в контейнер
		messagesContainer.appendChild(messageElement)

		// Прокручиваем к новому сообщению
		messageElement.scrollIntoView({ behavior: 'smooth' })
	}

	// Функция для получения текстового описания типа сообщения
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

	// Функция для получения текущего времени
	function getCurrentTime() {
		const now = new Date()
		return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
	}

	// Инициализация интерфейса
	function initUI() {
		// Скрываем контейнер ответа до первого запроса
		responseContainer.style.display = 'none'

		// Фокус на поле ввода при загрузке страницы
		userInput.focus()
	}
})
