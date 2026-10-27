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

            <div className="plurione-chart-card" style={{ display: 'flex', flexDirection: 'column', gap: '15px', minWidth: 0 }}>

              <div style={{ background: '#111217', padding: '20px', borderRadius: '8px', border: '1px solid #333', height: '250px' }}>

                <h4 style={{ margin: '0 0 15px 0', color: '#fff', textAlign: 'center' }}>Latencia de Red (ms)</h4>

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

              <div style={{ background: '#111217', padding: '15px', borderRadius: '8px', border: '1px solid #333', textAlign: 'center' }}>

                <span style={{ background: ultimoLatencia?.status === 'Critico' ? '#8B0000' : ultimoLatencia?.status === 'Alerta' ? '#D4A017' : '#006400', padding: '6px 12px', borderRadius: '4px', color: '#fff', fontWeight: 'bold' }}>

                  ESTADO: {ultimoLatencia ? ultimoLatencia.status : 'Normal'}

                </span>

              </div>

              <div style={{ background: '#111217', padding: '15px', borderRadius: '8px', border: '1px solid #333', height: '110px', overflowY: 'auto', fontSize: '0.85em' }}>

                <strong style={{ color: '#E5B80B' }}>Diagnóstico automático (Latencia): </strong>

                <span style={{ color: '#a8a8a8' }}>{ultimoLatencia ? ultimoLatencia.ai_recommendation : 'Esperando datos...'}</span>

              </div>

            </div>

            {/* CALIDAD */}

            <div className="plurione-chart-card" style={{ display: 'flex', flexDirection: 'column', gap: '15px', minWidth: 0 }}>

              <div style={{ background: '#111217', padding: '20px', borderRadius: '8px', border: '1px solid #333', height: '250px' }}>

                <h4 style={{ margin: '0 0 15px 0', color: '#fff', textAlign: 'center' }}>Calidad (% Corruptos)</h4>

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

              <div style={{ background: '#111217', padding: '15px', borderRadius: '8px', border: '1px solid #333', textAlign: 'center' }}>

                <span style={{ background: ultimoCalidad?.status === 'Critico' ? '#8B0000' : ultimoCalidad?.status === 'Alerta' ? '#D4A017' : '#006400', padding: '6px 12px', borderRadius: '4px', color: '#fff', fontWeight: 'bold' }}>

                  ESTADO: {ultimoCalidad ? ultimoCalidad.status : 'Normal'}

                </span>

              </div>

              <div style={{ background: '#111217', padding: '15px', borderRadius: '8px', border: '1px solid #333', height: '110px', overflowY: 'auto', fontSize: '0.85em' }}>

                <strong style={{ color: '#E5B80B' }}>Diagnóstico automático (Calidad): </strong>

                <span style={{ color: '#a8a8a8' }}>{ultimoCalidad ? ultimoCalidad.ai_recommendation : 'Esperando datos...'}</span>

              </div>

            </div>

            {/* TASA DE FALLOS */}

            <div className="plurione-chart-card" style={{ display: 'flex', flexDirection: 'column', gap: '15px', minWidth: 0 }}>

              <div style={{ background: '#111217', padding: '20px', borderRadius: '8px', border: '1px solid #333', height: '250px' }}>

                <h4 style={{ margin: '0 0 15px 0', color: '#fff', textAlign: 'center' }}>Tasa de Fallos</h4>

                <ResponsiveContainer width="100%" height="85%">

                  <PieChart>

                    <Pie data={datosDona} innerRadius={40} outerRadius={60} dataKey="value" stroke="none">

                      {datosDona.map((entry, index) => <Cell key={`cell-${index}`} fill={coloresDona[index]} />)}

                    </Pie>

                    <Tooltip />

                  </PieChart>

                </ResponsiveContainer>

              </div>

              <div style={{ background: '#111217', padding: '15px', borderRadius: '8px', border: '1px solid #333', textAlign: 'center' }}>

                <span style={{ background: ultimoFallo?.status === 'Critico' ? '#8B0000' : ultimoFallo?.status === 'Alerta' ? '#D4A017' : '#006400', padding: '6px 12px', borderRadius: '4px', color: '#fff', fontWeight: 'bold' }}>

                  ESTADO: {ultimoFallo ? ultimoFallo.status : 'Normal'}

                </span>

              </div>

              <div style={{ background: '#111217', padding: '15px', borderRadius: '8px', border: '1px solid #333', height: '110px', overflowY: 'auto', fontSize: '0.85em' }}>

                <strong style={{ color: '#E5B80B' }}>Diagnóstico automático (Fallos): </strong>

                <span style={{ color: '#a8a8a8' }}>{ultimoFallo ? ultimoFallo.ai_recommendation : 'Esperando datos...'}</span>

              </div>

            </div>

            {/* FEED DE ALERTAS */}

            <div className="plurione-feed-panel" style={{ background: '#111217', padding: '20px', borderRadius: '8px', border: '1px solid #333', height: '450px', display: 'flex', flexDirection: 'column', minWidth: 0, maxWidth: '100%', boxSizing: 'border-box', overflow: 'hidden' }}>

              <h4 style={{ margin: '0 0 10px 0', color: '#E5B80B' }}>Feed de Alertas Recientes</h4>

              <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.85em' }}>

                {anomalias.slice(0, 5).map(a => (

                  <div key={a.id} style={{ borderBottom: '1px solid #1a1a1d', paddingBottom: '5px' }}>

                    <span style={{ color: '#888' }}>{a.timestamp ? new Date(a.timestamp).toLocaleTimeString() : '—'}</span> |

                    <strong style={{ color: a.status === 'Critico' ? '#E63946' : a.status === 'Alerta' ? '#D4A017' : '#4BB543', marginLeft: '5px' }}>{a.status}</strong> en {a.pipeline_name}: {a.metric_type} = {a.value}

                  </div>

                ))}

                {anomalias.length === 0 && <div style={{ color: '#888' }}>Sin alertas registradas.</div>}

              </div>

            </div>
    </>
  );
}
