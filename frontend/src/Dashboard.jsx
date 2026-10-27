import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import PanelMetricas from './dashboard/PanelMetricas';
import './dashboard/Dashboard.css';
import { api, WS_URL, limpiarSesion } from './api';
import JarvisOnboarding from './JarvisOnboarding';
import ChatJarvis from './dashboard/ChatJarvis';
import HistorialAnomalias from './dashboard/HistorialAnomalias';
import { generarPDFAnomalias } from './dashboard/generarPDFAnomalias';
import { crearAccionesHistorial } from './dashboard/crearAccionesHistorial';

export default function Dashboard() {

  const [vista, setVista] = useState('dashboard');

  const [anomalias, setAnomalias] = useState([]);

  const [metricasEnVivo, setMetricasEnVivo] = useState({});

  const [procesandoHistorial, setProcesandoHistorial] = useState(false);

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

    api.get('/anomalias/').then(res => {

      setAnomalias(res.data.filter(item => item.id > idOcultosHasta).sort((a, b) => b.id - a.id));

    }).catch(() => {
      // La expiracion del JWT se gestiona en el interceptor de api.js.
      console.error('No se pudo cargar el historial de anomalias.');
    });

    // Conexion WebSocket autenticada mediante JWT

    const ws = new WebSocket(`${WS_URL}/ws/anomalias`);

    // Enviar el token al establecer la conexion

    ws.onopen = () => {

      ws.send(JSON.stringify({

        type: 'auth',

        token: token

      }));

    };

    // Recibir solamente las anomalias del usuario autenticado

    // Mantener lecturas recientes fuera del historial persistente.
    const actualizarMetricaEnVivo = (nueva) => {
      if (
        !nueva ||
        typeof nueva !== 'object' ||
        !['latencia_ms', 'datos_corruptos_%', 'tasa_fallos_%'].includes(nueva.metric_type) ||
        !['Normal', 'Alerta', 'Critico'].includes(nueva.status) ||
        !Number.isFinite(nueva.value) ||
        typeof nueva.timestamp !== 'string'
      ) {
        return;
      }

      const instante = Date.parse(nueva.timestamp);
      if (!Number.isFinite(instante)) return;

      setMetricasEnVivo(prev => {
        const anterior = prev[nueva.metric_type];

        if (
          anterior &&
          Date.parse(anterior.timestamp) > instante
        ) {
          return prev;
        }

        return {
          ...prev,
          [nueva.metric_type]: nueva
        };
      });
    };

    ws.onmessage = (event) => {

      try {

        const nueva = JSON.parse(event.data);

        // Confirmacion de autenticacion del servidor

        if (nueva.type === 'auth_ok') {

          console.log('WebSocket autenticado correctamente');

          return;

        }

        // Lectura temporal: actualiza indicadores sin crear historial.
        if (nueva.type === 'metrica_normal') {
          if (
            nueva.id === null &&
            nueva.registrada === false &&
            nueva.status === 'Normal'
          ) {
            actualizarMetricaEnVivo(nueva);
          }
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

        // Una alerta guardada tambien actualiza el estado actual.
        actualizarMetricaEnVivo(nueva);

        setAnomalias(prev => {

          // Evitar registros duplicados

          if (prev.some(a => a.id === nueva.id)) {

            return prev;

          }

          return [nueva, ...prev].sort((a, b) => b.id - a.id);

        });

      } catch {

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

      const response = await api.post(

        '/chat/',

        {

          anomaly_id: ultimoCritico.id,

          pregunta: textoPregunta,

          contexto_anomalia: ultimoCritico.ai_recommendation,

          historial: historialChat

        }

      );

      setMensajes(prev => [

        ...prev,

        { role: 'jarvis', text: response.data.respuesta }

      ]);

    } catch {

      setMensajes(prev => [

        ...prev,

        { role: 'jarvis', text: 'Error de red.' }

      ]);

    }

  };

  const { limpiarHistorial, restaurarHistorial } = crearAccionesHistorial({
    procesandoHistorial,
    setProcesandoHistorial,
    nombreUsuario,
    setIdOcultosHasta,
    setAnomalias,
    setMetricasEnVivo,
    navigate,
  });

  const cerrarSesion = () => {

    limpiarSesion();

    navigate('/login');

  };

  const exportarPDF = () => generarPDFAnomalias(anomalias);


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

          <Link
            to="/pipelines"
            style={{
              color: '#E5B80B',
              textDecoration: 'none',
              padding: '10px 12px',
              fontWeight: 'bold'
            }}
          >
            Pipelines
          </Link>
          <button onClick={() => setVista('historial')} style={{ background: vista === 'historial' ? 'rgba(229,184,11,0.1)' : 'transparent', color: vista === 'historial' ? '#E5B80B' : '#888', border: 'none', borderBottom: vista === 'historial' ? '2px solid #E5B80B' : '2px solid transparent', padding: '10px 20px', cursor: 'pointer', fontWeight: 'bold', fontSize: '1em' }}>Historial</button>

        </div>

        <h2 style={{ margin: 0, color: '#E5B80B', letterSpacing: '2px', textTransform: 'uppercase' }}>PLURIONE</h2>

      </div>

      {/* 2. ÁREA DE TRABAJO */}

      <div style={{ flex: 1, padding: '20px', overflowY: 'auto' }}>

        {vista === 'dashboard' && (

          <div className="plurione-dashboard-grid" style={{ width: '100%', minWidth: 0 }}>

            <PanelMetricas anomalias={anomalias} metricasEnVivo={metricasEnVivo} />

            {/* JARVIS PANEL */}

            <ChatJarvis
              mensajes={mensajes}
              pregunta={pregunta}
              setPregunta={setPregunta}
              onEnviar={enviarPregunta}
              onIrAlFinal={irAlFinalChat}
              chatContainerRef={chatContainerRef}
            />

          </div>

        )}

        {/* PESTAÑA HISTORIAL */}

        {vista === 'historial' && (
          <HistorialAnomalias
            anomalias={anomalias}
            exportarPDF={exportarPDF}
            limpiarHistorial={limpiarHistorial}
            restaurarHistorial={restaurarHistorial}
            procesandoHistorial={procesandoHistorial}
          />
        )}

        <JarvisOnboarding />

      </div>

    </div>

  );

}
