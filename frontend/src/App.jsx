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

import ReactMarkdown from 'react-markdown';

import remarkGfm from 'remark-gfm';

// Las tablas de Markdown no pueden agrandar la cuadrícula ni la página.

function RespuestaJarvis({ texto }) {

  return (

    <div style={{ width: '100%', minWidth: 0, maxWidth: '100%', color: '#d7d9dd', lineHeight: 1.6, overflowWrap: 'break-word' }}>

      <ReactMarkdown

        remarkPlugins={[remarkGfm]}

        components={{

          h1: ({ node, ...props }) => <h2 {...props} style={{ color: '#f2c94c', fontSize: '1.05rem', margin: '12px 0 8px', lineHeight: 1.35 }} />,

          h2: ({ node, ...props }) => <h2 {...props} style={{ color: '#f2c94c', fontSize: '1.02rem', margin: '14px 0 8px', lineHeight: 1.4 }} />,

          h3: ({ node, ...props }) => <h3 {...props} style={{ color: '#f2c94c', fontSize: '0.95rem', margin: '12px 0 6px' }} />,

          p: ({ node, ...props }) => <p {...props} style={{ margin: '6px 0 10px', lineHeight: 1.65 }} />,

          strong: ({ node, ...props }) => <strong {...props} style={{ color: '#f2c94c', fontWeight: 700 }} />,

          ul: ({ node, ...props }) => <ul {...props} style={{ paddingLeft: '20px', margin: '8px 0' }} />,

          ol: ({ node, ...props }) => <ol {...props} style={{ paddingLeft: '20px', margin: '8px 0' }} />,

          li: ({ node, ...props }) => <li {...props} style={{ marginBottom: '5px' }} />,

          blockquote: ({ node, ...props }) => <blockquote {...props} style={{ margin: '10px 0', padding: '8px 12px', borderLeft: '3px solid #E5B80B', background: '#16191f' }} />,

          hr: () => <hr style={{ border: 0, borderTop: '1px solid #333944', margin: '14px 0' }} />,

          pre: ({ node, ...props }) => <pre {...props} style={{ maxWidth: '100%', overflowX: 'auto', padding: '10px', borderRadius: '6px', background: '#171a20', fontSize: '0.78rem' }} />,

          code: ({ node, ...props }) => <code {...props} style={{ overflowWrap: 'anywhere', background: '#20232b', borderRadius: '3px', padding: '1px 3px', fontSize: '0.83em' }} />,

          table: ({ node, ...props }) => (

            <div role="region" aria-label="Tabla del diagnóstico, desplazable horizontalmente" tabIndex={0}

              style={{ width: '100%', maxWidth: '100%', minWidth: 0, overflowX: 'auto', margin: '10px 0 14px', border: '1px solid #30333a', borderRadius: '6px' }}>

              <table {...props} style={{ width: '100%', minWidth: '540px', tableLayout: 'fixed', borderCollapse: 'collapse', fontSize: '0.8rem', textAlign: 'left' }} />

            </div>

          ),

          th: ({ node, ...props }) => <th {...props} style={{ background: '#20232b', color: '#f2c94c', borderBottom: '1px solid #66581f', padding: '8px 10px', textAlign: 'left', whiteSpace: 'normal', overflowWrap: 'anywhere' }} />,

          td: ({ node, ...props }) => <td {...props} style={{ borderTop: '1px solid #30333a', padding: '8px 10px', verticalAlign: 'top', overflowWrap: 'anywhere', wordBreak: 'normal' }} />

        }}

      >

        {texto}

      </ReactMarkdown>

    </div>

  );

}

