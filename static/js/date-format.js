/**
 * Formateo de fechas a DD/MM/YYYY para inputs type="date"
 * 
 * Los inputs HTML5 type="date" siempre usan formato YYYY-MM-DD internamente,
 * pero podemos formatear el valor mostrado usando JavaScript.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Obtener todos los inputs de tipo date
    const dateInputs = document.querySelectorAll('input[type="date"]');
    
    dateInputs.forEach(function(input) {
        // Agregar evento para formatear cuando cambie el valor
        input.addEventListener('change', function() {
            formatDateInput(this);
        });
        
        // Formatear valor inicial si existe
        if (input.value) {
            formatDateDisplay(input);
        }
        
        // Agregar clase para estilizado
        input.classList.add('date-input-dd-mm-yyyy');
    });
    
    // Función para formatear el display del input
    function formatDateDisplay(input) {
        if (!input.value) return;
        
        // El valor viene en formato YYYY-MM-DD
        const parts = input.value.split('-');
        if (parts.length === 3) {
            const year = parts[0];
            const month = parts[1];
            const day = parts[2];
            
            // Convertir a DD/MM/YYYY para mostrar
            // Nota: Esto no cambia el valor real, solo la visualización
            // El navegador mostrará el formato según su configuración regional
            // pero podemos agregar un placeholder o helper text
            input.setAttribute('data-format', 'DD/MM/YYYY');
        }
    }
    
    // Función para validar y formatear cuando el usuario escribe
    function formatDateInput(input) {
        formatDateDisplay(input);
    }
});

/**
 * Función auxiliar para convertir fecha YYYY-MM-DD a DD/MM/YYYY
 */
function formatDateToDDMMYYYY(dateString) {
    if (!dateString) return '';
    const parts = dateString.split('-');
    if (parts.length === 3) {
        return `${parts[2]}/${parts[1]}/${parts[0]}`;
    }
    return dateString;
}

/**
 * Función auxiliar para convertir DD/MM/YYYY a YYYY-MM-DD
 */
function formatDateFromDDMMYYYY(dateString) {
    if (!dateString) return '';
    const parts = dateString.split('/');
    if (parts.length === 3) {
        const day = parts[0].padStart(2, '0');
        const month = parts[1].padStart(2, '0');
        const year = parts[2];
        return `${year}-${month}-${day}`;
    }
    return dateString;
}

