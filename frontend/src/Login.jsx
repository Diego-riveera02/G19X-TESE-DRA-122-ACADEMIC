import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import ParticlesBackground from './ParticlesBackground';

function Login() {
  const [correo, setCorreo] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(false);
  const navigate = useNavigate();

  const manejarLogin = async (e) => {
    e.preventDefault();
    setError('');
    setCargando(true);

    // FastAPI espera los datos en formato x-www-form-urlencoded para el login
    const formData = new URLSearchParams();
    formData.append('username', correo);
    formData.append('password', password);

    try {
      const response = await axios.post('http://127.0.0.1:8000/login/', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      // Guardamos el token en el almacenamiento local del navegador
      localStorage.setItem('token_plurione', response.data.access_token);
      localStorage.setItem('usuario_nombre', response.data.nombre);

      // Redirigimos al Dashboard principal de observabilidad
      navigate('/dashboard');
    } catch (err) {
      setError('Correo o contraseña incorrectos. Verifica tus credenciales.');
    } finally {
      setCargando(false);
    }
  };

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', fontFamily: '"Segoe UI", Roboto, sans-serif', overflow: 'hidden' }}>
      {/* Fondo galáctico animado */}
      <ParticlesBackground />

      {/* Tarjeta de Inicio de Sesión */}
      <div style={{ position: 'relative', zIndex: 10, width: '400px', padding: '40px', backgroundColor: 'rgba(26, 26, 29, 0.9)', border: '1px solid #E5B80B', borderRadius: '10px', boxShadow: '0 0 30px rgba(229,184,11,0.2)', backdropFilter: 'blur(5px)', color: '#c5c6c7', textAlign: 'center' }}>
        
        <h2 style={{ color: '#E5B80B', marginBottom: '5px', letterSpacing: '2px', textTransform: 'uppercase', fontSize: '1.6em' }}>PluriOne</h2>
        <p style={{ color: '#E63946', fontSize: '0.85em', fontWeight: 'bold', textTransform: 'uppercase', marginBottom: '30px', letterSpacing: '1px' }}>Sistema Central de Acceso</p>

        {error && <div style={{ backgroundColor: 'rgba(139,0,0,0.4)', border: '1px solid #ff4444', color: '#ff4444', padding: '10px', borderRadius: '4px', fontSize: '0.85em', marginBottom: '20px' }}>{error}</div>}

        <form onSubmit={manejarLogin} style={{ display: 'flex', flexDirection: 'column', gap: '15px', textAlign: 'left' }}>
          <div>
            <label style={{ fontSize: '0.8em', color: '#a8a8a8', textTransform: 'uppercase', fontWeight: 'bold' }}>Correo Electrónico</label>
            <input 
              type="email" 
              value={correo} 
              onChange={(e) => setCorreo(e.target.value)} 
              required 
              placeholder="ingeniero@plurione.com"
              style={{ width: '100%', padding: '12px', marginTop: '5px', backgroundColor: '#0b0c10', border: '1px solid #444', color: '#fff', borderRadius: '4px', outline: 'none' }} 
            />
          </div>

          <div>
            <label style={{ fontSize: '0.8em', color: '#a8a8a8', textTransform: 'uppercase', fontWeight: 'bold' }}>Contraseña</label>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              required 
              placeholder="••••••••"
              style={{ width: '100%', padding: '12px', marginTop: '5px', backgroundColor: '#0b0c10', border: '1px solid #444', color: '#fff', borderRadius: '4px', outline: 'none' }} 
            />
          </div>

          <button 
            type="submit" 
            disabled={cargando}
            style={{ marginTop: '10px', background: 'linear-gradient(135deg, #E5B80B 0%, #B8860B 100%)', color: '#0b0c10', border: 'none', padding: '12px', fontSize: '0.9em', fontWeight: 'bold', textTransform: 'uppercase', borderRadius: '4px', cursor: 'pointer', transition: 'all 0.3s' }}
          >
            {cargando ? 'Verificando...' : 'Iniciar Sesión'}
          </button>
        </form>

        <div style={{ marginTop: '25px', fontSize: '0.85em' }}>
          <span style={{ color: '#888' }}>¿No tienes una cuenta? </span>
          <Link to="/registro" style={{ color: '#E5B80B', textDecoration: 'none', fontWeight: 'bold' }}>Regístrate aquí</Link>
        </div>

      </div>
    </div>
  );
}

export default Login;