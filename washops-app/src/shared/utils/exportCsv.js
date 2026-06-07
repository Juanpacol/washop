/**
 * Genera y descarga un archivo CSV a partir de un array de objetos.
 * @param {string} filename - Nombre del archivo (sin extensión)
 * @param {Object[]} rows - Array de objetos con los datos a exportar
 */
export function exportToCsv(filename, rows) {
  if (!rows || rows.length === 0) return;

  const headers = Object.keys(rows[0]);
  const csvLines = [
    headers.join(','),
    ...rows.map(row =>
      headers.map(header => {
        const value = row[header] ?? '';
        const escaped = String(value).replace(/"/g, '""');
        return `"${escaped}"`;
      }).join(',')
    ),
  ];

  const csvContent = csvLines.join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `${filename}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
