/**
 * Скрипт для обработки авторизации с персистентной сессией
 */
class AuthManager {
    constructor() {
        this.currentUser = null;
        this.token = localStorage.getItem('accessToken') || null;
        this.init();
    }

    async init() {
        console.log('🔐 Инициализация системы авторизации...');
        this.bindEvents();
        // Проверяем сессию при загрузке страницы
        await this.checkCurrentUser();
    }

    bindEvents() {
        const loginBtn = document.getElementById('loginBtn');
        const registerBtn = document.getElementById('registerBtn');
        const logoutBtn = document.getElementById('logoutBtn');
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');

        loginBtn?.addEventListener('click', () => window.modalManager.open('loginModal'));
        registerBtn?.addEventListener('click', () => window.modalManager.open('registerModal'));
        logoutBtn?.addEventListener('click', () => this.logout());
        loginForm?.addEventListener('submit', (e) => this.handleLogin(e));
        registerForm?.addEventListener('submit', (e) => this.handleRegister(e));
    }

    // --- ОСНОВНЫЕ МЕТОДЫ АВТОРИЗАЦИИ ---

    async handleLogin(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });

            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.message || 'Ошибка входа');
            }

            // ✅ Сохраняем токен и данные пользователя
            this.setSession(result.access_token, result.user);

            window.modalManager.close('loginModal');
            this.showNotification('Вход выполнен успешно!', 'success');
            e.target.reset();

        } catch (error) {
            console.error('❌ Ошибка входа:', error);
            this.showNotification(error.message, 'error');
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());

        if (data.password !== data.confirmPassword) {
            this.showNotification('Пароли не совпадают!', 'error');
            return;
        }

        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });

            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.message || 'Ошибка регистрации');
            }

            // ✅ Сохраняем токен и данные пользователя
            this.setSession(result.access_token, result.user);

            window.modalManager.close('registerModal');
            this.showNotification('Регистрация прошла успешно!', 'success');
            e.target.reset();

        } catch (error) {
            console.error('❌ Ошибка регистрации:', error);
            this.showNotification(error.message, 'error');
        }
    }

    /**
     * ✅ Проверяет токен при загрузке страницы для восстановления сессии
     */
    async checkCurrentUser() {
        if (!this.token) {
            this.updateAuthUI(); // Просто обновляем UI, если токена нет
            return;
        }

        try {
            const response = await fetch('/api/auth/me', {
                headers: { 'Authorization': `Bearer ${ this.token }` }
            });

            if (response.ok) {
                const result = await response.json();
                this.setSession(this.token, result.user); // Обновляем сессию
            } else {
                // Если токен невалидный (истек, неверный), выходим из системы
                this.logout();
            }
        } catch (error) {
            console.error('❌ Ошибка проверки сессии:', error);
            this.logout(); // В случае ошибки сети и т.д. - выходим
        }
    }

    logout() {
        this.currentUser = null;
        this.token = null;
        localStorage.removeItem('accessToken');
        localStorage.removeItem('currentUser');

        this.updateAuthUI();
        this.showNotification('Вы вышли из системы', 'info');

        // Закрываем меню, если оно было открыто
        window.burgerMenu?.close();

        // Перезагружаем страницу, чтобы сбросить состояние других компонентов
        // window.location.reload(); // Раскомментируйте для принудительной перезагрузки
    }

    // --- УПРАВЛЕНИЕ СЕССИЕЙ И UI ---

    setSession(token, user) {
        this.token = token;
        this.currentUser = user;
        localStorage.setItem('accessToken', token);
        localStorage.setItem('currentUser', JSON.stringify(user));
        this.updateAuthUI();
    }

    updateAuthUI() {
        const authUserInfo = document.getElementById('authUserInfo');
        const authButtons = document.getElementById('authButtons');
        const userName = document.getElementById('userName');
        const userRole = document.getElementById('userRole');

        if (this.currentUser) {
            authUserInfo.style.display = 'block';
            authButtons.style.display = 'none';
            userName.textContent = this.currentUser.display_name || this.currentUser.username;
            userRole.textContent = this.currentUser.role || 'user';
        } else {
            authUserInfo.style.display = 'none';
            authButtons.style.display = 'block';
        }
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `notification notification-${ type }`;
        notification.innerHTML = `<span>${ message }</span><button class="notification-close">&times;</button>`;
        container.appendChild(notification);

        setTimeout(() => notification.remove(), 5000);
        notification.querySelector('.notification-close').addEventListener('click', () => notification.remove());
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.authManager = new AuthManager();
});
