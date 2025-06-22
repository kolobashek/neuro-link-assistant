/**
 * Скрипт для обработки авторизации
 */

class AuthManager {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    init() {
        console.log('🔐 Инициализация системы авторизации...');

        // Привязываем обработчики событий
        this.bindEvents();

        // Проверяем текущего пользователя
        this.checkCurrentUser();
    }

    bindEvents() {
        // Кнопки открытия модальных окон
        const loginBtn = document.getElementById('loginBtn');
        const registerBtn = document.getElementById('registerBtn');
        const logoutBtn = document.getElementById('logoutBtn');

        if (loginBtn) {
            loginBtn.addEventListener('click', () => this.openModal('loginModal'));
        }

        if (registerBtn) {
            registerBtn.addEventListener('click', () => this.openModal('registerModal'));
        }

        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }

        // Закрытие модальных окон
        document.querySelectorAll('.modal-close, [data-modal]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modalId = btn.getAttribute('data-modal');
                if (modalId) {
                    this.closeModal(modalId);
                }
            });
        });

        // Закрытие по клику вне модального окна
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal.id);
                }
            });
        });

        // Обработка форм
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');

        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.classList.add('modal-open');
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
            document.body.classList.remove('modal-open');
        }
    }

    async handleLogin(e) {
        e.preventDefault();

        const formData = new FormData(e.target);
        const username = formData.get('username');
        const password = formData.get('password');

        try {
            // Здесь будет реальный API запрос
            console.log('🔐 Попытка входа:', username);

            // Временная заглушка
            this.setCurrentUser({
                username: username,
                role: 'user',
                email: 'user@example.com'
            });

            this.closeModal('loginModal');
            this.showNotification('Вход выполнен успешно!', 'success');

        } catch (error) {
            console.error('❌ Ошибка входа:', error);
            this.showNotification('Ошибка входа. Проверьте данные.', 'error');
        }
    }

    async handleRegister(e) {
        e.preventDefault();

        const formData = new FormData(e.target);
        const username = formData.get('username');
        const email = formData.get('email');
        const password = formData.get('password');
        const confirmPassword = formData.get('confirmPassword');

        if (password !== confirmPassword) {
            this.showNotification('Пароли не совпадают!', 'error');
            return;
        }

        try {
            // Здесь будет реальный API запрос
            console.log('📝 Попытка регистрации:', username, email);

            // Временная заглушка
            this.setCurrentUser({
                username: username,
                role: 'user',
                email: email
            });

            this.closeModal('registerModal');
            this.showNotification('Регистрация прошла успешно!', 'success');

        } catch (error) {
            console.error('❌ Ошибка регистрации:', error);
            this.showNotification('Ошибка регистрации. Попробуйте позже.', 'error');
        }
    }

    logout() {
        this.currentUser = null;
        this.updateAuthUI();
        this.showNotification('Вы вышли из системы', 'info');

        // Закрываем меню после выхода
        const nav = document.getElementById('mainNav');
        if (nav) {
            nav.classList.remove('active');
        }
    }

    setCurrentUser(user) {
        this.currentUser = user;
        this.updateAuthUI();
    }

    updateAuthUI() {
        const authUserInfo = document.getElementById('authUserInfo');
        const authButtons = document.getElementById('authButtons');
        const userName = document.getElementById('userName');
        const userRole = document.getElementById('userRole');

        if (this.currentUser) {
            // Показываем информацию о пользователе
            if (authUserInfo) authUserInfo.style.display = 'block';
            if (authButtons) authButtons.style.display = 'none';

            if (userName) userName.textContent = this.currentUser.username;
            if (userRole) userRole.textContent = this.currentUser.role;
        } else {
            // Показываем кнопки входа/регистрации
            if (authUserInfo) authUserInfo.style.display = 'none';
            if (authButtons) authButtons.style.display = 'block';
        }
    }

    checkCurrentUser() {
        // Здесь можно проверить токен из localStorage или cookies
        // Пока используем заглушку
        const savedUser = localStorage.getItem('currentUser');
        if (savedUser) {
            try {
                this.currentUser = JSON.parse(savedUser);
                this.updateAuthUI();
            } catch (e) {
                localStorage.removeItem('currentUser');
            }
        }
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        `;

        container.appendChild(notification);

        // Автоматическое закрытие через 5 секунд
        setTimeout(() => {
            notification.remove();
        }, 5000);

        // Закрытие по клику
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.authManager = new AuthManager();
});
