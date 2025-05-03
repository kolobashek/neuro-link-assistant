document.addEventListener('DOMContentLoaded', function () {
	const commandInput = document.getElementById('command-input')
	const sendBtn = document.getElementById('send-btn')
	const responseText = document.getElementById('response-text')
	const codeContainer = document.getElementById('code-container')
	const codeBlock = document.getElementById('code-block')
	const executionResult = document.getElementById('execution-result')
	const executionText = document.getElementById('execution-text')
	const commandButtons = document.querySelectorAll('.command-btn')

	// Обработчик для кнопок предустановленных команд
	commandButtons.forEach((button) => {
		button.addEventListener('click', function () {
			const command = this.getAttribute('data-command')
			commandInput.value = command
			sendCommand()
		})
	})

	// Обработчик для кнопки отправки
	sendBtn.addEventListener('click', sendCommand)

	// Обработчик для нажатия Enter в поле ввода
	commandInput.addEventListener('keypress', function (e) {
		if (e.key === 'Enter') {
			sendCommand()
		}
	})

	function sendCommand() {
		const command = commandInput.value.trim()

		if (command === '') {
			return
		}

		// Очистка предыдущих результатов
		responseText.textContent = 'Обработка команды...'
		codeContainer.style.display = 'none'
		executionResult.style.display = 'none'

		// Отправка запроса на сервер
		fetch('/query', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ input: command }),
		})
			.then((response) => response.json())
			.then((data) => {
				// Отображение ответа
				responseText.textContent = data.response

				// Отображение кода, если он есть
				if (data.code) {
					codeBlock.textContent = data.code
					codeContainer.style.display = 'block'
				}

				// Отображение результата выполнения, если он есть
				if (data.execution_result) {
					executionText.textContent = data.execution_result
					executionResult.style.display = 'block'
				}
			})
			.catch((error) => {
				responseText.textContent = 'Ошибка при обработке запроса: ' + error
			})
	}
})