// === PANTALLA DE VERIFICACIÓN ===
function Verificar() {
  const location = useLocation();
  const navigate = useNavigate();
  const [correo, setCorreo] = useState(location.state?.email || '');
  const [codigo, setCodigo] = useState('');
  const [mensaje, setMensaje] = useState('');
  const [error, setError] = useState('');
  const [verificando, setVerificando] = useState(false);
  const [reenviando, setReenviando] = useState(false);
  const [verificado, setVerificado] = useState(false);

  const manejarVerificacion = async (e) => {
    e.preventDefault();
    if (verificando || verificado) return;
    setError('');
    setMensaje('');
    setVerificando(true);

    try {
      await axios.post('http://127.0.0.1:8000/verificar/', {
        correo: correo.trim(),
        codigo
      });
      setVerificado(true);
      setMensaje('¡Cuenta verificada exitosamente! Redirigiendo al inicio de sesión...');
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo verificar el código. Intenta nuevamente.');
    } finally {
      setVerificando(false);
    }
  };

  const manejarReenvio = async () => {
    const correoSolicitado = correo.trim();
    if (!correoSolicitado || reenviando || verificando || verificado) return;

    setError('');
    setMensaje('');
    setReenviando(true);

    try {
      const respuesta = await axios.post('http://127.0.0.1:8000/reenviar-verificacion/', {
        correo: correoSolicitado
      });
      // La API da una respuesta genérica: no revela cuentas registradas
      // y solo envía un código nuevo si el anterior ya venció.
      setMensaje(
        respuesta.data?.status ||
        'Si tu código ya venció, recibirás uno nuevo. Revisa tu correo y spam.'
      );
    } catch (err) {
      const detalle = err.response?.data?.detail;
      setError(
        typeof detalle === 'string'
          ? detalle
          : 'No se pudo solicitar otro código. Espera un momento e inténtalo de nuevo.'
      );
    } finally {
      setReenviando(false);
    }
  };

  return (
    <div style={{ position: 'relative', width: '100%', minHeight: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: '#0b0c10', overflow: 'auto' }}>
      <ParticlesBackground />
      <div style={{ position: 'relative', zIndex: 10, width: '400px', maxWidth: 'calc(100% - 32px)', boxSizing: 'border-box', padding: '32px', margin: '20px auto', backgroundColor: 'rgba(26, 26, 29, 0.9)', border: '1px solid #E5B80B', borderRadius: '10px', boxShadow: '0 0 30px rgba(229,184,11,0.2)', color: '#c5c6c7', textAlign: 'center' }}>
        <h2 style={{ color: '#E5B80B', marginBottom: '5px' }}>Verificación</h2>
        <p style={{ color: '#aaa', fontSize: '0.9em', marginBottom: '20px' }}>Ingresa el código de 6 dígitos que enviamos a tu correo.</p>

        {error && <div role="alert" style={{ color: '#ff7474', marginBottom: '15px', overflowWrap: 'anywhere' }}>{error}</div>}
        {mensaje && <div role="status" style={{ color: '#85db92', marginBottom: '15px', overflowWrap: 'anywhere' }}>{mensaje}</div>}

        <form onSubmit={manejarVerificacion} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          <input
            type="email"
            aria-label="Correo electrónico"
            value={correo}
            onChange={(e) => setCorreo(e.target.value)}
            required
            disabled={verificado}
            placeholder="Confirma tu correo"
            style={{ padding: '12px', backgroundColor: '#111217', border: '1px solid #444', color: '#fff', borderRadius: '4px' }}
          />
          <input
            type="text"
            aria-label="Código de verificación de seis dígitos"
            inputMode="numeric"
            autoComplete="one-time-code"
            pattern="[0-9]{6}"
            value={codigo}
            onChange={(e) => setCodigo(e.target.value.replace(/\D/g, '').slice(0, 6))}
            required
            disabled={verificado}
            placeholder="Código de 6 dígitos"
            maxLength={6}
            style={{ padding: '12px', backgroundColor: '#111217', border: '1px solid #E5B80B', color: '#E5B80B', fontWeight: 'bold', textAlign: 'center', letterSpacing: '5px', fontSize: '1.2em', borderRadius: '4px' }}
          />
          <button
            type="submit"
            disabled={verificando || reenviando || verificado || codigo.length !== 6}
            style={{ background: '#E5B80B', color: '#0b0c10', border: 'none', padding: '12px', fontWeight: 'bold', borderRadius: '4px', cursor: verificando ? 'wait' : 'pointer', opacity: verificando || reenviando || verificado || codigo.length !== 6 ? 0.65 : 1 }}
          >
            {verificando ? 'Verificando...' : verificado ? 'Cuenta activada' : 'Activar cuenta'}
          </button>

          <button
            type="button"
            onClick={manejarReenvio}
            disabled={!correo.trim() || reenviando || verificando || verificado}
            style={{ background: 'transparent', color: '#E5B80B', border: '1px solid #E5B80B', padding: '11px', borderRadius: '4px', fontWeight: 'bold', cursor: reenviando ? 'wait' : 'pointer', opacity: !correo.trim() || reenviando || verificando || verificado ? 0.55 : 1 }}
          >
            {reenviando ? 'Solicitando código...' : 'Reenviar código'}
          </button>
        </form>

        <p style={{ color: '#aaa', fontSize: '0.8em', marginTop: '14px', lineHeight: 1.5 }}>
          El código dura 10 minutos. Si todavía está vigente, usa el que ya recibiste.
          Si venció, solicita uno nuevo y revisa también tu carpeta de spam.
        </p>
        <div style={{ marginTop: '20px' }}>
          <Link to="/login" style={{ color: '#aaa', textDecoration: 'none', fontSize: '0.9em' }}>Volver al Login</Link>
        </div>
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

  const [enviandoCodigo, setEnviandoCodigo] = useState(false);

  const navigate = useNavigate();

  const solicitarCodigoRecuperacion = async () => {

    if (!correo.trim() || enviandoCodigo) return;

    setError('');

    setMensaje('');

    setEnviandoCodigo(true);

    try {

      await axios.post(

        'http://127.0.0.1:8000/solicitar-recuperacion/',

        { correo: correo.trim() }

      );

      setMensaje('Solicitud procesada. Revisa tu correo y la carpeta de spam.');

    } catch (err) {

      setError(

        err.response?.data?.detail ||

        'No se pudo solicitar el código de recuperación.'

      );

    } finally {

      setEnviandoCodigo(false);

    }

  };

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

          <button

            type="button"

            onClick={solicitarCodigoRecuperacion}

            disabled={!correo.trim() || enviandoCodigo}

            style={{

              background: '#E5B80B',

              color: '#111',

              border: 'none',

              padding: '12px',

              fontWeight: 'bold',

              borderRadius: '4px',

              cursor: enviandoCodigo ? 'wait' : 'pointer',

              opacity: !correo.trim() || enviandoCodigo ? 0.6 : 1

            }}

          >

            {enviandoCodigo ? 'Solicitando código...' : 'Enviar código de recuperación'}

          </button>

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

  const chatContainerRef = useRef(null);

  const nombreUsuario = localStorage.getItem('usuario_nombre') || 'Usuario';

  const token = localStorage.getItem('token_plurione');

  const navigate = useNavigate();

  // Conexión WebSockets y carga inicial

  useEffect(() => {

    if (!token) { navigate('/login'); return; }

    axios.get('http://127.0.0.1:8000/anomalias/', { headers: { Authorization: `Bearer ${token}` } }).then(res => {

      setAnomalias(res.data.filter(item => item.id > idOcultosHasta).sort((a, b) => b.id - a.id));

    }).catch(() => navigate('/login'));

    // Conexion WebSocket autenticada mediante JWT

    const ws = new WebSocket('ws://127.0.0.1:8000/ws/anomalias');

    // Enviar el token al establecer la conexion

    ws.onopen = () => {

      ws.send(JSON.stringify({

        type: 'auth',

        token: token

      }));

    };

    // Recibir solamente las anomalias del usuario autenticado

    ws.onmessage = (event) => {

      try {

        const nueva = JSON.parse(event.data);

        // Confirmacion de autenticacion del servidor

        if (nueva.type === 'auth_ok') {

          console.log('WebSocket autenticado correctamente');

          return;

        }

        // Ignorar mensajes que no sean anomalias validas

        if (typeof nueva.id !== 'number') {

          return;

        }

        // Respetar el historial oculto del usuario

        if (nueva.id <= idOcultosHasta) {

          return;

        }

        setAnomalias(prev => {

          // Evitar registros duplicados

          if (prev.some(a => a.id === nueva.id)) {

            return prev;

          }

          return [nueva, ...prev].sort((a, b) => b.id - a.id);

        });

      } catch (error) {

        console.error('Error al procesar mensaje WebSocket');

      }

    };

    // Detectar cierre por autenticacion o politica de seguridad

    ws.onclose = (event) => {

      if (event.code === 1008) {

        console.warn('Conexion WebSocket rechazada o expirada');

      }

    };

    // Cerrar la conexion al desmontar el componente

    return () => ws.close();

  }, [idOcultosHasta, token, navigate]);

  useEffect(() => {

    if (chatContainerRef.current) {

      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;

    }

  }, [mensajes]);

const irAlFinalChat = () => {

  if (chatContainerRef.current) {

    chatContainerRef.current.scrollTop =

      chatContainerRef.current.scrollHeight;

  }

};

  const enviarPregunta = async () => {

    if (!pregunta.trim()) return;

    const textoPregunta = pregunta.trim();

    const ultimoCritico = anomalias.find(

      a => a.status === 'Critico'

    ) || { id: 0, ai_recommendation: '' };

    // Preparar los últimos mensajes de la conversación.

    const historialChat = mensajes

      .slice(1)

      .filter(m =>

        (m.role === 'user' || m.role === 'jarvis') &&

        typeof m.text === 'string'

      )

      .slice(-10)

      .map(m => ({

        role: m.role === 'jarvis' ? 'assistant' : 'user',

        content: m.text.slice(0, 1200)

      }));

    // Mostrar la pregunta en el chat.

    setMensajes(prev => [

      ...prev,

      { role: 'user', text: textoPregunta }

    ]);

    setPregunta('');

    try {

      const response = await axios.post(

        'http://127.0.0.1:8000/chat/',

        {

          anomaly_id: ultimoCritico.id,

          pregunta: textoPregunta,

          contexto_anomalia: ultimoCritico.ai_recommendation,

          historial: historialChat

        },

        {

          headers: {

            Authorization: `Bearer ${token}`

          }

        }

      );

      setMensajes(prev => [

        ...prev,

        { role: 'jarvis', text: response.data.respuesta }

      ]);

    } catch (error) {

      setMensajes(prev => [

        ...prev,

        { role: 'jarvis', text: 'Error de red.' }

      ]);

    }

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

    const fechaArchivo = new Date().toLocaleDateString('es-MX').replace(/\//g, '-');

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

      <style>{`

        .plurione-dashboard-grid {

          display: grid;

          grid-template-columns: repeat(6, minmax(0, 1fr));

          align-items: start;

          gap: 20px;

        }

        .plurione-chart-card { grid-column: span 2; }

        .plurione-feed-panel, .plurione-chat-panel { grid-column: span 3; }

        @media (max-width: 1000px) {

          .plurione-chart-card { grid-column: span 3; }

          .plurione-feed-panel, .plurione-chat-panel { grid-column: span 6; }

        }

        @media (max-width: 620px) {

          .plurione-chart-card { grid-column: span 6; }

        }

      `}</style>

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

          <div className="plurione-dashboard-grid" style={{ width: '100%', minWidth: 0 }}>

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

            {/* JARVIS PANEL */}

<div className="plurione-chat-panel" style={{ background: '#111217', padding: '16px', borderRadius: '8px', border: '1px solid #E5B80B', height: '450px', display: 'flex', flexDirection: 'column', minWidth: 0, maxWidth: '100%', boxSizing: 'border-box', overflow: 'hidden' }}>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>

                <strong style={{ color: '#E5B80B', fontSize: '0.9em' }}>J.A.R.V.I.S.</strong>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>

                  <button

                    type="button"

                    onClick={irAlFinalChat}

                    title="Ir al último mensaje"

                    style={{ background: '#22252d', color: '#E5B80B', border: '1px solid #494026', borderRadius: '5px', padding: '4px 8px', cursor: 'pointer', fontSize: '0.75em' }}

                  >

                    ↓ Último

                  </button>

                  <span style={{ color: '#4BB543', fontSize: '0.7em', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '5px' }}>

                    <span style={{ display: 'inline-block', width: '8px', height: '8px', backgroundColor: '#4BB543', borderRadius: '50%' }}></span>

                    ● EN VIVO

                  </span>

                </div>

              </div>

              <div ref={chatContainerRef} style={{ flex: 1, minHeight: 0, minWidth: 0, maxWidth: '100%', overflowY: 'auto', overflowX: 'hidden', overscrollBehaviorY: 'contain', background: '#0b0c10', padding: '12px', borderRadius: '6px', marginBottom: '10px', fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '12px', boxSizing: 'border-box' }}>

{mensajes.map((m, i) => (

                  <div key={i} style={{ alignSelf: m.role === 'jarvis' ? 'stretch' : 'flex-end', flexShrink: 0, maxWidth: '100%', minWidth: 0, overflow: 'hidden' }}>

                    {m.role === 'jarvis' ? (

                      <RespuestaJarvis texto={m.text} />

                    ) : (

                      <div style={{ color: '#f2f3f4', background: '#28323b', border: '1px solid #3d4852', padding: '9px 12px', borderRadius: '10px 10px 3px 10px', overflowWrap: 'break-word', textAlign: 'left' }}>

                        {m.text}

                      </div>

                    )}

                  </div>

                ))}

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
