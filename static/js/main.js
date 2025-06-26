/**
 * Функция для прерывания выполнения текущей команды
 */
function interruptCommand() {
	if (!commandExecutionInProgress) return

	// Показываем подтверждение
	if (confirm('Вы уверены, что хотите прервать выполнение текущей команды?')) {
		// ✅ ИСПРАВЛЕНО: /api/interrupt → /api/tasks/interrupt
		fetch('/api/tasks/interrupt', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
		})
			.then((response) => response.json())
			.then((data) => {
				console.log('Ответ на запрос прерывания:', data)

				// Показываем сообщение пользователю
				if (window.commandFormModule && window.commandFormModule.addMessage) {
					window.commandFormModule.addMessage('Выполнение команды прервано пользователем', 'system')
				}

				// Обновляем индикатор прогресса
				updateProgressBar(100)

				// Скрываем элементы управления через небольшую задержку
				setTimeout(hideCommandControls, 1500)
			})
			.catch((error) => {
				console.error('Ошибка при прерывании команды:', error)
				if (window.commandFormModule && window.commandFormModule.addMessage) {
					window.commandFormModule.addMessage(
						`Ошибка при прерывании команды: ${ error.message }`,
						'error'
					)
				}
			})
	}
}

/**
 * Инициализация интерфейса
 */
function initUI() {
	// Скрываем контейнер ответа до первого запроса
	const responseContainer = document.getElementById('response-container')
	if (responseContainer) {
		responseContainer.style.display = 'none'
	}

	// Фокус на поле ввода при загрузке страницы
	const userInput = document.getElementById('user-input')
	if (userInput) {
		userInput.focus()
	}
}

/**
 * Инициализация обработчиков событий
 */
function initEventHandlers() {
	// Обработчик для кнопки прерывания
	const interruptButton = document.getElementById('interrupt-command')
	if (interruptButton) {
		interruptButton.addEventListener('click', interruptCommand)
	}

	// Инициализация обработчиков для формы команд
	if (window.commandFormModule && window.commandFormModule.initCommandFormHandlers) {
		window.commandFormModule.initCommandFormHandlers()
	}

	// Инициализация обработчиков для истории
	if (window.historyModule && window.historyModule.initHistoryHandlers) {
		window.historyModule.initHistoryHandlers()
	}

	// Инициализация обработчиков для нейросетей
	if (window.aiModelsModule && window.aiModelsModule.initAIModelsHandlers) {
		window.aiModelsModule.initAIModelsHandlers()
	}
}

/**
 * Функция, выполняемая при загрузке страницы
 */
document.addEventListener('DOMContentLoaded', function () {
	console.log('Инициализация приложения...')

	// Инициализация интерфейса
	initUI()

	// Инициализация обработчиков событий
	initEventHandlers()

	// Загружаем историю при загрузке страницы
	if (window.historyModule && window.historyModule.updateCommandHistory) {
		window.historyModule.updateCommandHistory()
	}

	// Загружаем статус нейросетей
	if (window.aiModelsModule && window.aiModelsModule.updateAIModelsStatus) {
		window.aiModelsModule.updateAIModelsStatus()
	}

	console.log('Приложение инициализировано')
})

// Функции для управления элементами интерфейса
function showCommandControls(show = true) {
	const commandControls = document.querySelector('.command-controls')
	if (commandControls) {
		commandControls.style.display = show ? 'flex' : 'none'
	} else {
		console.warn('Элемент .command-controls не найден')
	}
}

function hideCommandControls() {
	showCommandControls(false)
}

function updateProgressBar(percentage) {
	const progressBar = document.querySelector('.progress-bar-fill')
	if (progressBar) {
		progressBar.style.width = `${ percentage }%`
	} else {
		console.warn('Элемент .progress-bar-fill не найден')
	}
}

// Экспортируем функции для использования в других модулях
window.mainModule = {
	showCommandControls,
	hideCommandControls,
	updateProgressBar,
	interruptCommand,
}

/**
 * Управление бургер-меню
 */
class BurgerMenu {
	constructor() {
		this.burgerBtn = document.getElementById('burgerMenu');
		this.nav = document.getElementById('mainNav');
		this.overlay = document.getElementById('navOverlay');
		this.closeBtn = document.getElementById('navClose');
		this.init();
	}

	init() {
		if (!this.burgerBtn || !this.nav) return;

		this.burgerBtn.addEventListener('click', () => this.toggle());
		this.closeBtn?.addEventListener('click', () => this.close());
		this.overlay?.addEventListener('click', () => this.close());

		// Закрытие по Escape
		document.addEventListener('keydown', (e) => {
			if (e.key === 'Escape' && this.nav.classList.contains('active')) {
				this.close();
			}
		});

		// Закрытие при клике по навигации
		this.nav.querySelectorAll('.nav-link').forEach(link => {
			link.addEventListener('click', () => setTimeout(() => this.close(), 200));
		});
	}

	toggle() {
		this.nav.classList.contains('active') ? this.close() : this.open();
	}

	open() {
		this.nav.classList.add('active');
		this.overlay?.classList.add('active');
		this.burgerBtn.classList.add('active');
		document.body.style.overflow = 'hidden';
	}

	close() {
		this.nav.classList.remove('active');
		this.overlay?.classList.remove('active');
		this.burgerBtn.classList.remove('active');
		document.body.style.overflow = '';
	}
}

// Инициализируем бургер-меню при загрузке
document.addEventListener('DOMContentLoaded', function () {
	// Существующая инициализация...

	// Добавляем инициализацию бургер-меню (должно быть только один раз!)
	window.burgerMenu = new BurgerMenu();

	// Подсветка активной страницы
	const currentPath = window.location.pathname;
	document.querySelectorAll('.nav-link').forEach(link => {
		if (new URL(link.href).pathname === currentPath) {
			link.classList.add('active');
		}
	});
});

// Дополняем экспорт
window.mainModule = {
	...window.mainModule,
	burgerMenu: () => window.burgerMenu
};
