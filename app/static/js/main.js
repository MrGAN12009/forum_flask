/**
 * Основной JavaScript файл для форума
 */

// Автоскрытие alert-ов через 5 секунд
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Подтверждение удаления
function confirmDelete(message) {
    return confirm(message || 'Вы уверены, что хотите удалить это?');
}

// Предпросмотр изображения перед загрузкой
function previewImage(input, previewId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const preview = document.getElementById(previewId);
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

// Валидация размера файла
function validateFileSize(input, maxSizeMB = 16) {
    if (input.files && input.files[0]) {
        const fileSize = input.files[0].size / 1024 / 1024; // в MB
        
        if (fileSize > maxSizeMB) {
            alert(`Файл слишком большой. Максимальный размер: ${maxSizeMB}MB`);
            input.value = '';
            return false;
        }
    }
    return true;
}

// Автоматическое расширение textarea
function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

// Инициализация auto-resize для всех textarea
document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('textarea.auto-resize');
    
    textareas.forEach(function(textarea) {
        textarea.addEventListener('input', function() {
            autoResize(this);
        });
        
        // Начальная высота
        autoResize(textarea);
    });
});

// Форматирование времени "X минут назад"
function timeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    let interval = seconds / 31536000;
    if (interval > 1) return Math.floor(interval) + ' лет назад';
    
    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + ' месяцев назад';
    
    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + ' дней назад';
    
    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + ' часов назад';
    
    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + ' минут назад';
    
    return Math.floor(seconds) + ' секунд назад';
}

// Плавная прокрутка к якорям
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Копирование в буфер обмена
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showToast('Скопировано в буфер обмена');
        }).catch(function(err) {
            console.error('Ошибка копирования:', err);
        });
    } else {
        // Fallback для старых браузеров
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand('copy');
            showToast('Скопировано в буфер обмена');
        } catch (err) {
            console.error('Ошибка копирования:', err);
        }
        document.body.removeChild(textarea);
    }
}

// Показать toast уведомление
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show`;
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(function() {
        toast.remove();
    }, 3000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.style.position = 'fixed';
    container.style.top = '20px';
    container.style.right = '20px';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

