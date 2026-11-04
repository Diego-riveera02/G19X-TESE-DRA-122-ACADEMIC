import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from './api';
import ParticlesBackground from './ParticlesBackground';
import './Auth.css';

export default function Registro() {
  const [nombreCompleto, setNombreCompleto] = useState(''); 
  const [correo, setCorreo] = useState(''); 
  const [telefono, setTelefono] = useState(''); 
  const [password, setPassword] = useState(''); 
  const [error, setError] = useState(''); 
  const [exito, setExito] = useState(false); 
  const navigate = useNavigate();
  
  const manejarRegistro = async (e) => {
    e.preventDefault();
    try { 
      await api.post('/registro/', { nombre_completo: nombreCompleto, correo, telefono, password });
      setExito(true); 
      setTimeout(() => navigate('/verificar', { state: { email: correo } }), 2000); 
    } catch (err) { setError(err.response?.data?.detail || 'Error al registrar.'); }
  };
  
  return (
    <div className="auth-page">
      <ParticlesBackground />
      <div className="auth-card auth-card--wide">
        <h2 className="auth-title">PluriOne</h2>
        <p className="auth-subtitle auth-subtitle--registration">Registro de Nuevo Ingeniero</p>
        {error && <div className="auth-message auth-message--error">{error}</div>}
        {exito && <div className="auth-message auth-message--success">Si el correo puede registrarse, recibiras un codigo. Si ya tienes cuenta, inicia sesion.</div>}
        <form onSubmit={manejarRegistro} className="auth-form auth-form--compact">
          <input type="text" value={nombreCompleto} onChange={(e) => setNombreCompleto(e.target.value)} required placeholder="Nombre Completo" className="auth-input auth-input--compact" />
          <input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} required placeholder="Correo" className="auth-input auth-input--compact" />
          <input type="tel" value={telefono} onChange={(e) => setTelefono(e.target.value.replace(/[^0-9]/g, ''))} placeholder="Teléfono" className="auth-input auth-input--compact" />
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} autoComplete="new-password" placeholder="Contraseña" className="auth-input auth-input--compact" />
          <button type="submit" disabled={exito} className="auth-button">Crear Cuenta</button>
        </form>
        <div className="auth-footer"><Link to="/login" className="auth-link">Inicia Sesión</Link></div>
      </div>
    </div>
  );
}