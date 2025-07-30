#!/usr/bin/env python3
"""
🎾 TennisViz Local Development Server
Serves frontend files with no-cache headers to prevent stale content
"""

import os
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading
import time

class NoCacheHTTPRequestHandler(SimpleHTTPRequestHandler):
    """HTTP request handler that prevents caching"""
    
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        super().__init__(*args, directory=str(Path(__file__).parent / "frontend"), **kwargs)
    
    def end_headers(self):
        # Add no-cache headers to prevent browser caching
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        # Default to serving tennisviz-app.html for root path
        if self.path == '/':
            self.path = '/tennisviz-app.html'
        
        # Add cache-busting timestamp to prevent stale JS/CSS
        if self.path.endswith(('.js', '.css', '.html')):
            print(f"🔄 Serving fresh file: {self.path}")
        
        super().do_GET()
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"🌐 {format % args}")

def open_browser_delayed(url, delay=2):
    """Open browser after a short delay"""
    time.sleep(delay)
    print(f"🚀 Opening browser: {url}")
    webbrowser.open(url)

def main():
    """Start the local development server"""
    port = 3000
    server_address = ('localhost', port)
    
    print("🎾 TennisViz Local Development Server")
    print("=" * 50)
    print(f"📁 Serving from: {Path(__file__).parent / 'frontend'}")
    print(f"🌐 Server URL: http://localhost:{port}")
    print(f"📱 App URL: http://localhost:{port}/tennisviz-app.html")
    print("=" * 50)
    print("✨ Features:")
    print("  • No-cache headers (always fresh files)")
    print("  • Auto-opens browser")
    print("  • Real-time file serving")
    print("=" * 50)
    
    try:
        # Create and start the server
        httpd = HTTPServer(server_address, NoCacheHTTPRequestHandler)
        
        # Open browser in a separate thread
        browser_thread = threading.Thread(
            target=open_browser_delayed, 
            args=(f"http://localhost:{port}/tennisviz-app.html",)
        )
        browser_thread.daemon = True
        browser_thread.start()
        
        print(f"🚀 Server started on http://localhost:{port}")
        print("💡 Press Ctrl+C to stop the server")
        print("🔄 Files are served fresh (no caching) - refresh browser to see changes!")
        
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
