import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import ParticlesBackground from './ParticlesBackground';

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
      await axios.post('http://127.0.0.1:8000/registro/', { nombre_completo: nombreCompleto, correo, telefono, password }); 
      setExito(true); 
      setTimeout(() => navigate('/verificar', { state: { email: correo } }), 2000); 
    } catch (err) { setError(err.response?.data?.detail || 'Error al registrar.'); }
  };
  
  return (
    <div style={{ position: 'relative', width: '100%', height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: '#0b0c10', overflow: 'hidden' }}>
      <ParticlesBackground />
      <div style={{ position: 'relative', zIndex: 10, width: '420px', padding: '35px', backgroundColor: 'rgba(26, 26, 29, 0.9)', border: '1px solid #E5B80B', borderRadius: '10px', boxShadow: '0 0 30px rgba(229,184,11,0.2)', color: '#c5c6c7', textAlign: 'center' }}>
        <h2 style={{ color: '#E5B80B', marginBottom: '5px' }}>PluriOne</h2>
        <p style={{ color: '#E63946', fontWeight: 'bold', marginBottom: '20px' }}>Registro de Nuevo Ingeniero</p>
        {error && <div style={{ color: '#ff4444', marginBottom: '15px' }}>{error}</div>}
        {exito && <div style={{ color: '#4BB543', marginBottom: '15px' }}>¡Registro exitoso! Revisa tu correo.</div>}
        <form onSubmit={manejarRegistro} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <input type="text" value={nombreCompleto} onChange={(e) => setNombreCompleto(e.target.value)} required placeholder="Nombre Completo" style={{ padding: '10px', backgroundColor: '#111217', border: '1px solid #444', color: '#fff' }} />
          <input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} required placeholder="Correo" style={{ padding: '10px', backgroundColor: '#111217', border: '1px solid #444', color: '#fff' }} />
          <input type="tel" value={telefono} onChange={(e) => setTelefono(e.target.value.replace(/[^0-9]/g, ''))} placeholder="Teléfono" style={{ padding: '10px', backgroundColor: '#111217', border: '1px solid #444', color: '#fff' }} />
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required placeholder="Contraseña" style={{ padding: '10px', backgroundColor: '#111217', border: '1px solid #444', color: '#fff' }} />
          <button type="submit" disabled={exito} style={{ background: '#E5B80B', color: '#0b0c10', padding: '12px', fontWeight: 'bold', cursor: 'pointer' }}>Crear Cuenta</button>
        </form>
        <div style={{ marginTop: '20px' }}><Link to="/login" style={{ color: '#E5B80B', fontWeight: 'bold' }}>Inicia Sesión</Link></div>
      </div>
    </div>
  );
}