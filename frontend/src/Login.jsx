import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from './api';
import ParticlesBackground from './ParticlesBackground';
import './Auth.css';

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
      sessionStorage.removeItem('plurione_jarvis_mostrada');
      navigate('/app');
    } catch (err) {
      const estado = err.response?.status;

      if (estado === 403) {
        setError(err.response?.data?.detail || 'Debes verificar tu cuenta.');
        setNecesitaVerificacion(true);
      } else if (estado === 429) {
        const detalle = err.response?.data?.detail;
        setError(
          typeof detalle === 'string'
            ? detalle
            : 'Demasiados intentos. Espera unos minutos.'
        );
      } else if (!err.response) {
        setError('No hay conexión con el servidor. Revisa que la API esté disponible.');
      } else if (estado === 401) {
        setError('Correo o contraseña incorrectos.');
      } else {
        setError('No se pudo iniciar sesión. Intenta nuevamente.');
      }
    } finally { setCargando(false); }
  };

  return (
    <div className="auth-page">
      <ParticlesBackground />
      <div className="auth-card">
        <h2 className="auth-title auth-title--brand">PluriOne</h2>
        <p className="auth-subtitle">Sistema Central de Acceso</p>
        
        {error && <div className="auth-error">{error}</div>}
        
        {necesitaVerificacion ? (
           <button onClick={() => navigate('/verificar', { state: { email: correo } })} className="auth-button auth-button--outline auth-button--verify">Ir a Verificar Cuenta</button>
        ) : (
          <form onSubmit={manejarLogin} className="auth-form auth-form--left">
            <input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} required placeholder="Correo" className="auth-input" />
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required placeholder="Contraseña" className="auth-input" />
            <button type="submit" disabled={cargando} className="auth-button auth-button--gradient">{cargando ? 'Verificando...' : 'Iniciar Sesión'}</button>
          </form>
        )}
        
        <div className="auth-links">
          <Link to="/recuperar" className="auth-link auth-link--muted">¿Olvidaste tu contraseña?</Link>
          <Link to="/registro" className="auth-link auth-link--accent">Regístrate aquí</Link>
        </div>
      </div>
    </div>
  );
}