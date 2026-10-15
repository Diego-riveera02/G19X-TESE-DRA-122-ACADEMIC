import { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation, Link } from 'react-router-dom';
import axios from 'axios';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, PieChart, Pie, Cell } from 'recharts';
import ParticlesBackground from './ParticlesBackground';
import JarvisOnboarding from './JarvisOnboarding';
import Login from './Login';
import Registro from './Registro';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

// === PANTALLA DE VERIFICACIÓN ===
function Verificar() {
  const location = useLocation();
  const [correo, setCorreo] = useState(location.state?.email || '');
  const [codigo, setCodigo] = useState('');
  const [mensaje, setMensaje] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const manejarVerificacion = async (e) => {
    e.preventDefault();
    setError(''); setMensaje('');
    try {
      await axios.post('http://127.0.0.1:8000/verificar/', { correo, codigo });
      setMensaje('¡Cuenta verificada exitosamente!');
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) { setError(err.response?.data?.detail || 'Código incorrecto.'); }
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: '#0b0c10', overflow: 'hidden' }}>
      <ParticlesBackground />
      <div style={{ position: 'relative', zIndex: 10, width: '400px', padding: '40px', backgroundColor: 'rgba(26, 26, 29, 0.9)', border: '1px solid #E5B80B', borderRadius: '10px', boxShadow: '0 0 30px rgba(229,184,11,0.2)', color: '#c5c6c7', textAlign: 'center' }}>
        <h2 style={{ color: '#E5B80B', marginBottom: '5px' }}>Verificación</h2>
        <p style={{ color: '#888', fontSize: '0.9em', marginBottom: '20px' }}>Ingresa el código de 6 dígitos que enviamos a tu correo.</p>
        {error && <div style={{ color: '#ff4444', marginBottom: '15px' }}>{error}</div>}
        {mensaje && <div style={{ color: '#4BB543', marginBottom: '15px' }}>{mensaje}</div>}
        <form onSubmit={manejarVerificacion} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          <input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} required placeholder="Confirma tu Correo" style={{ padding: '12px', backgroundColor: '#111217', border: '1px solid #444', color: '#fff', borderRadius: '4px' }} />
          <input type="text" value={codigo} onChange={(e) => setCodigo(e.target.value)} required placeholder="Código (Ej. 123456)" maxLength="6" style={{ padding: '12px', backgroundColor: '#111217', border: '1px solid #E5B80B', color: '#E5B80B', fontWeight: 'bold', textAlign: 'center', letterSpacing: '5px', fontSize: '1.2em', borderRadius: '4px' }} />
          <button type="submit" style={{ background: '#E5B80B', color: '#0b0c10', border: 'none', padding: '12px', fontWeight: 'bold', borderRadius: '4px', cursor: 'pointer' }}>Activar Cuenta</button>
        </form>
        <div style={{ marginTop: '20px' }}><Link to="/login" style={{ color: '#888', textDecoration: 'none', fontSize: '0.9em' }}>Volver al Login</Link></div>
      </div>
    </div>
  );
}

