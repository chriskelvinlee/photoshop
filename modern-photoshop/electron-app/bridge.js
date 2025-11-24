const { spawn } = require('child_process');
const fs = require('fs');

class SwiftBridge {
    constructor(binaryPath) {
        this.binaryPath = binaryPath;
        this.process = null;
        this.callback = null;
    }

    start() {
        if (!fs.existsSync(this.binaryPath)) {
            console.error(`[Bridge] Swift binary not found at ${this.binaryPath}.`);
            console.error(`[Bridge] Please run 'swift build' in the swift-engine directory.`);
            console.log('[Bridge] Running in MOCK mode.');
            return;
        }

        console.log(`[Bridge] Spawning Swift Engine: ${this.binaryPath}`);
        this.process = spawn(this.binaryPath);

        this.process.stdout.on('data', (data) => {
            const lines = data.toString().split('\n');
            lines.forEach(line => {
                if (!line.trim()) return;
                console.log(`[Swift]: ${line}`);
                try {
                    const json = JSON.parse(line);
                    if (this.callback) this.callback(json);
                } catch (e) {
                    // Might be a debug print, ignore JSON parse error
                }
            });
        });

        this.process.stderr.on('data', (data) => {
            console.error(`[Swift Error]: ${data}`);
        });

        this.process.on('close', (code) => {
            console.log(`[Bridge] Swift process exited with code ${code}`);
        });
    }

    send(commandObj) {
        const jsonString = JSON.stringify(commandObj) + '\n';
        if (this.process) {
            this.process.stdin.write(jsonString);
        } else {
            // Mock response for testing without binary
            console.log('[Bridge Mock] Sending:', jsonString.trim());
            if (commandObj.command === 'PING') {
                setTimeout(() => {
                    if (this.callback) this.callback({ status: 'OK', message: 'PONG (Mock from JS)' });
                }, 100);
            }
        }
    }

    onMessage(callback) {
        this.callback = callback;
    }

    stop() {
        if (this.process) this.process.kill();
    }
}

module.exports = SwiftBridge;
