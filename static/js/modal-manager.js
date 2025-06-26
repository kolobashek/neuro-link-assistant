class ModalManager {
  constructor() {
    this.activeModals = new Set();
    this.init();
  }

  init() {
    // ✅ Автоматическая инициализация при загрузке DOM
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.initEventHandlers());
    } else {
      this.initEventHandlers();
    }

    console.log('✅ ModalManager инициализирован');
  }

  initEventHandlers() {
    // ✅ Обработчик для кнопок открытия (data-modal-open)
    document.addEventListener('click', (e) => {
      const trigger = e.target.closest('[data-modal-open]');
      if (trigger) {
        e.preventDefault();
        const modalId = trigger.getAttribute('data-modal-open');
        this.open(modalId);
      }
    });

    // ✅ Обработчик для кнопок закрытия
    document.addEventListener('click', (e) => {
      const closeBtn = e.target.closest('[data-modal-close], .modal-close');
      if (closeBtn) {
        e.preventDefault();
        const modalId = closeBtn.getAttribute('data-modal-close') ||
          closeBtn.closest('.modal')?.id;
        if (modalId) {
          this.close(modalId);
        }
      }
    });

    // ✅ Закрытие по клику на overlay
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('modal') && this.isOpen(e.target.id)) {
        this.close(e.target.id);
      }
    });

    // ✅ Закрытие по Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.activeModals.size > 0) {
        const lastModal = Array.from(this.activeModals).pop();
        this.close(lastModal);
      }
    });
  }

  open(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) {
      console.error(`❌ Модальное окно ${ modalId } не найдено`);
      return false;
    }

    this.activeModals.add(modalId);
    modal.classList.add('active');
    document.body.classList.add('modal-open');

    // ✅ Фокус на первом элементе ввода
    setTimeout(() => {
      const firstInput = modal.querySelector('input, textarea, select, button:not([data-modal-close])');
      firstInput?.focus();
    }, 100);

    console.log(`✅ Модальное окно ${ modalId } открыто`);
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

    console.log(`✅ Модальное окно ${ modalId } закрыто`);
    return true;
  }

  isOpen(modalId) {
    return this.activeModals.has(modalId);
  }
}

// ✅ Глобальный экземпляр
window.modalManager = new ModalManager();
