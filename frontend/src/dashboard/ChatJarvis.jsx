import RespuestaJarvis from '../RespuestaJarvis';

export default function ChatJarvis({
  mensajes,
  pregunta,
  setPregunta,
  onEnviar,
  onIrAlFinal,
  chatContainerRef
}) {
  return (
<div className="plurione-chat-panel plurione-surface-card">

              <div className="plurione-chat-toolbar">

                <strong className="plurione-chat-title">J.A.R.V.I.S.</strong>

                <div className="plurione-chat-toolbar-actions">

                  <button

                    type="button"

                    onClick={onIrAlFinal}

                    title="Ir al último mensaje"

                    className="plurione-chat-last-button"

                  >

                    ↓ Último

                  </button>

                  <span className="plurione-chat-live">

                    <span className="plurione-chat-live-dot"></span>

                    ● EN VIVO

                  </span>

                </div>

              </div>

              <div ref={chatContainerRef} className="plurione-chat-messages">

{mensajes.map((m, i) => (

                  <div key={i} className={m.role === 'jarvis' ? 'plurione-chat-message plurione-chat-message--jarvis' : 'plurione-chat-message plurione-chat-message--user'}>

                    {m.role === 'jarvis' ? (

                      <RespuestaJarvis texto={m.text} />

                    ) : (

                      <div className="plurione-chat-user-bubble">

                        {m.text}

                      </div>

                    )}

                  </div>

                ))}

              </div>

              <div className="plurione-chat-composer">

                <input type="text" value={pregunta} onChange={(e) => setPregunta(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && onEnviar()} placeholder="Preguntar..." className="plurione-chat-input" />

                <button onClick={onEnviar} className="plurione-chat-send-button">&gt;</button>

              </div>

            </div>
  );
}