// === PANTALLA DE RECUPERACIÓN DE CONTRASEÑA ===
function RecuperarPassword() {
  const [correo, setCorreo] = useState('');
  const [nuevaPassword, setNuevaPassword] = useState('');
  const [codigo, setCodigo] = useState('');
  const [mensaje, setMensaje] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const manejarRecuperacion = async (e) => {
    e.preventDefault();
    setError(''); setMensaje('');
    try {
      await axios.post('http://127.0.0.1:8000/recuperar-password/', { correo, codigo, nueva_password: nuevaPassword });
      setMensaje('Contraseña actualizada correctamente.');
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) { setError(err.response?.data?.detail || 'Error al actualizar contraseña.'); }
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: '#0b0c10', overflow: 'hidden' }}>
      <ParticlesBackground />
      <div style={{ position: 'relative', zIndex: 10, width: '400px', padding: '40px', backgroundColor: 'rgba(26, 26, 29, 0.9)', border: '1px solid #E5B80B', borderRadius: '10px', boxShadow: '0 0 30px rgba(229,184,11,0.2)', color: '#c5c6c7', textAlign: 'center' }}>
        <h2 style={{ color: '#E5B80B', marginBottom: '5px' }}>Recuperar Acceso</h2>
        <p style={{ color: '#888', fontSize: '0.9em', marginBottom: '20px' }}>Ingresa tu correo, el código de verificación y tu nueva contraseña.</p>
        {error && <div style={{ color: '#ff4444', marginBottom: '15px' }}>{error}</div>}
        {mensaje && <div style={{ color: '#4BB543', marginBottom: '15px' }}>{mensaje}</div>}
        <form onSubmit={manejarRecuperacion} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          <input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} required placeholder="Correo registrado" style={{ padding: '12px', backgroundColor: '#111217', border: '1px solid #444', color: '#fff', borderRadius: '4px' }} />
          <input type="text" value={codigo} onChange={(e) => setCodigo(e.target.value)} required placeholder="Código de 6 dígitos" maxLength="6" style={{ padding: '12px', backgroundColor: '#111217', border: '1px solid #444', color: '#fff', borderRadius: '4px', textAlign: 'center', letterSpacing: '3px' }} />
          <input type="password" value={nuevaPassword} onChange={(e) => setNuevaPassword(e.target.value)} required placeholder="Nueva Contraseña" style={{ padding: '12px', backgroundColor: '#111217', border: '1px solid #444', color: '#fff', borderRadius: '4px' }} />
          <button type="submit" style={{ background: '#457B9D', color: '#fff', border: 'none', padding: '12px', fontWeight: 'bold', borderRadius: '4px', cursor: 'pointer' }}>Actualizar Contraseña</button>
        </form>
        <div style={{ marginTop: '20px' }}><Link to="/login" style={{ color: '#888', textDecoration: 'none', fontSize: '0.9em' }}>Volver al Login</Link></div>
      </div>
    </div>
  );
}

