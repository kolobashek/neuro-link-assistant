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
				// Добавляем ответ AI в историю
				addMessageToChat('ai', data.response)
			})
			.catch((error) => {
				console.error('Ошибка:', error)
				addMessageToChat('ai', 'Произошла ошибка при обработке запроса.')
			})
	}

	// Функция для добавления сообщения в историю чата
	function addMessageToChat(sender, text) {
		const messageDiv = document.createElement('div')
		messageDiv.className = `message ${sender === 'user' ? 'user-message' : 'ai-message'}`
		messageDiv.textContent = text
		chatHistory.appendChild(messageDiv)

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
