const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const SwiftBridge = require('./bridge');

let mainWindow;
let swiftEngine;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    title: "Modern Photoshop (Apple Silicon Edition)",
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false // For prototype simplicity
    }
  });

  mainWindow.loadFile('index.html');

  // Initialize Swift Bridge
  // Note: User must run 'swift build' in swift-engine first
  const swiftPath = path.resolve(__dirname, '../swift-engine/.build/debug/SwiftEngine'); 
  swiftEngine = new SwiftBridge(swiftPath);
  swiftEngine.start();

  // Forward messages from UI to Swift
  ipcMain.on('to-swift', (event, command) => {
    swiftEngine.send(command);
  });

  // Forward messages from Swift to UI
  swiftEngine.onMessage((response) => {
    if (mainWindow && !mainWindow.webContents.isDestroyed()) {
        mainWindow.webContents.send('from-swift', response);
    }
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (swiftEngine) swiftEngine.stop();
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
