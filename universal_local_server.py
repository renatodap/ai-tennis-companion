#!/usr/bin/env python3
"""
🎾 TennisViz Universal Local Development Server
Works with ALL Python versions - no deprecated modules!
Serves frontend files + handles basic backend API for video uploads
"""

import os
import sys
import json
import threading
import webbrowser
import time
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

# Get project paths
PROJECT_ROOT = Path(__file__).parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
BACKEND_DIR = PROJECT_ROOT / "backend"

# Ensure directories exist
FRONTEND_DIR.mkdir(exist_ok=True)
BACKEND_DIR.mkdir(exist_ok=True)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads"""
    pass

class TennisVizHandler(BaseHTTPRequestHandler):
    """HTTP request handler for TennisViz app"""
    
    def __init__(self, *args, **kwargs):
        self.frontend_dir = str(FRONTEND_DIR)
        super().__init__(*args, **kwargs)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            # Parse the URL
            if self.path == '/' or self.path == '/tennisviz-app.html':
                self.serve_file('tennisviz-app.html')
            elif self.path.startswith('/api/'):
                self.handle_api_get()
            else:
                # Serve static files
                file_path = self.path.lstrip('/')
                self.serve_file(file_path)
        except Exception as e:
            print(f"❌ Error handling GET {self.path}: {e}")
            self.send_error(500, str(e))
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            if self.path == '/api/upload':
                self.handle_upload()
            elif self.path == '/api/analyze':
                self.handle_analyze()
            else:
                self.send_error(404, "API endpoint not found")
        except Exception as e:
            print(f"❌ Error handling POST {self.path}: {e}")
            self.send_error(500, str(e))
    
    def serve_file(self, filename):
        """Serve a static file"""
        file_path = Path(self.frontend_dir) / filename
        
        if not file_path.exists():
            self.send_error(404, f"File not found: {filename}")
            return
        
        # Determine content type
        content_type = self.get_content_type(filename)
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            # Add no-cache headers
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            # Add CORS headers
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(content)
            print(f"✅ Served: {filename} ({len(content)} bytes)")
            
        except Exception as e:
            print(f"❌ Error serving {filename}: {e}")
            self.send_error(500, str(e))
    
    def handle_upload(self):
        """Handle video upload - simplified version"""
        print("🎾 Handling video upload...")
        print(f"📋 Headers: {dict(self.headers)}")
        
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            print(f"📏 Content length: {content_length} bytes")
            
            if content_length == 0:
                print("❌ No content received")
                self.send_error(400, "No file uploaded")
                return
            
            # Read the raw data (we'll just acknowledge it for demo)
            print("📖 Reading upload data...")
            raw_data = self.rfile.read(content_length)
            print(f"✅ Read {len(raw_data)} bytes")
            
            # Extract basic info
            filename = "uploaded_video.mp4"  # Default filename
            
            # Try to extract filename from multipart data
            if b'filename=' in raw_data:
                try:
                    # Look for filename in the multipart data
                    data_str = raw_data.decode('utf-8', errors='ignore')
                    if 'filename="' in data_str:
                        start = data_str.find('filename="') + 10
                        end = data_str.find('"', start)
                        if start > 9 and end > start:
                            filename = data_str[start:end]
                            print(f"📝 Extracted filename: {filename}")
                except Exception as e:
                    print(f"⚠️ Could not extract filename: {e}")
            
            print(f"📁 Processing upload: {filename} ({content_length} bytes)")
            
            # Create mock analysis results
            mock_results = {
                "status": "success",
                "filename": filename,
                "size": content_length,
                "message": "Video uploaded successfully! 🎾",
                "timeline": [
                    {
                        "time": 2.5,
                        "stroke_type": "forehand",
                        "confidence": 0.85,
                        "description": "Clean forehand with good follow-through",
                        "contact_time": 2.5
                    },
                    {
                        "time": 5.1,
                        "stroke_type": "backhand", 
                        "confidence": 0.78,
                        "description": "Two-handed backhand, slightly late contact",
                        "contact_time": 5.1
                    },
                    {
                        "time": 8.3,
                        "stroke_type": "serve",
                        "confidence": 0.92,
                        "description": "First serve with good toss placement",
                        "contact_time": 8.3
                    }
                ],
                "analytics": {
                    "total_strokes": 3,
                    "forehand_count": 1,
                    "backhand_count": 1,
                    "serve_count": 1,
                    "average_confidence": 0.85,
                    "session_duration": 10.0
                },
                "ai_insights": {
                    "summary": "Good overall technique with consistent stroke mechanics. Focus on timing for backhand shots.",
                    "recommendations": [
                        "Work on earlier preparation for backhand shots",
                        "Maintain current serve toss consistency", 
                        "Continue developing forehand power"
                    ]
                },
                "stroke_events": [
                    {
                        "time": 2.5,
                        "stroke_type": "forehand",
                        "confidence": 0.85,
                        "court_position": [0.3, 0.7],
                        "technique_score": 8.5,
                        "contact_time": 2.5
                    },
                    {
                        "time": 5.1,
                        "stroke_type": "backhand",
                        "confidence": 0.78,
                        "court_position": [0.7, 0.6],
                        "technique_score": 7.8,
                        "contact_time": 5.1
                    },
                    {
                        "time": 8.3,
                        "stroke_type": "serve",
                        "confidence": 0.92,
                        "court_position": [0.5, 0.1],
                        "technique_score": 9.2,
                        "contact_time": 8.3
                    }
                ]
            }
            
            # Send JSON response
            self.send_json_response(mock_results)
            print("✅ Upload processed successfully!")
            
        except Exception as e:
            print(f"❌ Upload error: {e}")
            self.send_error(500, f"Upload failed: {str(e)}")
    
    def handle_analyze(self):
        """Handle video analysis request"""
        print("🔍 Handling analysis request...")
        
        # Simulate processing delay
        time.sleep(1)
        
        mock_results = {
            "status": "completed",
            "message": "Analysis completed successfully! 🎾",
            "results": {
                "stroke_events": [
                    {
                        "time": 1.2,
                        "stroke_type": "forehand",
                        "confidence": 0.89,
                        "court_position": [0.3, 0.7],
                        "technique_score": 8.5,
                        "contact_time": 1.2
                    },
                    {
                        "time": 3.8,
                        "stroke_type": "backhand",
                        "confidence": 0.82,
                        "court_position": [0.7, 0.6],
                        "technique_score": 7.8,
                        "contact_time": 3.8
                    }
                ],
                "analytics": {
                    "total_strokes": 2,
                    "average_confidence": 0.855
                }
            }
        }
        
        self.send_json_response(mock_results)
        print("✅ Analysis completed!")
    
    def handle_api_get(self):
        """Handle API GET requests"""
        if self.path == '/api/status':
            self.send_json_response({"status": "online", "message": "TennisViz API is running! 🎾"})
        else:
            self.send_error(404, "API endpoint not found")
    
    def send_json_response(self, data):
        """Send a JSON response"""
        json_data = json.dumps(data, indent=2).encode('utf-8')
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(json_data)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        self.wfile.write(json_data)
    
    def get_content_type(self, filename):
        """Get content type based on file extension"""
        ext = Path(filename).suffix.lower()
        content_types = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
            '.mp4': 'video/mp4',
            '.mov': 'video/quicktime',
            '.avi': 'video/x-msvideo'
        }
        return content_types.get(ext, 'application/octet-stream')
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"🌐 {format % args}")

def open_browser_delayed(url: str, delay: int = 3):
    """Open browser after server starts"""
    time.sleep(delay)
    print(f"🚀 Opening browser: {url}")
    webbrowser.open(url)

def main():
    """Start the universal local development server"""
    port = 8000
    host = "localhost"
    
    print("🎾 TennisViz Universal Local Development Server")
    print("=" * 60)
    print(f"📁 Frontend: {FRONTEND_DIR}")
    print(f"📁 Backend: {BACKEND_DIR}")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"📱 App URL: http://{host}:{port}/tennisviz-app.html")
    print("=" * 60)
    print("✨ Features:")
    print("  • Works with ALL Python versions")
    print("  • No external dependencies")
    print("  • Frontend serving with no-cache headers")
    print("  • Backend API for video uploads")
    print("  • Mock analysis results")
    print("  • Auto-opens browser")
    print("  • CORS enabled")
    print("=" * 60)
    
    try:
        # Create and start the server
        server_address = (host, port)
        httpd = ThreadedHTTPServer(server_address, TennisVizHandler)
        
        # Start browser in background thread
        browser_thread = threading.Thread(
            target=open_browser_delayed,
            args=(f"http://{host}:{port}/tennisviz-app.html",)
        )
        browser_thread.daemon = True
        browser_thread.start()
        
        print(f"🚀 Server started on http://{host}:{port}")
        print("💡 Press Ctrl+C to stop")
        print("🔄 Upload videos to test the complete flow!")
        print("📝 Check console for upload/analysis logs")
        print("🎯 Both file input click AND drag-and-drop should work!")
        
        # Start serving
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        httpd.shutdown()
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
