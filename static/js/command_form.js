/**
 * Функции для работы с формой ввода команд
 */

/**
 * Функция для инициализации автодополнения команд
 */
function initCommandAutocomplete() {
	const userInput = document.getElementById('user-input')
	const commandItems = document.querySelectorAll('.command-item')

	if (!userInput || !commandItems.length) return

	// Получаем список доступных команд
	const availableCommands = Array.from(commandItems)
		.map((item) => {
			const mainCommand = item.querySelector('.command-main').textContent
			const alternativesElement = item.querySelector('.command-alternatives')

			let alternatives = []
			if (alternativesElement) {
				const altText = alternativesElement.textContent.replace('Также:', '').trim()
				alternatives = altText.split(',').map((alt) => alt.trim())
			}

			return [mainCommand, ...alternatives]
		})
		.flat()

	// Добавляем обработчик ввода
	userInput.addEventListener('input', function () {
		const inputValue = this.value.toLowerCase()

		// Если ввод пустой, не показываем подсказки
		if (!inputValue) return

		// Ищем подходящие команды
		const matchingCommands = availableCommands.filter((cmd) =>
			cmd.toLowerCase().includes(inputValue)
		)

		// Если есть подходящие команды, показываем первую как подсказку
		if (matchingCommands.length > 0) {
			const suggestion = matchingCommands[0]

			// Создаем элемент подсказки, если его еще нет
			let suggestionElement = document.getElementById('command-suggestion')
			if (!suggestionElement) {
				suggestionElement = document.createElement('div')
				suggestionElement.id = 'command-suggestion'
				suggestionElement.style.position = 'absolute'
				suggestionElement.style.color = '#999'
				suggestionElement.style.pointerEvents = 'none'
				suggestionElement.style.whiteSpace = 'nowrap'
				suggestionElement.style.overflow = 'hidden'

				// Вставляем элемент подсказки после поля ввода
				userInput.parentNode.insertBefore(suggestionElement, userInput.nextSibling)
			}

			// Позиционируем подсказку
			suggestionElement.style.left = userInput.offsetLeft + 'px'
			suggestionElement.style.top = userInput.offsetTop + 'px'
			suggestionElement.style.width = userInput.offsetWidth + 'px'
			suggestionElement.style.height = userInput.offsetHeight + 'px'
			suggestionElement.style.lineHeight = userInput.offsetHeight + 'px'
			suggestionElement.style.paddingLeft = window.getComputedStyle(userInput).paddingLeft

			// Устанавливаем текст подсказки
			suggestionElement.textContent = suggestion

			// Показываем подсказку
			suggestionElement.style.display = 'block'
		} else {
			// Если нет подходящих команд, скрываем подсказку
			const suggestionElement = document.getElementById('command-suggestion')
			if (suggestionElement) {
				suggestionElement.style.display = 'none'
			}
		}
	})

	// Добавляем обработчик нажатия клавиш
	userInput.addEventListener('keydown', function (e) {
		const suggestionElement = document.getElementById('command-suggestion')

		// Если нажата клавиша Tab и есть подсказка, используем её
		if (e.key === 'Tab' && suggestionElement && suggestionElement.style.display !== 'none') {
			e.preventDefault()
			this.value = suggestionElement.textContent
			suggestionElement.style.display = 'none'
		}
	})

	// Скрываем подсказку при потере фокуса
	userInput.addEventListener('blur', function () {
		const suggestionElement = document.getElementById('command-suggestion')
		if (suggestionElement) {
			suggestionElement.style.display = 'none'
		}
	})
}

/**
 * Функция для отображения прогресса выполнения составной команды
 * @param {Object} data - Данные о выполнении команды
 * @returns {HTMLElement} - Элемент с информацией о прогрессе
 */
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

/**
 * Функция для добавления сообщения в чат
 * @param {string} message - Текст сообщения
 * @param {string} type - Тип сообщения (user, assistant, system, error)
 * @param {Object} data - Дополнительные данные (для составных команд)
 */
function addMessage(message, type, data = null) {
	const messagesContainer = document.getElementById('messages')
	if (!messagesContainer) {
		console.error('Элемент #messages не найден')
		return
	}

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

/**
 * Функция для обработки отправки формы команды
 * @param {Event} e - Событие отправки формы
 */
function handleCommandSubmit(e) {
	e.preventDefault()

	const userInput = document.getElementById('user-input')
	if (!userInput) {
		console.error('Элемент #user-input не найден')
		return
	}

	const input = userInput.value.trim()
	if (!input) return

	// Добавляем сообщение пользователя в чат
	addMessage(input, 'user')

	// Очищаем поле ввода
	userInput.value = ''

	// Показываем элементы управления командой
	showCommandControls()

	// Отправляем запрос на сервер
	fetch('/api/query', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({ input: input }),
	})
		.then((response) => {
			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`)
			}
			return response.json()
		})
		.then((data) => {
			console.log('Ответ сервера:', data)

			// Добавляем ответ в чат
			if (data.is_compound) {
				// Если это составная команда
				addMessage(data.response, 'assistant', data)
			} else {
				// Если это простая команда
				addMessage(data.response, 'assistant')

				// Если есть результат выполнения, добавляем его
				if (data.execution_result) {
					addMessage(data.execution_result, 'system')
				}
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
			if (window.historyModule && window.historyModule.updateCommandHistory) {
				window.historyModule.updateCommandHistory()
			}
		})
		.catch((error) => {
			console.error('Ошибка при отправке запроса:', error)
			addMessage(`Ошибка при отправке запроса: ${error.message}`, 'error')

			// Скрываем элементы управления
			hideCommandControls()
		})
}

/**
 * Инициализация обработчиков событий для формы команд
 */
function initCommandFormHandlers() {
	// Инициализация автодополнения
	initCommandAutocomplete()

	// Обработчик отправки формы
	const queryForm = document.getElementById('query-form')
	if (queryForm) {
		queryForm.addEventListener('submit', handleCommandSubmit)
	}

	// Обработчик клика по карточке команды
	const commandCards = document.querySelectorAll('.command-card')
	commandCards.forEach((card) => {
		card.addEventListener('click', function () {
			const command = this.getAttribute('data-command')
			const userInput = document.getElementById('user-input')
			if (userInput) {
				userInput.value = command
				userInput.focus()

				// Опционально: автоматически отправить форму
				const queryForm = document.getElementById('query-form')
				if (queryForm) {
					queryForm.dispatchEvent(new Event('submit'))
				}
			}
		})
	})

	// Фильтрация команд
	const commandFilter = document.getElementById('command-filter')
	if (commandFilter) {
		commandFilter.addEventListener('input', function () {
			const filterText = this.value.toLowerCase()
			const commandCards = document.querySelectorAll('.command-card')

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
	}
}

// Экспортируем функции для использования в других модулях
window.commandFormModule = {
	initCommandAutocomplete,
	displayCompoundCommandProgress,
	addMessage,
	handleCommandSubmit,
	initCommandFormHandlers,
}
