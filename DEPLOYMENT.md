# 🎾 TennisViz Analytics - Deployment Guide

## Ensuring Correct HTML Page on Render

### Problem
Render might serve the old `index.html` instead of the new `tennisviz-app.html` PWA.

### Solution
The deployment is configured to automatically serve the TennisViz PWA:

### 1. **File Structure**
```
ai-tennis-deploy/
├── backend/
│   ├── tennisviz_api.py          # Main FastAPI app with proper routing
│   └── analytics/                # Analytics modules
├── frontend/
│   ├── tennisviz-app.html        # Main TennisViz PWA (THIS gets served)
│   ├── index.html.backup         # Old file (automatically backed up)
│   ├── manifest.json             # PWA manifest
│   └── sw.js                     # Service worker
├── start.py                      # Startup script (handles routing)
├── render.yaml                   # Render configuration
└── requirements.txt              # Dependencies
```

### 2. **Automatic Routing Setup**
The FastAPI backend (`tennisviz_api.py`) includes these routes:

```python
@app.get("/")
async def root():
    return FileResponse("frontend/tennisviz-app.html")  # Serves TennisViz PWA

@app.get("/index.html")
async def serve_index():
    return FileResponse("frontend/tennisviz-app.html")  # Redirects to TennisViz PWA
```

### 3. **Startup Script Protection**
The `start.py` script automatically:
- Backs up old `index.html` to prevent conflicts
- Verifies `tennisviz-app.html` exists
- Sets up proper Python paths
- Starts the server with correct configuration

## Overview
Your Tennis AI app is now a modern Progressive Web App (PWA) with a stellar mobile-first design that works seamlessly across web, iOS, and Android platforms.

## 🚀 Quick Start

### Local Development
1. **Activate virtual environment:**
   ```bash
   .\venv\Scripts\Activate.ps1  # Windows
   source venv/bin/activate     # macOS/Linux
   ```

2. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn python-multipart
   ```

3. **Start the server:**
   ```bash
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access the app:**
   - Open http://localhost:8000 in your browser
   - The app will automatically serve the new mobile-first frontend

## 📱 Mobile Features

### Progressive Web App (PWA)
- **Installable**: Users can install the app on their home screen
- **Offline Support**: Service worker caches resources for offline use
- **Native Feel**: Full-screen experience with custom splash screen
- **Push Notifications**: Ready for future notification features

### Mobile-First Design
- **Responsive Layout**: Optimized for all screen sizes
- **Touch-Friendly**: Large tap targets and intuitive gestures
- **Fast Loading**: Optimized assets and lazy loading
- **Dark Mode**: Automatic dark mode support based on system preference

## 🌐 Web Deployment

### Option 1: Vercel (Recommended for Frontend)
1. **Prepare for deployment:**
   ```bash
   # Create vercel.json in root directory
   ```

2. **Deploy:**
   ```bash
   npm i -g vercel
   vercel --prod
   ```

### Option 2: Netlify
1. **Build command:** Not needed (static files)
2. **Publish directory:** `frontend`
3. **Redirects:** Add `_redirects` file for SPA routing

### Option 3: Traditional Hosting
- Upload `frontend` folder contents to your web server
- Ensure server supports SPA routing (redirect all routes to index.html)

## 📱 Mobile App Deployment

### iOS App Store (via PWA)
1. **Test on iOS Safari:**
   - Open your deployed web app
   - Tap Share → Add to Home Screen
   - Test the installed PWA

2. **Submit to App Store:**
   - Use tools like PWABuilder or Capacitor to wrap your PWA
   - Follow Apple's App Store guidelines
   - Submit through App Store Connect

### Android Play Store (via PWA)
1. **Test on Android Chrome:**
   - Open your deployed web app
   - Chrome will show "Add to Home Screen" banner
   - Test the installed PWA

2. **Submit to Play Store:**
   - Use Trusted Web Activity (TWA) or PWABuilder
   - Create Android App Bundle
   - Submit through Google Play Console

### Alternative: Capacitor (Native Wrapper)
```bash
# Install Capacitor
npm install @capacitor/core @capacitor/cli

# Initialize
npx cap init

# Add platforms
npx cap add ios
npx cap add android

# Build and sync
npx cap sync

# Open in native IDEs
npx cap open ios
npx cap open android
```

## 🔧 Backend Deployment

### Option 1: Railway
1. **Connect GitHub repo**
2. **Add environment variables**
3. **Deploy automatically**

### Option 2: Heroku
```bash
# Create Procfile
echo "web: uvicorn backend.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### Option 3: DigitalOcean App Platform
1. **Connect GitHub repo**
2. **Configure build settings**
3. **Set environment variables**
4. **Deploy**

## 🔒 Production Considerations

### Security
- [ ] Add HTTPS (required for PWA features)
- [ ] Configure CORS properly
- [ ] Add rate limiting
- [ ] Validate file uploads
- [ ] Add authentication if needed

### Performance
- [ ] Enable gzip compression
- [ ] Add CDN for static assets
- [ ] Optimize video processing
- [ ] Add database for user data
- [ ] Implement caching strategies

### Monitoring
- [ ] Add error tracking (Sentry)
- [ ] Set up analytics
- [ ] Monitor server performance
- [ ] Add health checks

## 📊 Analytics & Monitoring

### Web Analytics
```html
<!-- Add to index.html head -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### PWA Analytics
- Track installation events
- Monitor offline usage
- Measure performance metrics

## 🎯 App Store Optimization

### App Store Listing
- **Title:** Tennis AI - Stroke Analysis
- **Subtitle:** AI-powered tennis coaching
- **Keywords:** tennis, AI, coaching, sports, analysis
- **Description:** Professional tennis stroke analysis powered by AI

### Screenshots
- Create screenshots for different device sizes
- Show key features and benefits
- Include before/after comparisons

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to production
        run: |
          # Your deployment commands
```

## 📈 Future Enhancements

### Planned Features
- [ ] Real-time video analysis
- [ ] Social sharing
- [ ] Progress tracking
- [ ] Coach recommendations
- [ ] Multi-language support
- [ ] Advanced analytics dashboard

### Technical Improvements
- [ ] WebRTC for live analysis
- [ ] Machine learning model improvements
- [ ] Database integration
- [ ] User authentication
- [ ] Payment processing
- [ ] Admin dashboard

## 🆘 Troubleshooting

### Common Issues
1. **PWA not installing:** Check HTTPS and manifest.json
2. **Service worker errors:** Clear cache and reload
3. **Video upload fails:** Check file size limits
4. **Mobile layout issues:** Test on actual devices

### Debug Tools
- Chrome DevTools → Application tab
- Lighthouse for PWA audit
- Mobile device simulators
- Real device testing

## 📞 Support
For deployment issues or questions, refer to the documentation or create an issue in the repository.

---

🎾 **Your Tennis AI app is now ready for the world!** The modern, mobile-first design will provide users with a stellar experience across all platforms.
