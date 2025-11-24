import Foundation

// A simple standard input/output handler for IPC
class IPCHandler {
    func start() {
        print("Swift Engine Started. Waiting for JSON commands...")
        fflush(stdout) // Ensure output is flushed immediately
        
        while let line = readLine() {
            handleCommand(line)
        }
    }
    
    func handleCommand(_ jsonString: String) {
        guard let data = jsonString.data(using: .utf8) else { return }
        
        do {
            // Basic command parsing
            // expected format: {"command": "OPEN", "payload": "path/to/file"}
            if let json = try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any],
               let command = json["command"] as? String {
                
                switch command {
                case "PING":
                    respond(status: "OK", message: "PONG")
                case "OPEN":
                    if let path = json["payload"] as? String {
                        // TODO: Open the document
                        respond(status: "OK", message: "Opening file at \(path)")
                    }
                case "EXIT":
                    exit(0)
                default:
                    respond(status: "ERROR", message: "Unknown command: \(command)")
                }
            }
        } catch {
            respond(status: "ERROR", message: "Invalid JSON")
        }
    }
    
    func respond(status: String, message: String) {
        let response: [String: Any] = ["status": status, "message": message]
        if let data = try? JSONSerialization.data(withJSONObject: response, options: []),
           let string = String(data: data, encoding: .utf8) {
            print(string)
            fflush(stdout)
        }
    }
}

// Start the loop
let ipc = IPCHandler()
ipc.start()
