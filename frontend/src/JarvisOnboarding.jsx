import { useState } from 'react';

const JarvisOnboarding = () => {
  const [isVisible, setIsVisible] = useState(() => {
    const token = localStorage.getItem('token_plurione');
    const nombre = localStorage.getItem('usuario_nombre');
    return Boolean(token && nombre);
  });

  const nombreUsuario = localStorage.getItem('usuario_nombre') || 'Ingeniero';

  if (!isVisible) return null;

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <span style={styles.title}>🤖 Ayuda de J.A.R.V.I.S.</span>
        <button onClick={() => setIsVisible(false)} style={styles.closeButton}>✕</button>
      </div>
      <div style={styles.body}>
        <p style={{ margin: '0 0 10px 0' }}><strong>¡Hola, {nombreUsuario}!</strong> Soy tu asistente inteligente.</p>
        <p style={{ margin: '0 0 10px 0' }}>
          Estoy aquí para guiarte en PluriOne. En este panel podrás monitorear en tiempo real 
          la salud de tus pipelines de datos y cuellos de botella.
        </p>
        <p style={{ margin: '0' }}>
          Las gráficas te mostrarán la latencia, calidad y fallos. Si detecto anomalías, te avisaré de inmediato.
        </p>
      </div>
    </div>
  );
};

const styles = {
  container: {
    position: 'fixed',
    bottom: '24px',
    right: '24px',
    backgroundColor: '#ffffff',
    color: '#1a1a1a',
    width: '320px',
    borderRadius: '12px',
    boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
    zIndex: 9999,
    fontFamily: 'system-ui, -apple-system, sans-serif',
    overflow: 'hidden',
    border: '1px solid #e0e0e0'
  },
  header: {
    backgroundColor: '#E5B80B',
    color: '#0b0c10',
    padding: '12px 16px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    fontWeight: '600'
  },
  title: {
    fontSize: '15px'
  },
  closeButton: {
    background: 'transparent',
    border: 'none',
    color: '#0b0c10',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: 'bold'
  },
  body: {
    padding: '16px',
    fontSize: '14px',
    lineHeight: '1.5'
  }
};

export default JarvisOnboarding;