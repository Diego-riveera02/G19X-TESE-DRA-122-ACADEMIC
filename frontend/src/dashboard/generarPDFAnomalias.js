export async function generarPDFAnomalias(anomalias) {

  if (anomalias.length === 0) {

    alert("No hay datos en el historial para exportar.");

    return;

  }


  let jsPDF;
  let autoTable;

  try {
    const [pdfModule, tableModule] = await Promise.all([
      import('jspdf'),
      import('jspdf-autotable'),
    ]);

    jsPDF = pdfModule.default;
    autoTable = tableModule.default;

    if (
      typeof jsPDF !== 'function' ||
      typeof autoTable !== 'function'
    ) {
      throw new Error('Modulos PDF invalidos');
    }
  } catch (error) {
    console.error('Error al cargar bibliotecas PDF:', error);
    alert('No se pudo preparar el PDF. Intenta nuevamente.');
    return;
  }

  const doc = new jsPDF();

  doc.setFontSize(18);

  doc.text("Bitácora de Anomalías - Sistema PluriOne", 14, 15);

  doc.setFontSize(11);

  const fechaActual = new Date().toLocaleString();

  doc.text(`Reporte generado el: ${fechaActual}`, 14, 22);

  const columnas = ["ID", "Pipeline", "Métrica", "Valor", "Estado", "Diagnóstico IA"];

  const filas = anomalias.map(row => [

    row.id,

    row.pipeline_name,

    row.metric_type,

    row.value,

    row.status,

    row.ai_recommendation || "Sin diagnóstico"

  ]);

  autoTable(doc, {

    startY: 28,

    head: [columnas],

    body: filas,

    theme: 'grid',

    headStyles: { fillColor: [229, 184, 11] },

    styles: { fontSize: 9 },

    columnStyles: { 5: { cellWidth: 70 } }

  });

  const fechaArchivo = new Date().toLocaleDateString('es-MX').replace(/\//g, '-');

  doc.save(`Bitacora_PluriOne_${fechaArchivo}.pdf`);

}
