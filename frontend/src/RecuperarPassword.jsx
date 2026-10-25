import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from './api';
import ParticlesBackground from './ParticlesBackground';

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
