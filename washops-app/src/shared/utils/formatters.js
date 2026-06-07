/**
 * Formatea un número como moneda colombiana.
 * @param {number} amount - Monto a formatear
 * @returns {string} Ej: "$45.000"
 */
export function formatCurrency(amount) {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Formatea una fecha ISO a formato legible.
 * @param {string} dateString - Fecha en formato ISO
 * @returns {string} Ej: "10/03 08:30"
 */
export function formatDate(dateString) {
  const date = new Date(dateString);
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${day}/${month} ${hours}:${minutes}`;
}

/**
 * Calcula la duración en minutos entre dos fechas.
 * @param {string} startedAt - Fecha de inicio en formato ISO
 * @param {string} completedAt - Fecha de fin en formato ISO
 * @returns {string} Ej: "38 min"
 */
export function formatDuration(startedAt, completedAt) {
  const start = new Date(startedAt);
  const end = new Date(completedAt);
  const diffMs = end - start;
  const minutes = Math.round(diffMs / 60000);
  return `${minutes} min`;
}
