/**
 * Utilidades para manejo de contraste de colores
 * Calcula automáticamente si usar texto claro u oscuro según el color de fondo
 */

/**
 * Convierte un color hex a RGB
 * @param {string} hex - Color en formato hex (#RRGGBB o #RGB)
 * @returns {object} Objeto con propiedades r, g, b
 */
function hexToRgb(hex) {
    // Eliminar el # si está presente
    hex = hex.replace('#', '');
    
    // Expandir formato corto (#RGB a #RRGGBB)
    if (hex.length === 3) {
        hex = hex.split('').map(char => char + char).join('');
    }
    
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);
    
    return { r, g, b };
}

/**
 * Convierte color RGB a formato CSS
 * @param {string} rgb - Color en formato rgb(r, g, b)
 * @returns {object} Objeto con propiedades r, g, b
 */
function parseRgb(rgb) {
    const match = rgb.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
    if (match) {
        return {
            r: parseInt(match[1]),
            g: parseInt(match[2]),
            b: parseInt(match[3])
        };
    }
    return null;
}

/**
 * Calcula la luminancia relativa de un color
 * @param {object} rgb - Objeto con propiedades r, g, b
 * @returns {number} Luminancia entre 0 y 1
 */
function getLuminance(rgb) {
    const { r, g, b } = rgb;
    
    // Convertir a valores sRGB
    const sR = r / 255;
    const sG = g / 255;
    const sB = b / 255;
    
    // Aplicar corrección gamma
    const rLin = sR <= 0.03928 ? sR / 12.92 : Math.pow((sR + 0.055) / 1.055, 2.4);
    const gLin = sG <= 0.03928 ? sG / 12.92 : Math.pow((sG + 0.055) / 1.055, 2.4);
    const bLin = sB <= 0.03928 ? sB / 12.92 : Math.pow((sB + 0.055) / 1.055, 2.4);
    
    // Calcular luminancia
    return 0.2126 * rLin + 0.7152 * gLin + 0.0722 * bLin;
}

/**
 * Determina si usar texto claro u oscuro según el color de fondo
 * @param {string} backgroundColor - Color de fondo en cualquier formato CSS
 * @returns {string} 'light' para texto claro, 'dark' para texto oscuro
 */
function getTextColor(backgroundColor) {
    let rgb;
    
    // Convertir diferentes formatos de color a RGB
    if (backgroundColor.startsWith('#')) {
        rgb = hexToRgb(backgroundColor);
    } else if (backgroundColor.startsWith('rgb')) {
        rgb = parseRgb(backgroundColor);
    } else {
        // Para colores con nombre, crear elemento temporal para obtener RGB
        const tempElement = document.createElement('div');
        tempElement.style.color = backgroundColor;
        document.body.appendChild(tempElement);
        const computedColor = window.getComputedStyle(tempElement).color;
        document.body.removeChild(tempElement);
        rgb = parseRgb(computedColor);
    }
    
    if (!rgb) {
        return 'light'; // Fallback a texto claro
    }
    
    const luminance = getLuminance(rgb);
    
    // Si la luminancia es mayor a 0.5, usar texto oscuro
    // Si es menor o igual a 0.5, usar texto claro
    return luminance > 0.5 ? 'dark' : 'light';
}

/**
 * Aplica el contraste automático a todos los badges de colores
 */
function applyAutoContrast() {
    const badges = document.querySelectorAll('.badge-colores, .chip-color');
    
    badges.forEach(badge => {
        const backgroundColor = badge.style.backgroundColor || 
                              window.getComputedStyle(badge).backgroundColor;
        
        if (backgroundColor && backgroundColor !== 'rgba(0, 0, 0, 0)') {
            const textColorType = getTextColor(backgroundColor);
            
            if (textColorType === 'dark') {
                badge.classList.add('text-dark');
                badge.classList.remove('text-light');
            } else {
                badge.classList.remove('text-dark');
                badge.classList.add('text-light');
            }
        }
    });
}

/**
 * Aplicar contraste a un badge específico
 * @param {HTMLElement} badge - Elemento badge
 * @param {string} backgroundColor - Color de fondo
 */
function applyContrastToElement(badge, backgroundColor) {
    const textColorType = getTextColor(backgroundColor);
    
    if (textColorType === 'dark') {
        badge.classList.add('text-dark');
        badge.classList.remove('text-light');
    } else {
        badge.classList.remove('text-dark');
        badge.classList.add('text-light');
    }
}

// Aplicar automáticamente cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    applyAutoContrast();
    
    // Observer para aplicar contraste a elementos agregados dinámicamente
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        const badges = node.querySelectorAll ? 
                                     node.querySelectorAll('.badge-colores, .chip-color') : [];
                        
                        badges.forEach(badge => {
                            const backgroundColor = badge.style.backgroundColor;
                            if (backgroundColor) {
                                applyContrastToElement(badge, backgroundColor);
                            }
                        });
                        
                        // Si el propio nodo es un badge
                        if (node.matches && node.matches('.badge-colores, .chip-color')) {
                            const backgroundColor = node.style.backgroundColor;
                            if (backgroundColor) {
                                applyContrastToElement(node, backgroundColor);
                            }
                        }
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});

// Exportar funciones para uso manual
window.ColorContrast = {
    applyAutoContrast,
    applyContrastToElement,
    getTextColor,
    hexToRgb,
    getLuminance
};