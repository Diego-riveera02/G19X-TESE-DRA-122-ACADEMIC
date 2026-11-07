import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { api } from './api';
import ParticlesBackground from './ParticlesBackground';
import './Auth.css';

export default function Verificar() {
  const location = useLocation();
  const navigate = useNavigate();
  const [correo, setCorreo] = useState(location.state?.email || '');
  const [codigo, setCodigo] = useState('');
  const [password, setPassword] = useState('');
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
        codigo,
        password
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
    <div className="auth-page">
      <ParticlesBackground />
      <div className="auth-card auth-card--compact">
        <h2 className="auth-title">Verificación</h2>
        <p className="auth-description">Ingresa el código de 6 dígitos enviado a tu correo y la contraseña utilizada durante el registro.</p>

        {error && <div role="alert" className="auth-message auth-message--error">{error}</div>}
        {mensaje && <div role="status" className="auth-message auth-message--success">{mensaje}</div>}

        <form onSubmit={manejarVerificacion} className="auth-form">
          <input
            type="email"
            aria-label="Correo electrónico"
            value={correo}
            onChange={(e) => setCorreo(e.target.value)}
            required
            disabled={verificado}
            placeholder="Confirma tu correo"
            className="auth-input"
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
            className="auth-input auth-input--code"
          />
          <input
            type="password"
            aria-label="Contraseña utilizada durante el registro"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            disabled={verificado}
            placeholder="Contraseña del registro"
            className="auth-input"
          />
          <button
            type="submit"
            disabled={verificando || reenviando || verificado || codigo.length !== 6 || password.length < 8}
            className="auth-button"
          >
            {verificando ? 'Verificando...' : verificado ? 'Cuenta activada' : 'Activar cuenta'}
          </button>

          <button
            type="button"
            onClick={manejarReenvio}
            disabled={!correo.trim() || reenviando || verificando || verificado}
            className="auth-button auth-button--outline auth-button--resend"
          >
            {reenviando ? 'Solicitando código...' : 'Reenviar código'}
          </button>
        </form>

        <p className="auth-helper">
          El código dura 10 minutos. Si todavía está vigente, usa el que ya recibiste.
          Si venció, solicita uno nuevo y revisa también tu carpeta de spam.
        </p>
        <div className="auth-footer">
          <Link to="/login" className="auth-link auth-link--muted auth-link--back auth-link--soft">Volver al Login</Link>
        </div>
      </div>
    </div>
  );
}
