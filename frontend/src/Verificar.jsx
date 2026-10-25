import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { api } from './api';
import ParticlesBackground from './ParticlesBackground';

export default function Verificar() {
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
      await api.post('/verificar/', {
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
      const respuesta = await api.post('/reenviar-verificacion/', {
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
