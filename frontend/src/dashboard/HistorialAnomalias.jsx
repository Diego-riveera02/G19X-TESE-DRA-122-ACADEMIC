export default function HistorialAnomalias({
  anomalias,
  exportarPDF,
  limpiarHistorial,
  restaurarHistorial,
  procesandoHistorial
}) {
  return (
          <div style={{ background: '#111217', padding: '20px', borderRadius: '8px', border: '1px solid #333' }}>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>

              <h4 style={{ margin: 0, color: '#E5B80B' }}>Registro Detallado (Auditoría)</h4>

              <div style={{ display: 'flex', gap: '10px' }}>

                <button onClick={exportarPDF} style={{ background: 'transparent', color: '#457B9D', border: '1px solid #457B9D', padding: '5px 15px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>📄 Descargar PDF</button>

                <button onClick={limpiarHistorial} disabled={procesandoHistorial} title="Archivar sin borrar registros" style={{ background: 'transparent', color: '#E63946', border: '1px solid #E63946', padding: '5px 15px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>🗑️ Vaciar Tabla</button>
                <button
                  onClick={restaurarHistorial}
                  disabled={procesandoHistorial}
                  style={{
                    background: 'transparent',
                    color: '#2A9D8F',
                    border: '1px solid #2A9D8F',
                    padding: '5px 15px',
                    borderRadius: '4px',
                    cursor: procesandoHistorial ? 'wait' : 'pointer'
                  }}
                >
                  Restaurar historial
                </button>

              </div>

            </div>

            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9em' }}>

              <thead>

                <tr style={{ borderBottom: '2px solid #333', color: '#888' }}>

                  <th style={{ padding: '10px' }}>N.º</th><th>Pipeline</th><th>Métrica</th><th>Valor</th><th>Estado</th><th>IA Diagnóstico</th>

                </tr>

              </thead>

              <tbody>

                {anomalias.map((a, indice) => (

                  <tr key={a.id} style={{ borderBottom: '1px solid #1a1a1d' }}>

                    <td style={{ padding: '10px', color: '#E5B80B' }}>#{indice + 1}</td>

                    <td>{a.pipeline_name}</td>

                    <td style={{ color: '#888' }}>{a.metric_type}</td>

                    <td style={{ color: '#E63946', fontWeight: 'bold' }}>{a.value}</td>

                    <td><span style={{ background: a.status === 'Critico' ? '#8B0000' : a.status === 'Alerta' ? '#D4A017' : '#006400', padding: '4px 8px', borderRadius: '4px', color: '#fff', fontSize: '0.8em' }}>{a.status}</span></td>

                    <td style={{ maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', color: '#a8a8a8' }}>{a.ai_recommendation}</td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>
  );
}
