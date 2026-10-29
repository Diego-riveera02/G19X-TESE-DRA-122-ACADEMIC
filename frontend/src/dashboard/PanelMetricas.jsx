import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, PieChart, Pie, Cell } from 'recharts';

export default function PanelMetricas({ anomalias, metricasEnVivo }) {

  const latenciasHistoricas = [...anomalias].reverse().filter(a => a.metric_type === "latencia_ms").slice(-10);

  const latencias = metricasEnVivo.latencia_ms?.type === 'metrica_normal'
    ? [...latenciasHistoricas.slice(-9), metricasEnVivo.latencia_ms]
    : latenciasHistoricas;

  const calidadHistoricas = [...anomalias].reverse().filter(a => a.metric_type === "datos_corruptos_%").slice(-10);

  const calidad = metricasEnVivo["datos_corruptos_%"]?.type === 'metrica_normal'
    ? [...calidadHistoricas.slice(-9), metricasEnVivo["datos_corruptos_%"]]
    : calidadHistoricas;

  const fallosTotal = anomalias.filter(a => a.metric_type === "tasa_fallos_%").length;

  const fallosCriticos = anomalias.filter(a => a.metric_type === "tasa_fallos_%" && a.status === "Critico").length;

  const datosDona = [

    { name: 'Éxito', value: Math.max(1, fallosTotal - fallosCriticos) },

    { name: 'Fallos Críticos', value: fallosCriticos }

  ];

  const coloresDona = ['#457B9D', '#E63946'];

  const ultimoLatencia = metricasEnVivo.latencia_ms || anomalias.find(a => a.metric_type === "latencia_ms");

  const ultimoCalidad = metricasEnVivo["datos_corruptos_%"] || anomalias.find(a => a.metric_type === "datos_corruptos_%");

  const ultimoFallo = metricasEnVivo["tasa_fallos_%"] || anomalias.find(a => a.metric_type === "tasa_fallos_%");

  return (
    <>
            {/* LATENCIA */}

            <div className="plurione-chart-card">

              <div className="plurione-metric-chart">

                <h4 className="plurione-metric-title">Latencia de Red (ms)</h4>

                <ResponsiveContainer width="100%" height="85%">

                  <LineChart data={latencias}>

                    <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />

                    <XAxis dataKey="id" hide />

                    <YAxis stroke="#a8a8a8" fontSize={10} width={30} />

                    <Tooltip contentStyle={{ backgroundColor: '#1a1a1d', border: '1px solid #333' }} />

                    <Line type="monotone" dataKey="value" stroke="#E5B80B" strokeWidth={2} dot={{r:3}} isAnimationActive={false} />

                  </LineChart>

                </ResponsiveContainer>

              </div>

              <div className="plurione-metric-state">

                <span className="plurione-metric-status" data-status={ultimoLatencia?.status}>

                  ESTADO: {ultimoLatencia ? ultimoLatencia.status : 'Normal'}

                </span>

              </div>

              <div className="plurione-metric-details">

                <strong className="plurione-metric-diagnosis-title">Diagnóstico automático (Latencia): </strong>

                <span className="plurione-metric-diagnosis-text">{ultimoLatencia ? ultimoLatencia.ai_recommendation : 'Esperando datos...'}</span>

              </div>

            </div>

            {/* CALIDAD */}

            <div className="plurione-chart-card">

              <div className="plurione-metric-chart">

                <h4 className="plurione-metric-title">Calidad (% Corruptos)</h4>

                <ResponsiveContainer width="100%" height="85%">

                  <BarChart data={calidad}>

                    <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />

                    <XAxis dataKey="id" hide />

                    <YAxis stroke="#a8a8a8" fontSize={10} width={30} />

                    <Tooltip contentStyle={{ backgroundColor: '#1a1a1d', border: '1px solid #333' }} />

                    <Bar dataKey="value" fill="#457B9D" isAnimationActive={false} />

                  </BarChart>

                </ResponsiveContainer>

              </div>

              <div className="plurione-metric-state">

                <span className="plurione-metric-status" data-status={ultimoCalidad?.status}>

                  ESTADO: {ultimoCalidad ? ultimoCalidad.status : 'Normal'}

                </span>

              </div>

              <div className="plurione-metric-details">

                <strong className="plurione-metric-diagnosis-title">Diagnóstico automático (Calidad): </strong>

                <span className="plurione-metric-diagnosis-text">{ultimoCalidad ? ultimoCalidad.ai_recommendation : 'Esperando datos...'}</span>

              </div>

            </div>

            {/* TASA DE FALLOS */}

            <div className="plurione-chart-card">

              <div className="plurione-metric-chart">

                <h4 className="plurione-metric-title">Tasa de Fallos</h4>

                <ResponsiveContainer width="100%" height="85%">

                  <PieChart>

                    <Pie data={datosDona} innerRadius={40} outerRadius={60} dataKey="value" stroke="none">

                      {datosDona.map((entry, index) => <Cell key={`cell-${index}`} fill={coloresDona[index]} />)}

                    </Pie>

                    <Tooltip />

                  </PieChart>

                </ResponsiveContainer>

              </div>

              <div className="plurione-metric-state">

                <span className="plurione-metric-status" data-status={ultimoFallo?.status}>

                  ESTADO: {ultimoFallo ? ultimoFallo.status : 'Normal'}

                </span>

              </div>

              <div className="plurione-metric-details">

                <strong className="plurione-metric-diagnosis-title">Diagnóstico automático (Fallos): </strong>

                <span className="plurione-metric-diagnosis-text">{ultimoFallo ? ultimoFallo.ai_recommendation : 'Esperando datos...'}</span>

              </div>

            </div>

            {/* FEED DE ALERTAS */}

            <div className="plurione-feed-panel plurione-surface-card">

              <h4 className="plurione-feed-heading">Feed de Alertas Recientes</h4>

              <div className="plurione-feed-list">

                {anomalias.slice(0, 5).map(a => (

                  <div key={a.id} className="plurione-feed-item">

                    <span className="plurione-feed-time">{a.timestamp ? new Date(a.timestamp).toLocaleTimeString() : '—'}</span> |

                    <strong className="plurione-feed-status" data-status={a.status}>{a.status}</strong> en {a.pipeline_name}: {a.metric_type} = {a.value}

                  </div>

                ))}

                {anomalias.length === 0 && <div className="plurione-feed-empty">Sin alertas registradas.</div>}

              </div>

            </div>
    </>
  );
}
