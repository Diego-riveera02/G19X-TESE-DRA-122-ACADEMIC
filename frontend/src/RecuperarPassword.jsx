import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from './api';
import ParticlesBackground from './ParticlesBackground';
import './Auth.css';

export default function RecuperarPassword() {

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

      await api.post(

        '/solicitar-recuperacion/',

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

      await api.post('/recuperar-password/', { correo, codigo, nueva_password: nuevaPassword });

      setMensaje('Contraseña actualizada correctamente.');

      setTimeout(() => navigate('/login'), 2000);

    } catch (err) { setError(err.response?.data?.detail || 'Error al actualizar contraseña.'); }

  };

  return (

    <div className="auth-page">

      <ParticlesBackground />

      <div className="auth-card">

        <h2 className="auth-title">Recuperar Acceso</h2>

        <p className="auth-description auth-description--muted">Ingresa tu correo, el código de verificación y tu nueva contraseña.</p>

        {error && <div className="auth-message auth-message--error">{error}</div>}

        {mensaje && <div className="auth-message auth-message--success">{mensaje}</div>}

        <form onSubmit={manejarRecuperacion} className="auth-form">

          <input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} required placeholder="Correo registrado" className="auth-input" />

          <button

            type="button"

            onClick={solicitarCodigoRecuperacion}

            disabled={!correo.trim() || enviandoCodigo}

            className="auth-button auth-button--send"

          >

            {enviandoCodigo ? 'Solicitando código...' : 'Enviar código de recuperación'}

          </button>

          <input type="text" value={codigo} onChange={(e) => setCodigo(e.target.value)} required placeholder="Código de 6 dígitos" maxLength="6" className="auth-input auth-input--code-recovery" />

          <input type="password" value={nuevaPassword} onChange={(e) => setNuevaPassword(e.target.value)} required placeholder="Nueva Contraseña" className="auth-input" />

          <button type="submit" className="auth-button auth-button--blue">Actualizar Contraseña</button>

        </form>

        <div className="auth-footer"><Link to="/login" className="auth-link auth-link--muted auth-link--back">Volver al Login</Link></div>

      </div>

    </div>

  );

}
