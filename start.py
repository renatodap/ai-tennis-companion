#!/usr/bin/env python3
"""
🎾 TENNISVIZ STARTUP SCRIPT
Ensures proper deployment on Render with correct file serving
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Setup environment for production deployment"""
    
    # Add backend to Python path
    backend_path = Path(__file__).parent / "backend"
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))
    
    # Ensure frontend files exist
    frontend_path = Path(__file__).parent / "frontend"
    tennisviz_app = frontend_path / "tennisviz-app.html"
    
    if not tennisviz_app.exists():
        print(f"❌ TennisViz PWA not found: {tennisviz_app}")
        sys.exit(1)
    
    # Remove or rename old index.html to prevent conflicts
    old_index = frontend_path / "index.html"
    if old_index.exists():
        backup_index = frontend_path / "index.html.backup"
        if not backup_index.exists():
            old_index.rename(backup_index)
            print(f"📁 Backed up old index.html to index.html.backup")
    
    print("✅ Environment setup complete")
    print(f"📁 Frontend path: {frontend_path}")
    print(f"🎾 TennisViz PWA: {tennisviz_app}")

def main():
    """Main startup function"""
    print("🎾 Starting TennisViz Analytics System...")
    
    # Setup environment
    setup_environment()
    
    # Import and run the FastAPI app
    try:
        import uvicorn
        from backend.tennisviz_api import app
        
        # Get port from environment (Render sets this)
        port = int(os.environ.get("PORT", 8000))
        host = "0.0.0.0"
        
        print(f"🚀 Starting server on {host}:{port}")
        
        # Run the server
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
