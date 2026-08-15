/* ========================================================================== */
/* API.JS                                                                     */
/* Helper centralizado para comunicarse con el servidor Django                */
/* ========================================================================== */

// Nueva función infalible: Lee el token directamente del HTML oculto
function getCsrfToken() {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) {
        return csrfInput.value;
    }
    console.warn("⚠️ No se encontró la etiqueta CSRF en el HTML");
    return '';
}

async function apiFetch(endpoint, options = {}) {
    try {
        const csrftoken = getCsrfToken();
        
        // Configuramos los headers y adjuntamos el Token
        const defaultHeaders = { 
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken 
        };
        
        const response = await fetch(endpoint, {
            ...options,
            headers: { ...defaultHeaders, ...options.headers }
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({})); 
            throw new Error(errorData.error || `Error HTTP: ${response.status}`);
        }

        return await response.json();
        
    } catch (error) {
        console.error(`🚨 Error en la API al llamar a [${endpoint}]:`, error);
        throw error; 
    }
}