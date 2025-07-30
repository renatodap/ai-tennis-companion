@echo off
echo 🎾 Starting TennisViz Universal Local Development Server...
echo.
echo This includes:
echo   • Works with ALL Python versions
echo   • No external dependencies
echo   • Frontend serving (no-cache headers)
echo   • Backend API for video uploads
echo   • Mock analysis results
echo   • Auto-opens browser
echo   • CORS enabled
echo.
echo You can now test video uploads locally!
echo Both file input click AND drag-and-drop should work!
echo.
python universal_local_server.py
pause
