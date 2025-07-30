"""
🎾 TENNISVIZ DEMO SERVER
Simple HTTP server to demonstrate the TennisViz PWA frontend
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# Configuration
PORT = 8000
FRONTEND_DIR = Path(__file__).parent / "frontend"

class TennisVizHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)
    
    def end_headers(self):
        # Add CORS headers for PWA
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        # Add PWA headers
        if self.path.endswith('.js'):
            self.send_header('Content-Type', 'application/javascript')
        elif self.path.endswith('.json'):
            self.send_header('Content-Type', 'application/json')
        elif self.path.endswith('.html'):
            self.send_header('Content-Type', 'text/html')
        
        super().end_headers()
    
    def do_GET(self):
        # Serve the TennisViz PWA for root requests
        if self.path == '/' or self.path == '/index.html':
            self.path = '/tennisviz-app.html'
        
        # Handle PWA manifest
        elif self.path == '/manifest.json':
            self.path = '/manifest.json'
        
        # Handle service worker
        elif self.path == '/sw.js':
            self.path = '/sw.js'
        
        # Redirect old paths to new TennisViz app
        elif self.path in ['/timeline_viewer.html', '/old-index.html']:
            self.send_response(302)
            self.send_header('Location', '/tennisviz-app.html')
            self.end_headers()
            return
        
        return super().do_GET()
    
    def do_POST(self):
        # Mock API response for demo
        if self.path.startswith('/api/'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # Mock response for analysis
            mock_response = {
                "analysis_id": "demo_analysis_001",
                "status": "success",
                "timeline": [
                    {
                        "timestamp": 1.5,
                        "stroke_type": "forehand",
                        "confidence": 0.92,
                        "court_position": "baseline_center",
                        "technique_score": 8.5
                    },
                    {
                        "timestamp": 3.2,
                        "stroke_type": "backhand",
                        "confidence": 0.88,
                        "court_position": "baseline_left",
                        "technique_score": 7.8
                    },
                    {
                        "timestamp": 5.1,
                        "stroke_type": "serve",
                        "confidence": 0.95,
                        "court_position": "service_line",
                        "technique_score": 9.2
                    }
                ],
                "analytics": {
                    "session_overview": {
                        "total_strokes": 3,
                        "duration": 6.5,
                        "avg_technique_score": 8.5
                    },
                    "stroke_distribution": {
                        "forehand": 33.3,
                        "backhand": 33.3,
                        "serve": 33.3
                    },
                    "performance_metrics": {
                        "consistency": 85.2,
                        "power": 78.9,
                        "accuracy": 82.1
                    }
                },
                "ai_insights": {
                    "summary": "Great session! Your serve technique is excellent with a 9.2/10 score. Focus on improving backhand consistency.",
                    "recommendations": [
                        "Practice cross-court backhand shots",
                        "Work on follow-through for more power",
                        "Maintain excellent serve form"
                    ],
                    "key_patterns": [
                        "Strong serve placement and timing",
                        "Consistent baseline positioning",
                        "Good stroke variety"
                    ]
                }
            }
            
            import json
            self.wfile.write(json.dumps(mock_response).encode())
            return
        
        # Default response
        self.send_response(404)
        self.end_headers()

def main():
    """Start the TennisViz demo server"""
    
    print("🎾 Starting TennisViz Demo Server...")
    print(f"📁 Serving from: {FRONTEND_DIR}")
    print(f"🌐 Server will run on: http://localhost:{PORT}")
    
    # Check if frontend files exist
    html_file = FRONTEND_DIR / "tennisviz-app.html"
    if not html_file.exists():
        print("❌ Frontend files not found!")
        print(f"   Expected: {html_file}")
        return
    
    try:
        # Start server
        with socketserver.TCPServer(("", PORT), TennisVizHandler) as httpd:
            print(f"✅ TennisViz Demo Server running on port {PORT}")
            print(f"🚀 Open your browser to: http://localhost:{PORT}")
            print("📱 The PWA will work on mobile devices too!")
            print("\n🎯 Demo Features:")
            print("   • Mobile-first PWA interface")
            print("   • File upload simulation")
            print("   • Mock tennis analysis results")
            print("   • Service worker caching")
            print("   • Offline functionality")
            print("\n⚡ To stop the server, press Ctrl+C")
            
            # Try to open browser automatically
            try:
                webbrowser.open(f'http://localhost:{PORT}')
                print("🌐 Browser opened automatically")
            except:
                print("🌐 Please open your browser manually")
            
            # Serve forever
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except OSError as e:
        if e.errno == 10048:  # Port already in use
            print(f"❌ Port {PORT} is already in use!")
            print("   Try a different port or stop the other server")
        else:
            print(f"❌ Server error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
