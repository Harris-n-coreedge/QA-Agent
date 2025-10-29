# QA Agent - Intelligent Test Automation Platform

A comprehensive quality assurance automation platform that combines AI-powered test generation, cross-browser testing, mobile testing, and intelligent reporting capabilities.

## 🚀 Features

### Core Capabilities
- **AI-Powered Test Generation** - Automatically generate test cases using Google Gemini AI
- **Cross-Browser Testing** - Support for Chromium, Firefox, and WebKit browsers
- **Mobile Testing** - Device-specific testing for iOS and Android devices
- **Performance Testing** - Load time monitoring and performance metrics
- **Accessibility Testing** - WCAG compliance checking
- **Security Testing** - XSS vulnerability detection and security headers validation
- **Real-time Reporting** - HTML, JSON, and PDF report generation

### Frontend Dashboard
- Modern React-based web interface
- Real-time test execution monitoring
- Interactive test result visualization
- Session management and browser automation control
- Mobile test screenshot viewing

### Backend API
- FastAPI-based REST API
- WebSocket support for real-time updates
- Configurable test execution parameters
- Database integration for test result storage

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Git

## 🛠️ Installation

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Harris-n-coreedge/QA-agent.git
   cd QA-agent
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the QA Agent**
   - Edit `qa_config.yaml` to set your preferences
   - Set up AI provider credentials (Google Gemini, OpenAI, or Anthropic)
   - Configure email settings for notifications

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

## 🚀 Quick Start

### Running the QA Agent

1. **Start the backend server**
   ```bash
   python standalone_backend.py
   ```

2. **Start the frontend dashboard**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the dashboard**
   - Open your browser and navigate to `http://localhost:5173`
   - The backend API will be available at `http://localhost:8000`

## ⚙️ Configuration

The QA Agent uses `qa_config.yaml` for configuration. Key settings include:

- **AI Configuration**: Provider selection, model settings, and token limits
- **Browser Configuration**: Headless mode, viewport settings, and browser arguments
- **Testing Parameters**: Timeouts, retry attempts, and screenshot settings
- **Mobile Testing**: Device configurations for various mobile devices
- **Performance Thresholds**: Load time and performance metrics limits

## 🔑 API Key Setup

To use AI features, you need to configure API keys:

1. **Google Gemini API** (Recommended)
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Set the environment variable: `export GOOGLE_API_KEY="your-api-key"`

## 📱 Mobile Testing

The platform supports testing on various mobile devices:

- iPhone 12/14 Pro
- iPhone SE
- Samsung Galaxy S21
- iPad
- Custom device configurations

## 🔧 API Endpoints

- `GET /health` - Health check endpoint
- `POST /api/qa-tests` - Create and execute QA tests
- `GET /api/runs` - Retrieve test run results
- `GET /api/projects` - Project management
- `WebSocket /ws` - Real-time test execution updates

## 📊 Reporting

The QA Agent generates comprehensive reports including:

- Test execution results
- Performance metrics
- Screenshots and videos
- Accessibility compliance reports
- Security vulnerability assessments

## 🐛 Troubleshooting

### Common Issues

1. **API Key Missing Error**

   **Solution**: Set up your API key as described in the API Key Setup section above.

2. **Browser Launch Issues**
   - Ensure Playwright browsers are installed: `playwright install`
   - Check browser configuration in `qa_config.yaml`

3. **Frontend Connection Issues**
   - Verify backend server is running on port 8000
   - Check CORS settings in backend configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---


**Developed by** | **Core Edge Solutions**

