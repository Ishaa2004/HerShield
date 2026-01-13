# HerShield - Women's Safety Route Planning App

HerShield is an AI-powered safety application that helps women plan safer routes, monitor their journeys in real-time, and access emergency assistance. The app uses machine learning to analyze crime data, street lighting, and other safety factors to recommend the safest routes.

## Features

- **🗺️ Smart Route Planning**: Get multiple route options with AI-powered safety scores
- **📍 Live Location Tracking**: Automatic GPS location detection with continuous real-time updates
- **🔄 Auto-Updating Maps**: Maps automatically update to show your current position as you move
- **📌 Quick Location Fill**: One-click button to set your current location as starting point
- **⚠️ Route Deviation Alerts**: Get notified if you deviate from your planned safe route
- **🚨 Emergency SOS**: Quick access to emergency contacts and services with location sharing
- **🤖 AI Safety Scoring**: Machine learning model analyzes multiple safety factors
- **📊 Interactive Maps**: Visual representation of routes with safety markers and 500m radius indicator
- **👥 Trusted Contacts**: Manage emergency contacts for instant alerts
- **📜 Alert History**: Track all safety alerts and SOS triggers

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Web browser (Chrome, Firefox, Edge, etc.)

## Installation

### Step 1: Clone or Download the Project

Download the project folder to your local machine.

### Step 2: Create Virtual Environment

Open a terminal/command prompt in the project folder and run:

```bash
python -m venv .venv
```

### Step 3: Activate Virtual Environment

**On Windows:**
```bash
.venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
source .venv/bin/activate
```

### Step 4: Install Required Packages

```bash
pip install streamlit folium streamlit-folium geopy pandas numpy scikit-learn streamlit-js-eval
```

### Step 5: Train the AI Model (Optional - First Time Only)

```bash
python "hershield1 (1) (1).py"
```

This will create the AI model with ~91% accuracy and save it to `AI_Model/model_artifacts/simple_model.pkl`.

## Running the Application

### Start the Web Application

```bash
streamlit run "homepage.py"
```

The app will automatically open in your default web browser at `http://localhost:8501` (or another port if 8501 is busy).

### Using the Application

#### 🌍 Initial Setup
- When you first open the app, it will automatically request location access from your browser
- Click "Allow" when prompted to enable live GPS tracking
- Your location will be continuously tracked and updated on all maps
- Use the "🔄 Update" button to manually refresh your location anytime

#### 1. Plan Route Tab
- **Set Starting Point**: 
  - Click "📍 Use My Current Location as Start" to auto-fill with your GPS coordinates
  - Or manually enter a location name (e.g., "Connaught Place")
  - Or enter coordinates directly (e.g., "28.618750, 77.066630")
- **Set Destination**: Enter your destination location
- **Select Date & Time**: Choose when you plan to travel
- **Find Routes**: Click "🔍 Find Safe Routes" to see all available route options
- **Review Options**: Compare routes by safety score, risk level, distance, and duration
- **Select Route**: Click on your preferred route to track it during your journey

#### 2. Monitoring Tab
- **Live Location**: View your real-time GPS coordinates
- **Current Position Map**: See your location marked with a red home icon and 500m pink circle
- **Route Tracking**: If you selected a route, monitor your progress along the safe path
- **Deviation Alerts**: Get warned if you move away from the planned route
- **Start/Stop Monitoring**: Control journey tracking with simple buttons
- **Auto-Refresh**: Location and maps update automatically as you move

#### 3. Emergency Tab
- **SOS Button**: Large red emergency button to trigger instant alerts
- **Emergency Contacts**: View all your trusted contacts
- **Location Sharing**: Your current GPS location is automatically shared during emergencies
- **Quick Dial Numbers**: Access to Police (100) and Women Helpline (1091)
- **Live Map**: See your current location for sharing with authorities

## Project Structure

```
HerShield/
├── homepage.py                      # Main Streamlit web application
├── hershield1 (1) (1).py           # AI model training script
├── hershielddata (1) (1).py        # Data generation script
├── README.md                        # This file
└── AI_Model/
    └── model_artifacts/
        └── simple_model.pkl         # Trained AI model
```

## Package Dependencies

- **streamlit**: Web application framework
- **folium**: Interactive map visualization
- **streamlit-folium**: Streamlit-Folium integration
- **geopy**: Geocoding and distance calculations
- **pandas**: Data manipulation
- **numpy**: Numerical computations
- **scikit-learn**: Machine learning library
- **streamlit-js-eval**: Browser geolocation access

## Troubleshooting

### Port Already in Use

If you see an error about the port being in use, you can specify a different port:

```bash
streamlit run "homepage.py" --server.port 8502
```

### Location Not Detected

- **Allow Location Access**: Click "Allow" when your browser prompts for location permission
- **Secure Context Required**: Geolocation only works on HTTPS or localhost
- **Manual Refresh**: Click the "🔄 Update" button to refresh your location
- **Manual Entry**: Use the "🔧 Manually Change Location" expander to enter coordinates
- **Browser Compatibility**: Works best on Chrome, Firefox, and Edge
- **Troubleshooting**: If location still doesn't work, try:
  - Refreshing the entire page (F5)
  - Checking browser location settings
  - Ensuring location services are enabled on your device

### Module Not Found Error

Make sure you have activated the virtual environment and installed all packages:

```bash
.venv\Scripts\Activate.ps1
pip install streamlit folium streamlit-folium geopy pandas numpy scikit-learn streamlit-js-eval
```

## Demo Mode

The application currently runs in demo mode with mock route data. This is perfect for testing and demonstration purposes. Future versions will include:
- Real-time backend API integration
- MongoDB database for crime and safety data
- Live traffic and incident updates

## Technical Details

- **AI Model**: Logistic Regression trained on synthetic safety data (~91% accuracy)
- **Live Location**: HTML5 Geolocation API via streamlit-js-eval
- **Map Provider**: OpenStreetMap via Folium
- **Geocoding**: Nominatim (OpenStreetMap) with 15+ pre-configured Delhi locations
- **Frontend**: Streamlit with custom CSS styling
- **State Management**: Streamlit session state for persistent data
- **Real-time Updates**: Automatic location refresh and map updates
- **Location Accuracy**: Tracks movements >10 meters and displays distance moved
- **Map Features**: 
  - Red home marker for current location
  - 500m pink circle showing your area
  - Color-coded routes (green=safe, orange=moderate, red=unsafe)
  - Interactive popups with location details

## Future Enhancements

- [ ] Backend API server integration
- [ ] Real crime data integration from government databases
- [ ] Community-reported incidents system
- [ ] Public transport safety ratings
- [ ] Offline map support for areas with poor connectivity
- [ ] Mobile app version (iOS and Android)
- [ ] Voice-activated emergency alerts
- [ ] Integration with smartwatch devices
- [ ] Automatic family/friend notifications when monitoring starts
- [ ] Historical safety data analysis for specific routes

## Privacy & Safety

- Location data is processed locally and never stored without consent
- Emergency contacts are stored only in your browser session
- No personal data is transmitted to external servers in demo mode

## License

This project is for educational and demonstration purposes.

## Support

For issues or questions, please check:
1. All dependencies are installed
2. Virtual environment is activated
3. Python version is 3.8 or higher
4. Browser allows location access

---

**Stay Safe with HerShield! 🛡️**
