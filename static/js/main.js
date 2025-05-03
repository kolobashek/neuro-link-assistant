document.addEventListener('DOMContentLoaded', function () {
	const userInput = document.getElementById('user-input')
	const sendButton = document.getElementById('send-btn')
	const chatHistory = document.getElementById('chat-history')

	// Функция для отправки запроса
	function sendMessage() {
		const message = userInput.value.trim()
		if (message === '') return

		// Добавляем сообщение пользователя в историю
		addMessageToChat('user', message)

		// Показываем индикатор загрузки
		const loadingMsg = addMessageToChat('ai', 'Обрабатываю запрос...')

		// Очищаем поле ввода
		userInput.value = ''

		// Отправляем запрос на сервер
		fetch('/query', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ input: message }),
		})
			.then((response) => response.json())
			.then((data) => {
				// Удаляем индикатор загрузки
				chatHistory.removeChild(loadingMsg)

				// Добавляем ответ AI в историю
				let responseText = data.response

				// Если есть результат выполнения кода, добавляем его
				if (data.execution_result) {
					responseText += '\n\nРезультат выполнения: ' + data.execution_result
				}

				addMessageToChat('ai', responseText)

				// Если есть код, отображаем его в отдельном блоке
				if (data.code) {
					addCodeToChat(data.code)
				}
			})
			.catch((error) => {
				// Удаляем индикатор загрузки
				chatHistory.removeChild(loadingMsg)

				console.error('Ошибка:', error)
				addMessageToChat('ai', 'Произошла ошибка при обработке запроса.')
			})
	}

	// Функция для добавления сообщения в историю чата
	function addMessageToChat(sender, text) {
		const messageDiv = document.createElement('div')
		messageDiv.className = `message ${sender === 'user' ? 'user-message' : 'ai-message'}`

		// Преобразуем переносы строк в HTML-переносы
		text = text.replace(/\n/g, '<br>')

		messageDiv.innerHTML = text
		chatHistory.appendChild(messageDiv)

		// Прокручиваем историю вниз
		chatHistory.scrollTop = chatHistory.scrollHeight

		return messageDiv
	}

	// Функция для добавления блока кода в чат
	function addCodeToChat(code) {
		const codeDiv = document.createElement('div')
		codeDiv.className = 'code-block'

		const preElement = document.createElement('pre')
		const codeElement = document.createElement('code')
		codeElement.textContent = code

		preElement.appendChild(codeElement)
		codeDiv.appendChild(preElement)
		chatHistory.appendChild(codeDiv)

		// Прокручиваем историю вниз
		chatHistory.scrollTop = chatHistory.scrollHeight
	}

	// Обработчики событий
	sendButton.addEventListener('click', sendMessage)
	userInput.addEventListener('keypress', function (e) {
		if (e.key === 'Enter') {
			sendMessage()
		}
	})
})
