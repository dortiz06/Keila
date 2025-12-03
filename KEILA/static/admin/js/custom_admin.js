// JavaScript personalizado para el Admin de Django - Sistema de RH

document.addEventListener('DOMContentLoaded', function() {
    // Mejorar la experiencia del formulario
    enhanceFormFields();
    addFormValidation();
    addAnimations();
    addTooltips();
});

function enhanceFormFields() {
    // Agregar efectos visuales a los campos
    const inputs = document.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        // Efecto de focus
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
        
        // Validación en tiempo real
        input.addEventListener('input', function() {
            validateField(this);
        });
    });
}

function addFormValidation() {
    // Validación personalizada
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
                showNotification('Por favor, corrige los errores antes de continuar', 'error');
            }
        });
    }
}

function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name;
    let isValid = true;
    let message = '';
    
    // Remover mensajes de error anteriores
    removeFieldError(field);
    
    // Validaciones específicas
    switch(fieldName) {
        case 'numero_empleado':
            if (value && !/^[A-Z0-9-]+$/.test(value)) {
                isValid = false;
                message = 'El número de empleado debe contener solo letras mayúsculas, números y guiones';
            }
            break;
            
        case 'email':
            if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                isValid = false;
                message = 'Por favor, ingresa un email válido';
            }
            break;
            
        case 'telefono':
            if (value && !/^[\d\s\-\+\(\)]+$/.test(value)) {
                isValid = false;
                message = 'Por favor, ingresa un teléfono válido';
            }
            break;
            
        case 'salario':
            if (value && (isNaN(value) || parseFloat(value) < 0)) {
                isValid = false;
                message = 'El salario debe ser un número positivo';
            }
            break;
            
        case 'fecha_nacimiento':
            if (value) {
                const birthDate = new Date(value);
                const today = new Date();
                const age = today.getFullYear() - birthDate.getFullYear();
                
                if (age < 16 || age > 80) {
                    isValid = false;
                    message = 'La edad debe estar entre 16 y 80 años';
                }
            }
            break;
            
        case 'fecha_ingreso':
            if (value) {
                const hireDate = new Date(value);
                const today = new Date();
                
                if (hireDate > today) {
                    isValid = false;
                    message = 'La fecha de ingreso no puede ser futura';
                }
            }
            break;
    }
    
    // Mostrar error si es necesario
    if (!isValid) {
        showFieldError(field, message);
    }
    
    return isValid;
}

function validateForm() {
    const requiredFields = document.querySelectorAll('input[required], select[required], textarea[required]');
    let isFormValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'Este campo es obligatorio');
            isFormValid = false;
        } else if (!validateField(field)) {
            isFormValid = false;
        }
    });
    
    return isFormValid;
}

function showFieldError(field, message) {
    const fieldContainer = field.closest('.field-box') || field.parentElement;
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.style.cssText = `
        color: #e74c3c;
        font-size: 0.85rem;
        margin-top: 5px;
        padding: 5px 10px;
        background: #f8d7da;
        border-radius: 4px;
        border-left: 3px solid #e74c3c;
    `;
    errorDiv.textContent = message;
    
    fieldContainer.appendChild(errorDiv);
    field.style.borderColor = '#e74c3c';
}

function removeFieldError(field) {
    const fieldContainer = field.closest('.field-box') || field.parentElement;
    const existingError = fieldContainer.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    field.style.borderColor = '';
}

function addAnimations() {
    // Animación de entrada para los campos
    const formRows = document.querySelectorAll('.form-row');
    formRows.forEach((row, index) => {
        row.style.opacity = '0';
        row.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            row.style.transition = 'all 0.6s ease';
            row.style.opacity = '1';
            row.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

function addTooltips() {
    // Agregar tooltips informativos
    const tooltips = {
        'numero_empleado': 'Formato: EMP001, RH-2024, etc.',
        'email': 'Se usará para notificaciones del sistema',
        'telefono': 'Incluye código de país si es necesario',
        'salario': 'Salario mensual en la moneda local',
        'fecha_nacimiento': 'Se usará para calcular la edad',
        'fecha_ingreso': 'Fecha de inicio de labores en la empresa',
        'dias_vacaciones_anuales': 'Días de vacaciones por año según política',
        'dias_vacaciones_usados': 'Días ya utilizados en el año actual'
    };
    
    Object.keys(tooltips).forEach(fieldName => {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (field) {
            const label = field.closest('.field-box')?.querySelector('label');
            if (label) {
                label.title = tooltips[fieldName];
                label.style.cursor = 'help';
            }
        }
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        animation: slideIn 0.3s ease;
    `;
    
    const colors = {
        'success': '#27ae60',
        'error': '#e74c3c',
        'warning': '#f39c12',
        'info': '#3498db'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remover después de 5 segundos
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Agregar estilos CSS para las animaciones
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .field-box.focused {
        transform: scale(1.02);
        transition: transform 0.2s ease;
    }
    
    .field-error {
        animation: shake 0.5s ease;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
`;
document.head.appendChild(style);
