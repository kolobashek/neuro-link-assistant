document.addEventListener('DOMContentLoaded', function () {
	// Элементы формы и результатов
	const queryForm = document.getElementById('query-form')
	const userInput = document.getElementById('user-input')
	const responseText = document.getElementById('response-text')
	const executionResult = document.getElementById('execution-result')
	const responseContainer = document.getElementById('response-container')

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

	// Инициализация интерфейса
	initUI()

	// Загружаем историю при загрузке страницы
	loadHistory()

	// Обработка отправки формы
	queryForm.addEventListener('submit', function (e) {
		e.preventDefault()

		const input = userInput.value.trim()
		if (!input) return

		// Показываем область результатов
		responseContainer.style.display = 'block'

		// Очищаем предыдущий ответ
		responseText.innerHTML = '<p>Обработка запроса...</p>'
		executionResult.innerHTML = ''

		// Отправляем запрос на сервер
		fetch('/query', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ input: input }),
		})
			.then((response) => response.json())
			.then((data) => {
				// Отображаем ответ
				responseText.innerHTML = `<p>${data.response}</p>`

				// Если это составная команда, отображаем информацию о шагах
				if (data.is_compound) {
					let stepsHtml = '<div class="steps-container"><h3>Шаги выполнения:</h3><ul>'

					data.steps.forEach((step) => {
						const statusClass =
							step.status === 'completed'
								? 'status-completed'
								: step.status === 'failed'
								? 'status-failed'
								: 'status-in-progress'

						stepsHtml += `<li>
						<div class="step-header">
							<span class="step-number">Шаг ${step.number}:</span> 
							<span class="step-description">${step.description}</span>
							<span class="step-status ${statusClass}">(${step.status})</span>
						</div>
						<div class="step-result">${step.result || step.error || ''}</div>
					</li>`
					})

					stepsHtml += `</ul>
					<div class="execution-summary">
						<p>Общий статус: <span class="${
							data.overall_status === 'completed' ? 'status-completed' : 'status-failed'
						}">${data.overall_status}</span></p>
						<p>Завершенность: ${data.completion_percentage ? data.completion_percentage.toFixed(1) : 0}%</p>
						<p>Точность: ${data.accuracy_percentage ? data.accuracy_percentage.toFixed(1) : 0}%</p>
					</div>
				</div>`

					executionResult.innerHTML = stepsHtml
				} else {
					// Для простых команд отображаем результат выполнения
					if (data.execution_result) {
						executionResult.innerHTML = `<div class="execution-result">
						<pre>${data.execution_result}</pre>
					</div>`
					}
				}

				// Обновляем историю после выполнения команды
				loadHistory()
			})
			.catch((error) => {
				responseText.innerHTML = `<p class="error">Ошибка: ${error.message}</p>`
			})

		// Очищаем поле ввода
		userInput.value = ''
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
		historyList.innerHTML = '<tr><td colspan="6">История очищена</td></tr>'
	})

	// Функция загрузки истории
	function loadHistory() {
		fetch('/history')
			.then((response) => response.json())
			.then((data) => {
				if (data.error) {
					historyList.innerHTML = `<tr><td colspan="6">Ошибка: ${data.error}</td></tr>`
					return
				}

				if (!data.history || data.history.length === 0) {
					historyList.innerHTML = '<tr><td colspan="6">История пуста</td></tr>'
					return
				}

				// Очищаем текущую историю
				historyList.innerHTML = ''

				// Добавляем записи истории
				data.history.forEach((entry) => {
					const row = document.createElement('tr')

					// Определяем класс для статуса
					const statusClass = entry.status?.includes('completed')
						? 'status-completed'
						: entry.status?.includes('failed')
						? 'status-failed'
						: 'status-in-progress'

					row.innerHTML = `
						<td>${entry.timestamp || 'Н/Д'}</td>
						<td>${entry.command || 'Н/Д'}</td>
						<td class="${statusClass}">${entry.status || 'Н/Д'}</td>
						<td>${entry.completion || 'Н/Д'}</td>
						<td>${entry.accuracy || 'Н/Д'}</td>
						<td>
							<button class="history-action-btn view-details" data-timestamp="${
								entry.timestamp
							}">Подробности</button>
							<button class="history-action-btn repeat-command" data-command="${entry.command}">Повторить</button>
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
						userInput.value = command
						queryForm.dispatchEvent(new Event('submit'))
					})
				})
			})
			.catch((error) => {
				historyList.innerHTML = `<tr><td colspan="6">Ошибка загрузки истории: ${error.message}</td></tr>`
			})
	}

	// Функция отображения подробной информации о команде
	function showCommandDetails(timestamp) {
		fetch(`/detailed_history/${timestamp}`)
			.then((response) => response.json())
			.then((data) => {
				if (data.error) {
					commandDetails.textContent = `Ошибка: ${data.error}`
				} else {
					commandDetails.textContent = data.details.join('\n')
				}

				// Отображаем модальное окно
				detailsModal.style.display = 'block'
			})
			.catch((error) => {
				commandDetails.textContent = `Ошибка загрузки подробностей: ${error.message}`
				detailsModal.style.display = 'block'
			})
	}

	// Инициализация интерфейса
	function initUI() {
		// Скрываем контейнер ответа до первого запроса
		responseContainer.style.display = 'none'

		// Фокус на поле ввода при загрузке страницы
		userInput.focus()
	}
})
