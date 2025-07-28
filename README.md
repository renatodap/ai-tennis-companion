# 🎾 Tennis AI - Stroke Analysis App

A modern, mobile-first Progressive Web App that uses AI to analyze tennis strokes and provide insights to improve your game.

![Version](https://img.shields.io/badge/version-2.0-blue)
![PWA](https://img.shields.io/badge/PWA-enabled-green)
![Mobile](https://img.shields.io/badge/mobile-first-orange)
![License](https://img.shields.io/badge/license-MIT-blue)

## ✨ Features

### 🎯 Core Functionality
- **AI-Powered Analysis**: Advanced computer vision to detect and classify tennis strokes
- **Stroke Detection**: Identifies forehand, backhand, and serve strokes
- **Video Timeline**: Interactive timeline showing detected strokes with timestamps
- **Jump to Stroke**: Click any detected stroke to jump to that moment in the video

### 📱 Mobile-First Design
- **Progressive Web App**: Install on any device like a native app
- **Responsive Design**: Optimized for phones, tablets, and desktop
- **Touch-Friendly**: Large tap targets and intuitive gestures
- **Offline Support**: Works without internet connection after first load
- **Dark Mode**: Automatic dark mode based on system preference

### 🚀 Modern UX
- **Drag & Drop**: Easy video upload with drag and drop support
- **Real-time Progress**: Beautiful loading animations and progress indicators
- **Smooth Animations**: Fluid transitions and micro-interactions
- **Toast Notifications**: Elegant feedback messages
- **Modal Dialogs**: Clean, accessible modal interfaces

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Python**: Core processing and AI logic
- **OpenCV**: Computer vision for video processing
- **MediaPipe**: Pose estimation and keypoint detection

### Frontend
- **Vanilla JavaScript**: Modern ES6+ features
- **CSS3**: Advanced styling with CSS Grid and Flexbox
- **PWA**: Service Worker, Web App Manifest
- **Responsive Design**: Mobile-first approach

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ai-tennis-companion
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\Activate.ps1
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install fastapi uvicorn python-multipart
   ```

4. **Start the server:**
   ```bash
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Open the app:**
   Navigate to `http://localhost:8000` in your browser

## 📱 Mobile Installation

### iOS (Safari)
1. Open the app in Safari
2. Tap the Share button
3. Select "Add to Home Screen"
4. Tap "Add" to install

### Android (Chrome)
1. Open the app in Chrome
2. Tap the menu (three dots)
3. Select "Add to Home screen"
4. Tap "Add" to install

## 🎮 How to Use

1. **Upload Video**: Drag and drop or select a tennis video file
2. **Wait for Analysis**: The AI will process your video and detect strokes
3. **Review Results**: See detected strokes in the timeline below the video
4. **Jump to Strokes**: Click any stroke to jump to that moment in the video
5. **View Stats**: Check the session summary for stroke counts

### 📋 Tips for Best Results
- Record in landscape mode
- Keep the player clearly visible in frame
- Use good lighting conditions
- Maintain a stable camera position
- Video files should be under 100MB

## 🏗️ Project Structure

```
ai-tennis-companion/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── upload.py            # Video upload and analysis endpoints
│   ├── process_video.py     # Video frame extraction
│   ├── classify_strokes.py  # AI stroke classification
│   └── utils/               # Utility functions
├── frontend/
│   ├── index.html           # Main HTML file
│   ├── styles.css           # Modern CSS styles
│   ├── app.js               # JavaScript application logic
│   ├── manifest.json        # PWA manifest
│   ├── sw.js                # Service worker
│   └── icons/               # App icons
├── requirements.txt         # Python dependencies
├── DEPLOYMENT.md           # Deployment guide
└── README.md               # This file
```

## 🎨 Design System

### Color Palette
- **Primary**: `#1e40af` (Blue)
- **Secondary**: `#10b981` (Green)
- **Accent**: `#f59e0b` (Amber)
- **Background**: `#f8fafc` (Light Gray)
- **Surface**: `#ffffff` (White)

### Typography
- **Font Family**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700

### Components
- Modern card-based layout
- Rounded corners and subtle shadows
- Smooth hover and focus states
- Accessible color contrast ratios

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment instructions including:
- Web hosting options (Vercel, Netlify, etc.)
- Mobile app store deployment
- Backend hosting solutions
- CI/CD setup

## 🔮 Future Enhancements

### Planned Features
- [ ] Real-time video analysis
- [ ] Stroke technique scoring
- [ ] Progress tracking over time
- [ ] Social sharing capabilities
- [ ] Coach recommendations
- [ ] Multi-language support

### Technical Improvements
- [ ] Enhanced AI models
- [ ] WebRTC for live analysis
- [ ] User authentication
- [ ] Cloud storage integration
- [ ] Advanced analytics dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenCV community for computer vision tools
- MediaPipe team for pose estimation
- FastAPI creators for the excellent web framework
- Tennis community for inspiration and feedback

## 📞 Support

If you encounter any issues or have questions:
1. Check the [DEPLOYMENT.md](DEPLOYMENT.md) guide
2. Search existing issues
3. Create a new issue with detailed information

---

**Made with ❤️ for the tennis community**

🎾 *Improve your game with AI-powered analysis!*