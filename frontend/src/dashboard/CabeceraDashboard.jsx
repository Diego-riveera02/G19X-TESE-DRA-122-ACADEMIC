import { Link } from 'react-router-dom';

export default function CabeceraDashboard({
  nombreUsuario,
  vista,
  setVista,
  onCerrarSesion
}) {
  return (
    <div className="plurione-header">

      <div className="plurione-header-user">

        <div className="plurione-header-avatar">

          {nombreUsuario.charAt(0).toUpperCase()}

        </div>

        <div className="plurione-header-user-details">

          <span className="plurione-header-username">{nombreUsuario}</span>

          <button onClick={onCerrarSesion} className="plurione-header-logout">Cerrar Sesión</button>

        </div>

      </div>

      <div className="plurione-header-nav">

        <button onClick={() => setVista('dashboard')} className="plurione-header-nav-button" aria-pressed={vista === 'dashboard'}>Datos (Dashboard)</button>

        <Link
          to="/pipelines"
          className="plurione-header-pipelines"
        >
          Pipelines
        </Link>
        <button onClick={() => setVista('historial')} className="plurione-header-nav-button" aria-pressed={vista === 'historial'}>Historial</button>

      </div>

      <h2 className="plurione-header-title">PLURIONE</h2>

    </div>
  );
}
