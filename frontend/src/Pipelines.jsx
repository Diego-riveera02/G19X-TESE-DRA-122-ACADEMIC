import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api, limpiarSesion } from './api';

const tarjeta = {
  background: '#111217',
  border: '1px solid #333',
  borderRadius: '10px',
  padding: '22px',
  marginBottom: '20px',
};

const boton = {
  background: '#E5B80B',
  color: '#111',
  border: 'none',
  borderRadius: '6px',
  padding: '11px 16px',
  fontWeight: 'bold',
  cursor: 'pointer',
};

function obtenerMensajeError(error) {
  const detalle = error.response?.data?.detail;

  if (typeof detalle === 'string') {
    return detalle;
  }

  if (Array.isArray(detalle)) {
    return detalle.map((item) => item.msg).filter(Boolean).join('; ');
  }

  return 'No se pudo completar la solicitud. Verifica la conexion con el servidor.';
}

export default function Pipelines() {
  const navigate = useNavigate();
  const claveInputRef = useRef(null);

  const [pipelines, setPipelines] = useState([]);
  const [nombre, setNombre] = useState('');
  const [claveVisible, setClaveVisible] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [procesando, setProcesando] = useState(false);
  const [error, setError] = useState('');
  const [mensaje, setMensaje] = useState('');
  const [estadoCopia, setEstadoCopia] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token_plurione');

    if (!token) {
      navigate('/login', { replace: true });
      return;
    }

    let activo = true;

    api.get('/pipelines/')
      .then(({ data }) => {
        if (!activo) return;

        if (Array.isArray(data)) {
          setPipelines(data);
        } else {
          setError('El servidor devolvio una lista de pipelines inesperada.');
        }
      })
      .catch((fallo) => {
        if (!activo) return;

        setError(obtenerMensajeError(fallo));
      })
      .finally(() => {
        if (activo) setCargando(false);
      });

    return () => {
      activo = false;
    };
  }, [navigate]);

  function manejarError(fallo) {
    setError(obtenerMensajeError(fallo));
  }

  async function crearPipeline(evento) {
    evento.preventDefault();

    const nombreLimpio = nombre.trim();

    if (nombreLimpio.length < 2 || nombreLimpio.length > 100) {
      setError('El nombre debe tener entre 2 y 100 caracteres.');
      return;
    }

    if (
      claveVisible &&
      !window.confirm('Tienes una clave visible. Si continuas, dejaras de verla. ¿Ya la guardaste?')
    ) {
      return;
    }

    setProcesando(true);
    setError('');
    setMensaje('');

    try {
      const { data } = await api.post(
        '/pipelines/',
        { nombre: nombreLimpio }
      );

      setPipelines((anteriores) => [
        {
          id: data.id,
          nombre: data.nombre,
          revocado: false,
        },
        ...anteriores,
      ]);

      setEstadoCopia('');
      setClaveVisible({
        id: data.id,
        valor: data.clave_api,
      });

      setNombre('');
      setMensaje('Pipeline creado correctamente.');
    } catch (fallo) {
      manejarError(fallo);
    } finally {
      setProcesando(false);
    }
  }

  async function rotarClave(pipeline) {
    if (
      !window.confirm(
        `¿Rotar la clave de "${pipeline.nombre}"? La clave anterior dejara de funcionar inmediatamente.`
      )
    ) {
      return;
    }

    if (
      claveVisible &&
      !window.confirm('Tienes una clave visible. ¿Ya la guardaste antes de reemplazarla?')
    ) {
      return;
    }

    setProcesando(true);
    setError('');
    setMensaje('');

    try {
      const { data } = await api.post(
        `/pipelines/${pipeline.id}/rotar/`,
        {}
      );

      setEstadoCopia('');
      setClaveVisible({
        id: pipeline.id,
        valor: data.clave_api,
      });

      setMensaje(`Clave del pipeline "${pipeline.nombre}" rotada correctamente.`);
    } catch (fallo) {
      manejarError(fallo);
    } finally {
      setProcesando(false);
    }
  }

  async function revocarPipeline(pipeline) {
    if (
      !window.confirm(
        `¿Revocar definitivamente "${pipeline.nombre}"? Su clave ya no permitira enviar metricas.`
      )
    ) {
      return;
    }

    setProcesando(true);
    setError('');
    setMensaje('');

    try {
      await api.post(
        `/pipelines/${pipeline.id}/revocar/`,
        {}
      );

      setPipelines((anteriores) =>
        anteriores.map((item) =>
          item.id === pipeline.id
            ? { ...item, revocado: true }
            : item
        )
      );

      setClaveVisible((actual) =>
        actual?.id === pipeline.id ? null : actual
      );

      setMensaje(`Pipeline "${pipeline.nombre}" revocado correctamente.`);
    } catch (fallo) {
      manejarError(fallo);
    } finally {
      setProcesando(false);
    }
  }

  async function copiarClave() {
    if (!claveVisible) return;

    const campo = claveInputRef.current;
    let copiada = false;

    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(claveVisible.valor);
        copiada = true;
      }
    } catch {
      copiada = false;
    }

    if (!copiada && campo) {
      campo.focus();
      campo.select();

      try {
        copiada = document.execCommand('copy');
      } catch {
        copiada = false;
      }
    }

    if (copiada) {
      setEstadoCopia('copiada');
      setError('');
    } else {
      if (campo) {
        campo.focus();
        campo.select();
      }
      setEstadoCopia('manual');
    }
  }

  function cerrarSesion() {
    limpiarSesion();
    navigate('/login', { replace: true });
  }

  return (
    <main
      style={{
        minHeight: '100vh',
        background: '#0b0c10',
        color: '#d5d5d5',
        fontFamily: '"Segoe UI", Arial, sans-serif',
        padding: '24px',
        boxSizing: 'border-box',
      }}
    >
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        <header
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '18px',
            marginBottom: '28px',
          }}
        >
          <div>
            <h1 style={{ color: '#E5B80B', marginBottom: '6px' }}>
              Administracion de pipelines
            </h1>
            <p style={{ color: '#aaa', margin: 0 }}>
              Configura fuentes externas de metricas para PluriOne.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '18px', alignItems: 'center' }}>
            <Link
              to="/app"
              style={{ color: '#E5B80B', textDecoration: 'none' }}
            >
              Volver al Dashboard
            </Link>

            <button
              type="button"
              onClick={cerrarSesion}
              style={{
                background: 'transparent',
                color: '#E63946',
                border: '1px solid #E63946',
                borderRadius: '6px',
                padding: '9px',
                cursor: 'pointer',
              }}
            >
              Cerrar sesion
            </button>
          </div>
        </header>

        {error && (
          <div
            role="alert"
            style={{
              ...tarjeta,
              borderColor: '#E63946',
              color: '#ff929b',
            }}
          >
            {error}
          </div>
        )}

        {mensaje && (
          <div
            role="status"
            style={{
              ...tarjeta,
              borderColor: '#4caf50',
              color: '#a8e6ad',
            }}
          >
            {mensaje}
          </div>
        )}

        <section style={tarjeta}>
          <h2 style={{ color: '#E5B80B', marginTop: 0 }}>
            Crear nuevo pipeline
          </h2>

          <form
            onSubmit={crearPipeline}
            style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}
          >
            <input
              type="text"
              aria-label="Nombre del pipeline"
              placeholder="Ejemplo: servidor-produccion"
              value={nombre}
              onChange={(evento) => setNombre(evento.target.value)}
              minLength={2}
              maxLength={100}
              required
              style={{
                flex: '1 1 250px',
                padding: '12px',
                color: '#fff',
                background: '#1a1b20',
                border: '1px solid #555',
                borderRadius: '6px',
              }}
            />

            <button
              type="submit"
              disabled={procesando || cargando}
              style={{
                ...boton,
                opacity: procesando || cargando ? 0.5 : 1,
              }}
            >
              {procesando ? 'Procesando...' : 'Crear pipeline'}
            </button>
          </form>
        </section>

        {claveVisible && (
          <section
            style={{
              ...tarjeta,
              borderColor: '#E5B80B',
            }}
          >
            <h2 style={{ color: '#E5B80B', marginTop: 0 }}>
              Clave de ingesta — Pipeline #{claveVisible.id}
            </h2>

            <p>
              Guarda esta clave ahora. Por seguridad, no podras volver a
              consultarla despues de ocultarla o salir de esta pantalla.
            </p>

            <input
              type="text"
              ref={claveInputRef}
              aria-label="Clave de ingesta generada"
              readOnly
              value={claveVisible.valor}
              onFocus={(evento) => evento.target.select()}
              style={{
                width: '100%',
                boxSizing: 'border-box',
                background: '#1a1b20',
                color: '#fff',
                padding: '12px',
                border: '1px solid #777',
                borderRadius: '6px',
                marginBottom: '12px',
              }}
            />

            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              <button
                type="button"
                onClick={copiarClave}
                style={boton}
              >
                {estadoCopia === 'copiada' ? '¡Copiada!' : 'Copiar clave'}
              </button>

              <button
                type="button"
                onClick={() => setClaveVisible(null)}
                style={{
                  ...boton,
                  background: '#333',
                  color: '#fff',
                }}
              >
                Ya la guarde — Ocultar
              </button>
            </div>

            {estadoCopia === 'copiada' && (
              <p role="status" style={{ color: '#8de098' }}>
                Clave copiada correctamente al portapapeles.
              </p>
            )}

            {estadoCopia === 'manual' && (
              <p role="alert" style={{ color: '#ffb3b3' }}>
                El navegador bloqueo la copia automatica.
                La clave esta seleccionada: presiona Ctrl+C.
              </p>
            )}

            <p style={{ fontSize: '0.85rem', color: '#aaa' }}>
              No compartas esta clave ni la publiques en GitHub.
              Se utiliza en la cabecera X-Pipeline-Key para enviar metricas.
            </p>
          </section>
        )}

        <section style={tarjeta}>
          <h2 style={{ color: '#E5B80B', marginTop: 0 }}>
            Pipelines registrados
          </h2>

          {cargando ? (
            <p role="status">Cargando pipelines...</p>
          ) : pipelines.length === 0 ? (
            <p>
              Todavia no hay pipelines registrados para tu cuenta.
            </p>
          ) : (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {pipelines.map((pipeline) => (
                <li
                  key={pipeline.id}
                  style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '16px',
                    padding: '16px 0',
                    borderBottom: '1px solid #333',
                  }}
                >
                  <div>
                    <strong style={{ color: '#fff' }}>
                      {pipeline.nombre}
                    </strong>

                    <div style={{ fontSize: '0.85rem', marginTop: '5px' }}>
                      ID: {pipeline.id} ·{' '}
                      <span
                        style={{
                          color: pipeline.revocado ? '#ff929b' : '#8de098',
                        }}
                      >
                        {pipeline.revocado ? 'Revocado' : 'Activo'}
                      </span>
                    </div>
                  </div>

                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
                    <button
                      type="button"
                      disabled={pipeline.revocado || procesando}
                      onClick={() => rotarClave(pipeline)}
                      style={{
                        ...boton,
                        background: '#393011',
                        color: '#E5B80B',
                        opacity: pipeline.revocado || procesando ? 0.45 : 1,
                      }}
                    >
                      Rotar clave
                    </button>

                    <button
                      type="button"
                      disabled={pipeline.revocado || procesando}
                      onClick={() => revocarPipeline(pipeline)}
                      style={{
                        ...boton,
                        background: '#441b21',
                        color: '#ff9aa3',
                        opacity: pipeline.revocado || procesando ? 0.45 : 1,
                      }}
                    >
                      Revocar
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </main>
  );
}
