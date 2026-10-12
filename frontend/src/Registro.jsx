import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import ParticlesBackground from './ParticlesBackground';

function Registro() {
  const [nombreCompleto, setNombreCompleto] = useState('');
  const [correo, setCorreo] = useState('');
  const [telefono, setTelefono] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [exito, setExito] = useState(false);
  const [cargando, setCargando] = useState(false);
  const navigate = useNavigate();

  const manejarRegistro = async (e) => {
    e.preventDefault();
    setError('');
    setCargando(true);

    try {
      await axios.post('http://127.0.0.1:8000/registro/', {
        nombre_completo: nombreCompleto,
        correo: correo,
        telefono: telefono,
        password: password
      });

      setExito(true);
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ocurrió un error al registrar el usuario.');
    } finally {
      setCargando(false);
    }
  };

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', fontFamily: '"Segoe UI", Roboto, sans-serif', overflow: 'hidden' }}>
      {/* Fondo galáctico animado */}
      <ParticlesBackground />

      {/* Tarjeta de Registro */}
      <div style={{ position: 'relative', zIndex: 10, width: '420px', padding: '35px', backgroundColor: 'rgba(26, 26, 29, 0.9)', border: '1px solid #E5B80B', borderRadius: '10px', boxShadow: '0 0 30px rgba(229,184,11,0.2)', backdropFilter: 'blur(5px)', color: '#c5c6c7', textAlign: 'center' }}>
        
        <h2 style={{ color: '#E5B80B', marginBottom: '5px', letterSpacing: '2px', textTransform: 'uppercase', fontSize: '1.5em' }}>PluriOne</h2>
        <p style={{ color: '#E63946', fontSize: '0.8em', fontWeight: 'bold', textTransform: 'uppercase', marginBottom: '20px', letterSpacing: '1px' }}>Registro de Nuevo Ingeniero</p>

        {error && <div style={{ backgroundColor: 'rgba(139,0,0,0.4)', border: '1px solid #ff4444', color: '#ff4444', padding: '8px', borderRadius: '4px', fontSize: '0.85em', marginBottom: '15px' }}>{error}</div>}
        {exito && <div style={{ backgroundColor: 'rgba(0,128,0,0.4)', border: '1px solid #4BB543', color: '#4BB543', padding: '8px', borderRadius: '4px', fontSize: '0.85em', marginBottom: '15px' }}>¡Registro exitoso! Redirigiendo al login...</div>}

        <form onSubmit={manejarRegistro} style={{ display: 'flex', flexDirection: 'column', gap: '12px', textAlign: 'left' }}>
          <div>
            <label style={{ fontSize: '0.75em', color: '#a8a8a8', textTransform: 'uppercase', fontWeight: 'bold' }}>Nombre Completo</label>
            <input 
              type="text" 
              value={nombreCompleto} 
              onChange={(e) => setNombreCompleto(e.target.value)} 
              required 
              placeholder="Ing. Diego Pérez"
              style={{ width: '100%', padding: '10px', marginTop: '4px', backgroundColor: '#0b0c10', border: '1px solid #444', color: '#fff', borderRadius: '4px', outline: 'none' }} 
            />
          </div>

          <div>
            <label style={{ fontSize: '0.75em', color: '#a8a8a8', textTransform: 'uppercase', fontWeight: 'bold' }}>Correo Electrónico (Para Alertas)</label>
            <input 
              type="email" 
              value={correo} 
              onChange={(e) => setCorreo(e.target.value)} 
              required 
              placeholder="diego@plurione.com"
              style={{ width: '100%', padding: '10px', marginTop: '4px', backgroundColor: '#0b0c10', border: '1px solid #444', color: '#fff', borderRadius: '4px', outline: 'none' }} 
            />
          </div>

          <div>
            <label style={{ fontSize: '0.75em', color: '#a8a8a8', textTransform: 'uppercase', fontWeight: 'bold' }}>Teléfono (Opcional)</label>
            <input 
              type="text" 
              value={telefono} 
              onChange={(e) => setTelefono(e.target.value)} 
              placeholder="5512345678"
              style={{ width: '100%', padding: '10px', marginTop: '4px', backgroundColor: '#0b0c10', border: '1px solid #444', color: '#fff', borderRadius: '4px', outline: 'none' }} 
            />
          </div>

          <div>
            <label style={{ fontSize: '0.75em', color: '#a8a8a8', textTransform: 'uppercase', fontWeight: 'bold' }}>Contraseña</label>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              required 
              placeholder="••••••••"
              style={{ width: '100%', padding: '10px', marginTop: '4px', backgroundColor: '#0b0c10', border: '1px solid #444', color: '#fff', borderRadius: '4px', outline: 'none' }} 
            />
          </div>

          <button 
            type="submit" 
            disabled={cargando || exito}
            style={{ marginTop: '8px', background: 'linear-gradient(135deg, #E5B80B 0%, #B8860B 100%)', color: '#0b0c10', border: 'none', padding: '12px', fontSize: '0.85em', fontWeight: 'bold', textTransform: 'uppercase', borderRadius: '4px', cursor: 'pointer', transition: 'all 0.3s' }}
          >
            {cargando ? 'Registrando...' : 'Crear Cuenta'}
          </button>
        </form>

        <div style={{ marginTop: '20px', fontSize: '0.85em' }}>
          <span style={{ color: '#888' }}>¿Ya tienes una cuenta? </span>
          <Link to="/login" style={{ color: '#E5B80B', textDecoration: 'none', fontWeight: 'bold' }}>Inicia Sesión</Link>
        </div>

      </div>
    </div>
  );
}

export default Registro;