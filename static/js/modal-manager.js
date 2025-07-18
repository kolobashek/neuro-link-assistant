class ModalManager {
  constructor() {
    this.activeModals = new Set();

    // Состояние, специфичное для чата
    this.chatModal = null;
    this.currentSessionId = null;
    this.isLoading = false;

    // DOM-элементы, специфичные для чата
    this.chatListEl = null;
    this.chatHistoryEl = null;
    this.chatTitleEl = null;
    this.promptForm = null;
    this.promptInput = null;
    this.sendButton = null;
    this.newChatButton = null;

    this.init();
  }

  init() {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.initEventHandlers());
    } else {
      this.initEventHandlers();
    }
    console.log('✅ ModalManager (with Chat) инициализирован');
  }

  initEventHandlers() {
    // Общие обработчики для открытия модальных окон
    document.addEventListener('click', (e) => {
      const trigger = e.target.closest('[data-modal-open]');
      if (trigger) {
        e.preventDefault();
        this.open(trigger.getAttribute('data-modal-open'));
      }
    });

    // Общие обработчики для закрытия
    document.addEventListener('click', (e) => {
      const closeBtn = e.target.closest('[data-modal-close], .modal-close');
      if (closeBtn) {
        e.preventDefault();
        const modalId = closeBtn.closest('.modal')?.id;
        if (modalId) this.close(modalId);
      }
    });

    // Закрытие по клику на оверлей
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('modal') && this.isOpen(e.target.id)) {
        this.close(e.target.id);
      }
    });

    // Закрытие по клавише Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.activeModals.size > 0) {
        const lastModal = Array.from(this.activeModals).pop();
        this.close(lastModal);
      }
    });

    // Инициализация функциональности чата, если модальное окно есть на странице
    this.chatModal = document.getElementById('aiTestModal');
    if (this.chatModal) {
      this._initChatFunctionality();
    }
  }

  // --- Общие методы для модальных окон ---

  open(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return false;

    this.activeModals.add(modalId);
    modal.classList.add('active');
    document.body.classList.add('modal-open');

    // Если это модальное окно чата, инициализируем его
    if (modalId === 'aiTestModal') {
      this.loadChatList();
    }
    return true;
  }

  close(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return false;

    this.activeModals.delete(modalId);
    modal.classList.remove('active');

    if (this.activeModals.size === 0) {
      document.body.classList.remove('modal-open');
    }

    // Очищаем состояние чата при закрытии
    if (modalId === 'aiTestModal') {
      this.currentSessionId = null;
      if (this.chatHistoryEl) this.chatHistoryEl.innerHTML = '';
      if (this.chatListEl) this.chatListEl.innerHTML = '';
    }
    return true;
  }

  isOpen(modalId) {
    return this.activeModals.has(modalId);
  }

  // --- Методы, специфичные для чата ---

  // Исправленный фрагмент для _initChatFunctionality
  _initChatFunctionality() {
    // Привязка DOM-элементов
    this.chatListEl = this.chatModal.querySelector('#chatList');
    this.chatHistoryEl = this.chatModal.querySelector('#chatHistory');
    this.chatTitleEl = this.chatModal.querySelector('#chatTitle');
    this.promptForm = this.chatModal.querySelector('#aiTestForm');
    this.promptInput = this.chatModal.querySelector('#aiPrompt');
    this.sendButton = this.chatModal.querySelector('.send-btn');
    this.newChatButton = this.chatModal.querySelector('#newChatBtn');

    // Отключаем стандартную отправку формы
    if (this.promptForm) {
      this.promptForm.addEventListener('submit', (e) => e.preventDefault());
    }

    // Обработчик Enter в поле ввода
    if (this.promptInput) {
      this.promptInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          if (e.ctrlKey || e.shiftKey) {
            // Ctrl+Enter или Shift+Enter = перенос строки
            return true;
          }
          // Обычный Enter = отправка
          e.preventDefault();
          this.sendMessage();
        }
      });

      // Автоизменение высоты
      this.promptInput.addEventListener('input', () => {
        this.promptInput.style.height = 'auto';
        this.promptInput.style.height = Math.min(this.promptInput.scrollHeight, 120) + 'px';
      });
    }

    // Остальные обработчики...
    if (this.newChatButton) {
      this.newChatButton.addEventListener('click', () => this.createNewChat());
    }

    if (this.sendButton) {
      this.sendButton.addEventListener('click', (e) => {
        e.preventDefault();
        this.sendMessage();
      });
    }

    if (this.chatListEl) {
      this.chatListEl.addEventListener('click', (e) => {
        const chatItem = e.target.closest('.chat-list-item');
        if (!chatItem) return;

        const sessionId = chatItem.dataset.sessionId;
        if (e.target.closest('.delete-chat-btn')) {
          this.deleteChat(sessionId, chatItem);
        } else {
          this.selectChat(sessionId);
        }
      });
    }
  }


  async loadChatList() {
    this.setLoading(true);

    // ✅ Проверяем токен ПЕРЕД отправкой запроса
    const token = localStorage.getItem('accessToken');
    if (!token) {
      this.chatHistoryEl.innerHTML = `
            <div class="message ai-message">
                <div class="message-content">
                    <strong>Требуется авторизация.</strong><br>
                    Пожалуйста, войдите в систему, чтобы использовать чат.
                </div>
            </div>`;
      this.setLoading(false);
      return;
    }

    try {
      const response = await fetch('/api/chat/chats', {
        headers: {
          'Authorization': `Bearer ${ token }`
        }
      });
      if (!response.ok) {
        if (response.status === 401) {
          this.chatHistoryEl.innerHTML = `<div class="message ai-message"><div class="message-content">Сессия истекла или недействительна. Пожалуйста, перезайдите в систему.</div></div>`;
          return;
        }
        throw new Error('Failed to load chats');
      }

      const chats = await response.json();
      this.renderChatList(chats);

      // ✅ ИСПРАВЛЕНИЕ: Всегда должен быть активный чат
      if (chats.length > 0) {
        await this.selectChat(chats[0].id);
      } else {
        // Если чатов нет, создаем новый автоматически
        console.log('📝 Чатов нет, создаем новый автоматически');
        await this.createNewChat();
      }
    } catch (error) {
      console.error("Error loading chat list:", error);
      // ✅ Если ошибка загрузки, тоже создаем новый чат
      console.log('❌ Ошибка загрузки чатов, создаем новый');
      await this.createNewChat();
    } finally {
      this.setLoading(false);
    }
  }

  renderChatList(chats) {
    this.chatListEl.innerHTML = '';
    chats.forEach(chat => {
      const li = document.createElement('li');
      li.className = 'chat-list-item';
      li.dataset.sessionId = chat.id;
      li.innerHTML = `
                <span class="chat-title" title="${ chat.title }">${ chat.title }</span>
                <button class="delete-chat-btn" title="Удалить чат"><i class="fas fa-trash-alt"></i></button>
            `;
      this.chatListEl.appendChild(li);
    });
  }

  async createNewChat() {
    this.setLoading(true);
    try {
      // ✅ УЛУЧШЕНИЕ: Генерируем уникальное имя для чата
      const now = new Date();
      const dateStr = now.toLocaleDateString('ru-RU');
      const timeStr = now.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
      const chatNumber = Date.now() % 10000; // Используем последние 4 цифры timestamp как номер

      const chatTitle = `Чат #${ chatNumber } от ${ dateStr } ${ timeStr }`;

      const response = await fetch('/api/chat/chats', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${ localStorage.getItem('accessToken') }`
        },
        body: JSON.stringify({
          title: chatTitle  // Отправляем сгенерированное название
        })
      });
      if (!response.ok) throw new Error('Failed to create chat');

      const newChat = await response.json();
      console.log('✅ Новый чат создан:', newChat);

      // Перезагружаем список и выбираем новый чат
      await this.loadChatList();
      await this.selectChat(newChat.id);
    } catch (error) {
      console.error("Error creating new chat:", error);
      // ✅ Если не удается создать чат, показываем сообщение об ошибке
      this.chatHistoryEl.innerHTML = `
        <div class="message ai-message">
          <div class="message-content">
            ❌ Не удалось создать новый чат. Проверьте подключение к серверу.
          </div>
        </div>`;
    } finally {
      this.setLoading(false);
    }
  }

  async selectChat(sessionId) {
    if (this.isLoading || this.currentSessionId === sessionId) return;

    this.setLoading(true);
    this.currentSessionId = sessionId;

    this.chatListEl.querySelectorAll('.chat-list-item').forEach(item => {
      item.classList.toggle('active', item.dataset.sessionId === sessionId);
    });

    this.chatHistoryEl.innerHTML = '<div class="message ai-message"><div class="spinner"></div></div>';
    try {
      const response = await fetch(`/api/chat/chats/${ sessionId }/messages`, {
        headers: { 'Authorization': `Bearer ${ localStorage.getItem('accessToken') }` }
      });
      if (!response.ok) throw new Error('Failed to load messages');

      const messages = await response.json();
      this.renderMessages(messages);
      const selectedChat = this.chatListEl.querySelector(`[data-session-id="${ sessionId }"] .chat-title`);
      this.chatTitleEl.textContent = selectedChat ? selectedChat.textContent : "Чат";

    } catch (error) {
      console.error(`Error loading chat ${ sessionId }:`, error);
      this.chatHistoryEl.innerHTML = `<div class="message ai-message"><div class="message-content">Ошибка загрузки сообщений.</div></div>`;
    } finally {
      this.setLoading(false);
    }
  }

  async deleteChat(sessionId, listItemElement) {
    if (!confirm('Вы уверены, что хотите удалить этот чат?')) return;

    try {
      await fetch(`/api/chat/chats/${ sessionId }`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${ localStorage.getItem('accessToken') }` }
      });

      listItemElement.remove();

      if (this.currentSessionId === sessionId) {
        const firstChat = this.chatListEl.querySelector('.chat-list-item');
        if (firstChat) {
          await this.selectChat(firstChat.dataset.sessionId);
        } else {
          await this.createNewChat();
        }
      }
    } catch (error) {
      console.error(`Error deleting chat ${ sessionId }:`, error);
    }
  }

  async sendMessage() {
    const prompt = this.promptInput.value.trim();
    if (!prompt || this.isLoading) return;

    // ✅ ИСПРАВЛЕНИЕ: Если нет активного чата, создаем новый
    if (!this.currentSessionId) {
      console.log('📝 Нет активного чата, создаем новый перед отправкой сообщения');
      await this.createNewChat();

      // Если чат все еще не создан, выходим
      if (!this.currentSessionId) {
        console.error('❌ Не удалось создать чат для отправки сообщения');
        return;
      }
    }

    this.setLoading(true);
    this.addMessageToUI('user', prompt);
    this.promptInput.value = '';
    this.promptInput.style.height = 'auto';

    try {
      const response = await fetch(`/api/chat/chats/${ this.currentSessionId }/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${ localStorage.getItem('accessToken') }`
        },
        body: JSON.stringify({ prompt: prompt })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.error || `HTTP ${ response.status }: ${ response.statusText }`;
        throw new Error(errorMessage);
      }

      const aiMessage = await response.json();
      this.addMessageToUI(aiMessage.role, aiMessage.content);
    } catch (error) {
      console.error("Error sending message:", error);

      let errorMessage = '❌ Произошла ошибка при отправке сообщения.';

      if (error.message.includes('Failed to fetch')) {
        errorMessage = '🌐 Проблемы с подключением к серверу.';
      } else if (error.message.includes('401')) {
        errorMessage = '🔐 Сессия истекла. Пожалуйста, войдите заново.';
      } else if (error.message.includes('500')) {
        errorMessage = '⚙️ Внутренняя ошибка сервера. Попробуйте позже.';
      } else if (error.message) {
        errorMessage = `❌ ${ error.message }`;
      }

      this.addMessageToUI('ai', errorMessage);
    } finally {
      this.setLoading(false);
    }
  }

  renderMessages(messages) {
    this.chatHistoryEl.innerHTML = '';
    if (messages.length === 0) {
      this.chatHistoryEl.innerHTML = `<div class="message ai-message"><div class="bot-avatar">🤖</div><div class="message-content">Это новый чат. Задайте мне любой вопрос!</div></div>`;
    } else {
      messages.forEach(msg => this.addMessageToUI(msg.role, msg.content, false));
    }
    this.chatHistoryEl.scrollTop = this.chatHistoryEl.scrollHeight;
  }

  addMessageToUI(role, content, scroll = true) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${ role }-message`;

    const avatar = role === 'user' ? '👤' : '🤖';

    // Простая замена \n на <br> для отображения переносов строк
    const formattedContent = content.replace(/\n/g, '<br>');

    messageDiv.innerHTML = `
            <div class="bot-avatar">${ avatar }</div>
            <div class="message-content">${ formattedContent }</div>
        `;

    this.chatHistoryEl.appendChild(messageDiv);
    if (scroll) {
      this.chatHistoryEl.scrollTop = this.chatHistoryEl.scrollHeight;
    }
  }

  setLoading(isLoading) {
    this.isLoading = isLoading;
    this.promptInput.disabled = isLoading;
    this.sendButton.disabled = isLoading;
    this.newChatButton.disabled = isLoading;
    this.chatListEl.style.pointerEvents = isLoading ? 'none' : 'auto';
    this.chatListEl.style.opacity = isLoading ? 0.7 : 1;
  }
}
// Глобальный экземпляр для доступа из других скриптов, если потребуется
window.modalManager = new ModalManager();
