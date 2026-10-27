import { Link } from 'react-router-dom';

export default function CabeceraDashboard({
  nombreUsuario,
  vista,
  setVista,
  onCerrarSesion
}) {
  return (
    <div style={{ height: '70px', padding: '0 30px', backgroundColor: '#111217', borderBottom: '1px solid #333', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>

      <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>

        <div style={{ width: '35px', height: '35px', borderRadius: '50%', backgroundColor: '#457B9D', display: 'flex', justifyContent: 'center', alignItems: 'center', fontWeight: 'bold', color: '#fff' }}>

          {nombreUsuario.charAt(0).toUpperCase()}

        </div>

        <div style={{ display: 'flex', flexDirection: 'column' }}>

          <span style={{ fontWeight: 'bold', color: '#E5B80B', fontSize: '0.9em' }}>{nombreUsuario}</span>

          <button onClick={onCerrarSesion} style={{ background: 'none', border: 'none', color: '#E63946', cursor: 'pointer', padding: 0, fontSize: '0.75em', textAlign: 'left' }}>Cerrar Sesión</button>

        </div>

      </div>

      <div style={{ display: 'flex', gap: '20px' }}>

        <button onClick={() => setVista('dashboard')} style={{ background: vista === 'dashboard' ? 'rgba(229,184,11,0.1)' : 'transparent', color: vista === 'dashboard' ? '#E5B80B' : '#888', border: 'none', borderBottom: vista === 'dashboard' ? '2px solid #E5B80B' : '2px solid transparent', padding: '10px 20px', cursor: 'pointer', fontWeight: 'bold', fontSize: '1em' }}>Datos (Dashboard)</button>

        <Link
          to="/pipelines"
          style={{
            color: '#E5B80B',
            textDecoration: 'none',
            padding: '10px 12px',
            fontWeight: 'bold'
          }}
        >
          Pipelines
        </Link>
        <button onClick={() => setVista('historial')} style={{ background: vista === 'historial' ? 'rgba(229,184,11,0.1)' : 'transparent', color: vista === 'historial' ? '#E5B80B' : '#888', border: 'none', borderBottom: vista === 'historial' ? '2px solid #E5B80B' : '2px solid transparent', padding: '10px 20px', cursor: 'pointer', fontWeight: 'bold', fontSize: '1em' }}>Historial</button>

      </div>

      <h2 style={{ margin: 0, color: '#E5B80B', letterSpacing: '2px', textTransform: 'uppercase' }}>PLURIONE</h2>

    </div>
  );
}