// =================================================================
// 2. APLICACIÓN PRINCIPAL (Dashboard y Gráficas)
// =================================================================
function PluriOneApp() {
  const [vista, setVista] = useState('dashboard');
  const [anomalias, setAnomalias] = useState([]);
  
  const [idOcultosHasta, setIdOcultosHasta] = useState(() => {
    const userId = localStorage.getItem('usuario_nombre');
    return parseInt(localStorage.getItem(`plurione_id_ocultos_${userId}`) || '0', 10);
  });
  
  const [mensajes, setMensajes] = useState([{ role: 'jarvis', text: 'Sistemas en línea. Escuchando telemetría automáticamente. Listo para diagnósticos.' }]);
  const [pregunta, setPregunta] = useState('');
  const chatEndRef = useRef(null);

  const nombreUsuario = localStorage.getItem('usuario_nombre') || 'Usuario';
  const token = localStorage.getItem('token_plurione');
  const navigate = useNavigate();

  // Conexión WebSockets y carga inicial
  useEffect(() => {
    if (!token) { navigate('/login'); return; }
    
    axios.get('http://127.0.0.1:8000/anomalias/', { headers: { Authorization: `Bearer ${token}` } }).then(res => {
      setAnomalias(res.data.filter(item => item.id > idOcultosHasta).sort((a, b) => b.id - a.id));
    }).catch(() => navigate('/login'));
    
    const ws = new WebSocket('ws://127.0.0.1:8000/ws/anomalias');
    ws.onmessage = (event) => {
      const nueva = JSON.parse(event.data);
      setAnomalias(prev => [nueva, ...prev].sort((a, b) => b.id - a.id));
    };
    return () => ws.close();
  }, [idOcultosHasta, token, navigate]);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [mensajes]);

  const enviarPregunta = async () => {
    if (!pregunta.trim()) return;
    const ultimoCritico = anomalias.find(a => a.status === 'Critico') || { id: 0, ai_recommendation: '' };
    setMensajes(prev => [...prev, { role: 'user', text: pregunta }]); setPregunta('');
    try {
      const response = await axios.post('http://127.0.0.1:8000/chat/', { anomaly_id: ultimoCritico.id, pregunta: pregunta, contexto_anomalia: ultimoCritico.ai_recommendation }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMensajes(prev => [...prev, { role: 'jarvis', text: response.data.respuesta }]);
    } catch (error) { setMensajes(prev => [...prev, { role: 'jarvis', text: "Error de red." }]); }
  };

  const limpiarHistorial = () => {
    if (anomalias.length > 0) {
      const maxId = Math.max(...anomalias.map(a => a.id));
      setIdOcultosHasta(maxId); 
      localStorage.setItem(`plurione_id_ocultos_${nombreUsuario}`, maxId.toString());
    }
    setAnomalias([]);
  };

  const cerrarSesion = () => { 
    localStorage.removeItem('token_plurione');
    localStorage.removeItem('usuario_nombre');
    navigate('/login'); 
  };

  const exportarPDF = () => {
    if (anomalias.length === 0) {
      alert("No hay datos en el historial para exportar.");
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

    const fechaArchivo = new Date().toLocaleDateString().replace(/\//g, '-');
    doc.save(`Bitacora_PluriOne_${fechaArchivo}.pdf`);
  };

  const latencias = [...anomalias].reverse().filter(a => a.metric_type === "latencia_ms").slice(-10);
  const calidad = [...anomalias].reverse().filter(a => a.metric_type === "datos_corruptos_%").slice(-10);
  
  const fallosTotal = anomalias.filter(a => a.metric_type === "tasa_fallos_%").length;
  const fallosCriticos = anomalias.filter(a => a.metric_type === "tasa_fallos_%" && a.status === "Critico").length;
  const datosDona = [
    { name: 'Éxito', value: Math.max(1, fallosTotal - fallosCriticos) },
    { name: 'Fallos Críticos', value: fallosCriticos }
  ];
  const coloresDona = ['#457B9D', '#E63946'];

  const ultimoLatencia = anomalias.find(a => a.metric_type === "latencia_ms");
  const ultimoCalidad = anomalias.find(a => a.metric_type === "datos_corruptos_%");
  const ultimoFallo = anomalias.find(a => a.metric_type === "tasa_fallos_%");

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100%', overflow: 'hidden', backgroundColor: '#0b0c10', color: '#c5c6c7', fontFamily: '"Segoe UI", Roboto, sans-serif' }}>
      
      {/* 1. CABECERA */}
      <div style={{ height: '70px', padding: '0 30px', backgroundColor: '#111217', borderBottom: '1px solid #333', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <div style={{ width: '35px', height: '35px', borderRadius: '50%', backgroundColor: '#457B9D', display: 'flex', justifyContent: 'center', alignItems: 'center', fontWeight: 'bold', color: '#fff' }}>
            {nombreUsuario.charAt(0).toUpperCase()}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontWeight: 'bold', color: '#E5B80B', fontSize: '0.9em' }}>{nombreUsuario}</span>
            <button onClick={cerrarSesion} style={{ background: 'none', border: 'none', color: '#E63946', cursor: 'pointer', padding: 0, fontSize: '0.75em', textAlign: 'left' }}>Cerrar Sesión</button>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '20px' }}>
          <button onClick={() => setVista('dashboard')} style={{ background: vista === 'dashboard' ? 'rgba(229,184,11,0.1)' : 'transparent', color: vista === 'dashboard' ? '#E5B80B' : '#888', border: 'none', borderBottom: vista === 'dashboard' ? '2px solid #E5B80B' : '2px solid transparent', padding: '10px 20px', cursor: 'pointer', fontWeight: 'bold', fontSize: '1em' }}>Datos (Dashboard)</button>
          <button onClick={() => setVista('historial')} style={{ background: vista === 'historial' ? 'rgba(229,184,11,0.1)' : 'transparent', color: vista === 'historial' ? '#E5B80B' : '#888', border: 'none', borderBottom: vista === 'historial' ? '2px solid #E5B80B' : '2px solid transparent', padding: '10px 20px', cursor: 'pointer', fontWeight: 'bold', fontSize: '1em' }}>Historial</button>
        </div>

        <h2 style={{ margin: 0, color: '#E5B80B', letterSpacing: '2px', textTransform: 'uppercase' }}>PLURIONE</h2>
      </div>

      {/* 2. ÁREA DE TRABAJO */}
      <div style={{ flex: 1, padding: '20px', overflowY: 'auto' }}>
        
        {vista === 'dashboard' && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gridTemplateRows: 'auto auto', gap: '20px', height: '100%' }}>
            
            {/* LATENCIA */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
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
                <strong style={{ color: '#E5B80B' }}>Diagnóstico IA (Latencia): </strong>
                <span style={{ color: '#a8a8a8' }}>{ultimoLatencia ? ultimoLatencia.ai_recommendation : 'Esperando datos...'}</span>
              </div>
            </div>

            {/* CALIDAD */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
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
                <strong style={{ color: '#E5B80B' }}>Diagnóstico IA (Calidad): </strong>
                <span style={{ color: '#a8a8a8' }}>{ultimoCalidad ? ultimoCalidad.ai_recommendation : 'Esperando datos...'}</span>
              </div>
            </div>

            {/* TASA DE FALLOS */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
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
                <strong style={{ color: '#E5B80B' }}>Diagnóstico IA (Fallos): </strong>
                <span style={{ color: '#a8a8a8' }}>{ultimoFallo ? ultimoFallo.ai_recommendation : 'Esperando datos...'}</span>
              </div>
            </div>

            {/* FEED DE ALERTAS */}
            <div style={{ gridColumn: 'span 2', background: '#111217', padding: '20px', borderRadius: '8px', border: '1px solid #333', height: '280px', display: 'flex', flexDirection: 'column' }}>
              <h4 style={{ margin: '0 0 10px 0', color: '#E5B80B' }}>Feed de Alertas Recientes</h4>
              <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.85em' }}>
                {anomalias.slice(0, 5).map(a => (
                  <div key={a.id} style={{ borderBottom: '1px solid #1a1a1d', paddingBottom: '5px' }}>
                    <span style={{ color: '#888' }}>{new Date().toLocaleTimeString()}</span> | 
                    <strong style={{ color: a.status === 'Critico' ? '#E63946' : a.status === 'Alerta' ? '#D4A017' : '#4BB543', marginLeft: '5px' }}>{a.status}</strong> en {a.pipeline_name}: {a.metric_type} = {a.value}
                  </div>
                ))}
                {anomalias.length === 0 && <div style={{ color: '#888' }}>Sin alertas registradas.</div>}
              </div>
            </div>

            {/* JARVIS PANEL */}
            <div style={{ gridColumn: '3', background: '#111217', padding: '15px', borderRadius: '8px', border: '1px solid #E5B80B', height: '280px', display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <strong style={{ color: '#E5B80B', fontSize: '0.9em' }}>J.A.R.V.I.S.</strong>
                <span style={{ color: '#4BB543', fontSize: '0.7em', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <span style={{ display: 'inline-block', width: '8px', height: '8px', backgroundColor: '#4BB543', borderRadius: '50%' }}></span>
                  ● EN VIVO
                </span>
              </div>

              <div style={{ flex: 1, overflowY: 'auto', background: '#0b0c10', padding: '10px', borderRadius: '4px', marginBottom: '10px', fontSize: '0.8em', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {mensajes.map((m, i) => (
                  <div key={i} style={{ color: m.role === 'jarvis' ? '#E5B80B' : '#fff', textAlign: m.role === 'jarvis' ? 'left' : 'right' }}>{m.text}</div>
                ))}
                <div ref={chatEndRef} />
              </div>
              <div style={{ display: 'flex', gap: '5px' }}>
                <input type="text" value={pregunta} onChange={(e) => setPregunta(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && enviarPregunta()} placeholder="Preguntar..." style={{ flex: 1, padding: '5px', background: '#1a1a1d', color: '#fff', border: '1px solid #333', borderRadius: '4px', fontSize: '0.8em' }} />
                <button onClick={enviarPregunta} style={{ background: '#E5B80B', border: 'none', padding: '0 10px', borderRadius: '4px', fontWeight: 'bold' }}>&gt;</button>
              </div>
            </div>

          </div>
        )}

        {/* PESTAÑA HISTORIAL */}
        {vista === 'historial' && (
          <div style={{ background: '#111217', padding: '20px', borderRadius: '8px', border: '1px solid #333' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
              <h4 style={{ margin: 0, color: '#E5B80B' }}>Registro Detallado (Auditoría)</h4>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button onClick={exportarPDF} style={{ background: 'transparent', color: '#457B9D', border: '1px solid #457B9D', padding: '5px 15px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>📄 Descargar PDF</button>
                <button onClick={limpiarHistorial} style={{ background: 'transparent', color: '#E63946', border: '1px solid #E63946', padding: '5px 15px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>🗑️ Vaciar Tabla</button>
              </div>
            </div>
            
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9em' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #333', color: '#888' }}>
                  <th style={{ padding: '10px' }}>ID</th><th>Pipeline</th><th>Métrica</th><th>Valor</th><th>Estado</th><th>IA Diagnóstico</th>
                </tr>
              </thead>
              <tbody>
                {anomalias.map(a => (
                  <tr key={a.id} style={{ borderBottom: '1px solid #1a1a1d' }}>
                    <td style={{ padding: '10px', color: '#E5B80B' }}>#{a.id}</td>
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
        )}
        
        <JarvisOnboarding />

      </div>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/registro" element={<Registro />} />
        <Route path="/verificar" element={<Verificar />} />
        <Route path="/recuperar" element={<RecuperarPassword />} />
        <Route path="/app" element={<PluriOneApp />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}