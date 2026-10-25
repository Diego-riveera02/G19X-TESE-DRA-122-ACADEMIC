import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// Las tablas de Markdown no pueden agrandar la cuadrícula ni la página.
export default function RespuestaJarvis({ texto }) {

  return (

    <div style={{ width: '100%', minWidth: 0, maxWidth: '100%', color: '#d7d9dd', lineHeight: 1.6, overflowWrap: 'break-word' }}>

      <ReactMarkdown

        remarkPlugins={[remarkGfm]}

        components={{

          h1: ({ node, ...props }) => <h2 {...props} style={{ color: '#f2c94c', fontSize: '1.05rem', margin: '12px 0 8px', lineHeight: 1.35 }} />,

          h2: ({ node, ...props }) => <h2 {...props} style={{ color: '#f2c94c', fontSize: '1.02rem', margin: '14px 0 8px', lineHeight: 1.4 }} />,

          h3: ({ node, ...props }) => <h3 {...props} style={{ color: '#f2c94c', fontSize: '0.95rem', margin: '12px 0 6px' }} />,

          p: ({ node, ...props }) => <p {...props} style={{ margin: '6px 0 10px', lineHeight: 1.65 }} />,

          strong: ({ node, ...props }) => <strong {...props} style={{ color: '#f2c94c', fontWeight: 700 }} />,

          ul: ({ node, ...props }) => <ul {...props} style={{ paddingLeft: '20px', margin: '8px 0' }} />,

          ol: ({ node, ...props }) => <ol {...props} style={{ paddingLeft: '20px', margin: '8px 0' }} />,

          li: ({ node, ...props }) => <li {...props} style={{ marginBottom: '5px' }} />,

          blockquote: ({ node, ...props }) => <blockquote {...props} style={{ margin: '10px 0', padding: '8px 12px', borderLeft: '3px solid #E5B80B', background: '#16191f' }} />,

          hr: () => <hr style={{ border: 0, borderTop: '1px solid #333944', margin: '14px 0' }} />,

          pre: ({ node, ...props }) => <pre {...props} style={{ maxWidth: '100%', overflowX: 'auto', padding: '10px', borderRadius: '6px', background: '#171a20', fontSize: '0.78rem' }} />,

          code: ({ node, ...props }) => <code {...props} style={{ overflowWrap: 'anywhere', background: '#20232b', borderRadius: '3px', padding: '1px 3px', fontSize: '0.83em' }} />,

          table: ({ node, ...props }) => (

            <div role="region" aria-label="Tabla del diagnóstico, desplazable horizontalmente" tabIndex={0}

              style={{ width: '100%', maxWidth: '100%', minWidth: 0, overflowX: 'auto', margin: '10px 0 14px', border: '1px solid #30333a', borderRadius: '6px' }}>

              <table {...props} style={{ width: '100%', minWidth: '540px', tableLayout: 'fixed', borderCollapse: 'collapse', fontSize: '0.8rem', textAlign: 'left' }} />

            </div>

          ),

          th: ({ node, ...props }) => <th {...props} style={{ background: '#20232b', color: '#f2c94c', borderBottom: '1px solid #66581f', padding: '8px 10px', textAlign: 'left', whiteSpace: 'normal', overflowWrap: 'anywhere' }} />,

          td: ({ node, ...props }) => <td {...props} style={{ borderTop: '1px solid #30333a', padding: '8px 10px', verticalAlign: 'top', overflowWrap: 'anywhere', wordBreak: 'normal' }} />

        }}

      >

        {texto}

      </ReactMarkdown>

    </div>

  );

}
