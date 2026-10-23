import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from './api';
import ParticlesBackground from './ParticlesBackground';

export default function Login() {
  const [correo, setCorreo] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [necesitaVerificacion, setNecesitaVerificacion] = useState(false);
  const [cargando, setCargando] = useState(false);
  const navigate = useNavigate();

  const manejarLogin = async (e) => {
    e.preventDefault();
    setError(''); setNecesitaVerificacion(false); setCargando(true);
    const formData = new URLSearchParams(); 
    formData.append('username', correo); 
    formData.append('password', password);
    try {
      const response = await api.post('/login/', formData, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
      localStorage.setItem('token_plurione', response.data.access_token);
      localStorage.setItem('usuario_nombre', response.data.nombre);
      navigate('/app');
    } catch (err) { 
      if (err.response?.status === 403) {
        setError(err.response.data.detail);
        setNecesitaVerificacion(true);
      } else {
        setError('Correo o contraseña incorrectos.'); 
      }
    } finally { setCargando(false); }
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: '#0b0c10', overflow: 'hidden' }}>
      <ParticlesBackground />
      <div style={{ position: 'relative', zIndex: 10, width: '400px', padding: '40px', backgroundColor: 'rgba(26, 26, 29, 0.9)', border: '1px solid #E5B80B', borderRadius: '10px', boxShadow: '0 0 30px rgba(229,184,11,0.2)', color: '#c5c6c7', textAlign: 'center' }}>
        <h2 style={{ color: '#E5B80B', marginBottom: '5px', letterSpacing: '2px', textTransform: 'uppercase' }}>PluriOne</h2>
        <p style={{ color: '#E63946', fontWeight: 'bold', textTransform: 'uppercase', marginBottom: '30px' }}>Sistema Central de Acceso</p>
        
        {error && <div style={{ backgroundColor: 'rgba(139,0,0,0.4)', border: '1px solid #ff4444', color: '#ff4444', padding: '10px', borderRadius: '4px', marginBottom: '20px' }}>{error}</div>}
        
        {necesitaVerificacion ? (
           <button onClick={() => navigate('/verificar', { state: { email: correo } })} style={{ width: '100%', background: 'transparent', color: '#E5B80B', border: '1px solid #E5B80B', padding: '10px', marginBottom: '20px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Ir a Verificar Cuenta</button>
        ) : (
          <form onSubmit={manejarLogin} style={{ display: 'flex', flexDirection: 'column', gap: '15px', textAlign: 'left' }}>
            <input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} required placeholder="Correo" style={{ width: '100%', padding: '12px', backgroundColor: '#111217', border: '1px solid #444', color: '#fff', borderRadius: '4px' }} />
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required placeholder="Contraseña" style={{ width: '100%', padding: '12px', backgroundColor: '#111217', border: '1px solid #444', color: '#fff', borderRadius: '4px' }} />
            <button type="submit" disabled={cargando} style={{ background: 'linear-gradient(135deg, #E5B80B 0%, #B8860B 100%)', color: '#0b0c10', border: 'none', padding: '12px', fontWeight: 'bold', borderRadius: '4px', cursor: 'pointer' }}>{cargando ? 'Verificando...' : 'Iniciar Sesión'}</button>
          </form>
        )}
        
        <div style={{ marginTop: '25px', fontSize: '0.85em', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <Link to="/recuperar" style={{ color: '#888', textDecoration: 'none' }}>¿Olvidaste tu contraseña?</Link>
          <Link to="/registro" style={{ color: '#E5B80B', fontWeight: 'bold', textDecoration: 'none' }}>Regístrate aquí</Link>
        </div>
      </div>
    </div>
  );
}