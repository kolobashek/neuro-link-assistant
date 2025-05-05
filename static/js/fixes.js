/**
 * Файл с исправлениями для известных ошибок
 */

/**
 * Функция для исправления ошибки с отсутствующим файлом журнала
 * Создает пустой файл журнала при первом запуске
 */
function createEmptyLogFileIfNeeded() {
	// Отправляем запрос на создание пустого файла журнала, если он не существует
	fetch('/api/ensure_log_files_exist', {
		method: 'POST',
	})
		.then((response) => response.json())
		.then((data) => {
			console.log('Проверка файлов журнала:', data)
		})
		.catch((error) => {
			console.error('Ошибка при проверке файлов журнала:', error)
		})
}

// Вызываем функцию при загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
	createEmptyLogFileIfNeeded()
})
