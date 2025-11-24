const { ipcRenderer } = window.require('electron');

function App() {
    const [status, setStatus] = React.useState('Waiting...');
    const [logs, setLogs] = React.useState([]);

    React.useEffect(() => {
        // Listen for messages from Swift
        ipcRenderer.on('from-swift', (event, response) => {
            const log = `[Swift]: ${response.status} - ${response.message}`;
            setLogs(prev => [...prev, log]);
            setStatus('Connected');
        });
    }, []);

    const sendPing = () => {
        ipcRenderer.send('to-swift', { command: 'PING', payload: {} });
    };

    const openFile = () => {
        // In a real app, we'd use dialog.showOpenDialog
        ipcRenderer.send('to-swift', { command: 'OPEN', payload: '/path/to/test.psd' });
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            {/* Toolbar / Menu */}
            <div style={{ padding: '10px', background: '#3c3c3c', borderBottom: '1px solid #111', display: 'flex', alignItems: 'center' }}>
                <strong>Ps</strong>
                <div style={{ width: '20px' }}></div>
                <button onClick={sendPing}>Ping Engine</button>
                <button onClick={openFile}>Open File</button>
                <span style={{ marginLeft: 'auto', fontSize: '12px', color: status.includes('Connected') ? '#4caf50' : '#f44336' }}>
                    {status}
                </span>
            </div>
            
            <div style={{ flex: 1, display: 'flex' }}>
                {/* Tools Panel */}
                <div style={{ width: '60px', background: '#333', borderRight: '1px solid #111', padding: '10px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <div title="Marquee" style={{ width: '40px', height: '40px', background: '#444', borderRadius: '4px' }}></div>
                    <div title="Lasso" style={{ width: '40px', height: '40px', background: '#444', borderRadius: '4px' }}></div>
                    <div title="Magic Wand" style={{ width: '40px', height: '40px', background: '#444', borderRadius: '4px' }}></div>
                    <div title="Brush" style={{ width: '40px', height: '40px', background: '#444', borderRadius: '4px' }}></div>
                </div>

                {/* Main Canvas Area */}
                <div style={{ flex: 1, background: '#1e1e1e', position: 'relative', overflow: 'hidden' }}>
                     <div style={{ 
                         width: '400px', height: '300px', background: 'white', 
                         position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
                         boxShadow: '0 0 20px rgba(0,0,0,0.5)'
                     }}>
                         {/* This would be the <canvas> later */}
                     </div>
                </div>

                {/* Sidebar / Layers */}
                <div style={{ width: '250px', background: '#333', borderLeft: '1px solid #111', display: 'flex', flexDirection: 'column' }}>
                    <div style={{ padding: '10px', background: '#444', color: '#ccc', fontSize: '12px' }}>Layers</div>
                    <div style={{ flex: 1 }}></div>
                    
                    <div style={{ height: '200px', borderTop: '1px solid #222', background: '#222', padding: '10px', overflowY: 'auto' }}>
                        <div style={{ color: '#888', fontSize: '11px', marginBottom: '5px' }}>DEBUG CONSOLE</div>
                        <div style={{ fontFamily: 'monospace', fontSize: '11px', color: '#0f0' }}>
                            {logs.map((l, i) => <div key={i}>{l}</div>)}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
