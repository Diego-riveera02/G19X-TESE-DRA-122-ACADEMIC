export default function HistorialAnomalias({
  anomalias,
  exportarPDF,
  limpiarHistorial,
  restaurarHistorial,
  procesandoHistorial
}) {
  return (
          <div className="plurione-surface-card plurione-history-panel">

            <div className="plurione-history-toolbar">

              <h4 className="plurione-history-title">Registro Detallado (Auditoría)</h4>

              <div className="plurione-history-actions">

                <button onClick={exportarPDF} className="plurione-outline-button plurione-outline-button--pdf">📄 Descargar PDF</button>

                <button onClick={limpiarHistorial} disabled={procesandoHistorial} title="Archivar sin borrar registros" className="plurione-outline-button plurione-outline-button--archive">🗑️ Vaciar Tabla</button>
                <button
                  onClick={restaurarHistorial}
                  disabled={procesandoHistorial}
                  className="plurione-outline-button plurione-outline-button--restore"
                >
                  Restaurar historial
                </button>

              </div>

            </div>

            <table className="plurione-history-table">

              <thead>

                <tr className="plurione-history-head-row">

                  <th className="plurione-history-index-heading">N.º</th><th>Pipeline</th><th>Métrica</th><th>Valor</th><th>Estado</th><th>IA Diagnóstico</th>

                </tr>

              </thead>

              <tbody>

                {anomalias.map((a, indice) => (

                  <tr key={a.id} className="plurione-history-row">

                    <td className="plurione-history-index">#{indice + 1}</td>

                    <td>{a.pipeline_name}</td>

                    <td className="plurione-history-metric-type">{a.metric_type}</td>

                    <td className="plurione-history-value">{a.value}</td>

                    <td><span className="plurione-history-status" data-status={a.status}>{a.status}</span></td>

                    <td className="plurione-history-recommendation">{a.ai_recommendation}</td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>
  );
}
