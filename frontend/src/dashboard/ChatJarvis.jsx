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

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>

                <strong style={{ color: '#E5B80B', fontSize: '0.9em' }}>J.A.R.V.I.S.</strong>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>

                  <button

                    type="button"

                    onClick={onIrAlFinal}

                    title="Ir al último mensaje"

                    className="plurione-chat-last-button"

                  >

                    ↓ Último

                  </button>

                  <span style={{ color: '#4BB543', fontSize: '0.7em', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '5px' }}>

                    <span style={{ display: 'inline-block', width: '8px', height: '8px', backgroundColor: '#4BB543', borderRadius: '50%' }}></span>

                    ● EN VIVO

                  </span>

                </div>

              </div>

              <div ref={chatContainerRef} style={{ flex: 1, minHeight: 0, minWidth: 0, maxWidth: '100%', overflowY: 'auto', overflowX: 'hidden', overscrollBehaviorY: 'contain', background: '#0b0c10', padding: '12px', borderRadius: '6px', marginBottom: '10px', fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '12px', boxSizing: 'border-box' }}>

{mensajes.map((m, i) => (

                  <div key={i} style={{ alignSelf: m.role === 'jarvis' ? 'stretch' : 'flex-end', flexShrink: 0, maxWidth: '100%', minWidth: 0, overflow: 'hidden' }}>

                    {m.role === 'jarvis' ? (

                      <RespuestaJarvis texto={m.text} />

                    ) : (

                      <div style={{ color: '#f2f3f4', background: '#28323b', border: '1px solid #3d4852', padding: '9px 12px', borderRadius: '10px 10px 3px 10px', overflowWrap: 'break-word', textAlign: 'left' }}>

                        {m.text}

                      </div>

                    )}

                  </div>

                ))}

              </div>

              <div style={{ display: 'flex', gap: '5px' }}>

                <input type="text" value={pregunta} onChange={(e) => setPregunta(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && onEnviar()} placeholder="Preguntar..." className="plurione-chat-input" />

                <button onClick={onEnviar} className="plurione-chat-send-button">&gt;</button>

              </div>

            </div>
  );
}
