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

// Инициализируем автодополнение при загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
	initCommandAutocomplete()
})
