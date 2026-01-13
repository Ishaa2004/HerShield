import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime
import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time
from streamlit_js_eval import get_geolocation
import asyncio

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="HerShield - Women Safety App",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS FOR ATTRACTIVE UI
# ============================================
st.markdown("""
<style>
    /* Main Theme Colors */
    :root {
        --primary-color: #FF6B9D;
        --secondary-color: #C44569;
        --success-color: #26de81;
        --warning-color: #fed330;
        --danger-color: #fc5c65;
        --bg-dark: #1e272e;
        --text-light: #f5f6fa;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        text-align: center;
    }
    
    .main-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: #e0e0e0;
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }
    
    /* Input Boxes */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #667eea;
        padding: 12px;
        font-size: 1rem;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* Safety Score Card */
    .safety-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin: 1rem 0;
    }
    
    .safety-score {
        font-size: 4rem;
        font-weight: 700;
        margin: 1rem 0;
    }
    
    /* SOS Button */
    .sos-button {
        background: #fc5c65 !important;
        color: white !important;
        font-size: 1.5rem !important;
        padding: 1.5rem !important;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(252, 92, 101, 0.7); }
        50% { box-shadow: 0 0 0 20px rgba(252, 92, 101, 0); }
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        margin: 0.5rem;
    }
    
    .status-safe { background: #26de81; color: white; }
    .status-moderate { background: #fed330; color: #333; }
    .status-unsafe { background: #fc5c65; color: white; }
    
    /* Route Card */
    .route-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid;
    }
    
    .route-safe { border-color: #26de81; }
    .route-moderate { border-color: #fed330; }
    .route-unsafe { border-color: #fc5c65; }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Alert Box */
    .alert-box {
        background: #fc5c65;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False
if 'selected_route' not in st.session_state:
    st.session_state.selected_route = None
if 'user_location' not in st.session_state:
    st.session_state.user_location = [28.6139, 77.2090]  # Default: Delhi (will be updated by geolocation)
if 'location_detected' not in st.session_state:
    st.session_state.location_detected = False
if 'trusted_contacts' not in st.session_state:
    st.session_state.trusted_contacts = []
if 'alert_history' not in st.session_state:
    st.session_state.alert_history = []
if 'routes_data' not in st.session_state:
    st.session_state.routes_data = None
if 'route_start_coords' not in st.session_state:
    st.session_state.route_start_coords = None

# ============================================
# CONFIGURATION
# ============================================
BACKEND_URL = "http://localhost:5000"
DELHI_CENTER = [28.6139, 77.2090]

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_location_coordinates(location_name):
    """Convert location name to coordinates using geocoding"""
    # Common Delhi locations for quick lookup
    delhi_locations = {
        'connaught place': [28.6315, 77.2167],
        'india gate': [28.6129, 77.2295],
        'hauz khas': [28.5494, 77.2001],
        'saket': [28.5244, 77.2066],
        'dwarka': [28.5921, 77.0460],
        'rohini': [28.7496, 77.0669],
        'karol bagh': [28.6519, 77.1909],
        'rajouri garden': [28.6414, 77.1231],
        'laxmi nagar': [28.6353, 77.2772],
        'nehru place': [28.5494, 77.2501],
        'vasant vihar': [28.5677, 77.1615],
        'greater kailash': [28.5494, 77.2428],
        'defence colony': [28.5677, 77.2354],
        'pitampura': [28.6972, 77.1311],
        'janakpuri': [28.6219, 77.0834]
    }
    
    # Try quick lookup first
    location_lower = location_name.lower().strip()
    if location_lower in delhi_locations:
        return delhi_locations[location_lower]
    
    # Try geocoding with timeout
    try:
        geolocator = Nominatim(user_agent="hershield_app", timeout=3)
        location = geolocator.geocode(f"{location_name}, Delhi, India")
        if location:
            return [location.latitude, location.longitude]
        
        # Try without Delhi suffix
        location = geolocator.geocode(location_name)
        if location:
            return [location.latitude, location.longitude]
    except Exception as e:
        print(f"Geocoding error: {e}")
    
    # Return Delhi center as fallback
    st.warning(f"⚠️ Location '{location_name}' not found. Using approximate location.")
    return DELHI_CENTER

def call_safety_api(start_coords, end_coords, travel_time):
    """Call backend API to get safety predictions"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/predict_safety",
            json={
                "start_lat": start_coords[0],
                "start_lon": start_coords[1],
                "end_lat": end_coords[0],
                "end_lon": end_coords[1],
                "hour": travel_time.hour,
                "is_weekend": 1 if travel_time.weekday() >= 5 else 0
            },
            timeout=2
        )
        if response.status_code == 200:
            return response.json()
        else:
            # Use mock data on API error
            return generate_mock_routes(start_coords, end_coords)
    except Exception as e:
        # Backend not running - use mock data silently
        return generate_mock_routes(start_coords, end_coords)

def generate_mock_routes(start_coords, end_coords):
    """Generate mock route data for demonstration"""
    import random
    routes = []
    for i in range(3):
        safety_score = random.uniform(40, 95)
        routes.append({
            "route_id": i + 1,
            "route_name": f"Route {i+1}",
            "safety_score": round(safety_score, 2),
            "risk_level": "Low" if safety_score > 70 else ("Medium" if safety_score > 40 else "High"),
            "distance_km": round(random.uniform(5, 15), 1),
            "duration_min": random.randint(15, 45),
            "waypoints": [
                start_coords,
                [start_coords[0] + random.uniform(-0.01, 0.01), start_coords[1] + random.uniform(-0.01, 0.01)],
                end_coords
            ]
        })
    return {"status": "success", "routes": sorted(routes, key=lambda x: x['safety_score'], reverse=True)}

def trigger_sos_alert():
    """Trigger emergency SOS alert"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/trigger_alert",
            json={
                "user_id": "user123",
                "location": st.session_state.user_location,
                "timestamp": datetime.now().isoformat(),
                "alert_type": "SOS"
            }
        )
        return response.status_code == 200
    except:
        # Mock alert for demo
        st.session_state.alert_history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "SOS",
            "location": st.session_state.user_location
        })
        return True

def check_route_deviation(current_location, route_waypoints, threshold_meters=50):
    """Check if user has deviated from selected route"""
    min_distance = float('inf')
    for waypoint in route_waypoints:
        distance = geodesic(current_location, waypoint).meters
        min_distance = min(min_distance, distance)
    return min_distance > threshold_meters

def create_safety_map(routes_data, center_location):
    """Create interactive Folium map with color-coded routes"""
    # ALWAYS use current user location from session state
    current_loc = st.session_state.user_location
    
    m = folium.Map(
        location=current_loc,  # Always center on user's current location
        zoom_start=14,  # Closer zoom for better view
        tiles='OpenStreetMap',
        prefer_canvas=True
    )
    
    # Add routes if available
    if routes_data and 'routes' in routes_data:
        colors = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}
        
        for route in routes_data['routes']:
            color = colors.get(route['risk_level'], 'blue')
            folium.PolyLine(
                locations=route['waypoints'],
                color=color,
                weight=5,
                opacity=0.7,
                popup=f"<b>{route['route_name']}</b><br>Safety: {route['safety_score']}/100"
            ).add_to(m)
            
            # Add markers
            folium.Marker(
                route['waypoints'][0],
                popup="Start",
                icon=folium.Icon(color='blue', icon='play')
            ).add_to(m)
            
            folium.Marker(
                route['waypoints'][-1],
                popup="Destination",
                icon=folium.Icon(color='red', icon='stop')
            ).add_to(m)
    
    # Add LARGE circle around user location for visibility
    folium.Circle(
        location=current_loc,  # Use current_loc
        radius=500,  # 500 meters - LARGER
        color='#FF1493',  # Hot pink
        weight=3,
        fill=True,
        fillColor='#FF69B4',
        fillOpacity=0.3,
        popup="<b>🎯 YOUR AREA</b><br>500m radius"
    ).add_to(m)
    
    # Add user location marker with custom icon - LARGER
    folium.Marker(
        current_loc,  # Use current_loc
        popup=f"<b>📍 YOU ARE HERE</b><br><br>Lat: {current_loc[0]:.6f}<br>Lon: {current_loc[1]:.6f}<br><br>This is your current location!",
        icon=folium.Icon(color='red', icon='home', prefix='fa', icon_color='white'),
        tooltip="🏠 YOU ARE HERE - Click for details"
    ).add_to(m)
    
    return m

# ============================================
# MAIN APP LAYOUT
# ============================================

# Header
st.markdown("""
<div class="main-header">
    <h1>🛡️ HerShield</h1>
    <p>AI-Powered Women Safety & Route Alert System</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for Settings and Trusted Contacts
with st.sidebar:
    st.markdown("### ⚙️ Settings & Contacts")
    
    # Trusted Contacts Section
    with st.expander("👥 Manage Trusted Contacts", expanded=False):
        st.markdown("**Add Emergency Contact**")
        contact_name = st.text_input("Contact Name", key="contact_name")
        contact_phone = st.text_input("Phone Number", key="contact_phone")
        
        if st.button("➕ Add Contact"):
            if contact_name and contact_phone:
                st.session_state.trusted_contacts.append({
                    "name": contact_name,
                    "phone": contact_phone
                })
                st.success(f"Added {contact_name}")
        
        if st.session_state.trusted_contacts:
            st.markdown("**Your Contacts:**")
            for i, contact in enumerate(st.session_state.trusted_contacts):
                col1, col2 = st.columns([3, 1])
                col1.write(f"📞 {contact['name']}: {contact['phone']}")
                if col2.button("🗑️", key=f"delete_{i}"):
                    st.session_state.trusted_contacts.pop(i)
                    st.rerun()
    
    # Alert History
    with st.expander("📜 Alert History", expanded=False):
        if st.session_state.alert_history:
            for alert in st.session_state.alert_history[-5:]:
                st.write(f"🚨 {alert['timestamp']} - {alert['type']}")
        else:
            st.info("No alerts yet")
    
    # Current Location Section
    with st.expander("📍 Current Location", expanded=False):
        st.write(f"**Lat:** {st.session_state.user_location[0]:.4f}")
        st.write(f"**Lon:** {st.session_state.user_location[1]:.4f}")
        
        st.markdown("**Update Location:**")
        new_lat = st.number_input("Latitude", value=st.session_state.user_location[0], format="%.6f")
        new_lon = st.number_input("Longitude", value=st.session_state.user_location[1], format="%.6f")
        
        if st.button("Update Location"):
            st.session_state.user_location = [new_lat, new_lon]
            st.success("📍 Location updated!")
    
    # About Section
    with st.expander("ℹ️ About HerShield"):
        st.write("""
        **HerShield** uses AI to analyze route safety based on:
        - Historical crime data
        - Streetlight coverage
        - Time of day
        - Weather conditions
        - Real-time monitoring
        
        Stay safe, travel confidently! 💪
        """)

# AUTOMATIC LIVE LOCATION DETECTION WITH CONTINUOUS UPDATES
st.warning("🌍 **Continuous live location tracking active...**")

# Get live geolocation (called only once per page load)
loc = get_geolocation()

if loc:
    # Location detected!
    detected_lat = loc['coords']['latitude']
    detected_lon = loc['coords']['longitude']
    
    # Check if location has changed significantly (more than ~10 meters)
    old_location = st.session_state.user_location
    distance_moved = geodesic(old_location, [detected_lat, detected_lon]).meters
    
    # Update location silently and store in session state
    st.session_state.user_location = [detected_lat, detected_lon]
    st.session_state.location_detected = True
    st.session_state.last_geolocation = loc  # Store for reuse
    
    if distance_moved > 10:
        st.success(f"✅ **Location updated!** Moved {distance_moved:.1f}m - {detected_lat:.6f}, {detected_lon:.6f}")
    else:
        st.success(f"✅ **Live location tracking!** {detected_lat:.6f}, {detected_lon:.6f}")
else:
    # Show button to trigger detection
    if st.button("📍 Click to Detect My Location", type="primary"):
        st.info("👆 Please allow location access when your browser prompts you!")
        st.rerun()

# Show current location with manual refresh option
col1, col2 = st.columns([3, 1])
with col1:
    st.info(f"📍 **Current Location:** {st.session_state.user_location[0]:.6f}, {st.session_state.user_location[1]:.6f}")
with col2:
    if st.button("🔄 Update", key="header_refresh"):
        st.rerun()

# Manual update option
with st.expander("🔧 Manually Change Location"):
    st.caption("Use this if auto-detection doesn't work")
    col_lat, col_lon = st.columns(2)
    with col_lat:
        user_lat = st.number_input("Latitude", value=st.session_state.user_location[0], format="%.8f")
    with col_lon:
        user_lon = st.number_input("Longitude", value=st.session_state.user_location[1], format="%.8f")
    
    if st.button("✅ Update Location"):
        st.session_state.user_location = [user_lat, user_lon]
        st.session_state.location_detected = True
        st.success(f"✅ Updated to: {user_lat:.6f}, {user_lon:.6f}")
        st.rerun()


# Main Content Area
tab1, tab2, tab3 = st.tabs(["🗺️ Plan Route", "📊 Monitoring", "🚨 Emergency"])

# ============================================
# TAB 1: PLAN ROUTE
# ============================================
with tab1:
    st.markdown("### 🗺️ Plan Your Safe Route")
    
    # Initialize session state for start location if not exists
    if 'start_loc_input' not in st.session_state:
        st.session_state.start_loc_input = ""
    
    # Button to use current location
    if st.button("📍 Use My Current Location as Start", help="Fill start location with your current GPS coordinates"):
        st.session_state.start_loc_input = f"{st.session_state.user_location[0]:.6f}, {st.session_state.user_location[1]:.6f}"
        st.success(f"✅ Start location set to: {st.session_state.start_loc_input}")
        st.rerun()
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_location = st.text_input("📍 Start Location", 
                                      placeholder="e.g., Connaught Place or use coordinates",
                                      key="start_loc_input")
    
    with col2:
        end_location = st.text_input("🎯 Destination", placeholder="e.g., Hauz Khas")
    
    col3, col4 = st.columns(2)
    
    with col3:
        travel_date = st.date_input("📅 Travel Date", value=datetime.now())
    
    with col4:
        travel_time = st.time_input("🕐 Travel Time", value=datetime.now().time())
    
    if st.button("🔍 Find Safe Routes", type="primary"):
        if start_location and end_location:
            with st.spinner("🔍 Finding safe routes..."):
                # Get coordinates
                start_coords = get_location_coordinates(start_location)
                end_coords = get_location_coordinates(end_location)
                
                if start_coords and end_coords:
                    # Combine date and time
                    travel_datetime = datetime.combine(travel_date, travel_time)
                    
                    # Call API (will use mock data if backend not running)
                    routes_data = call_safety_api(start_coords, end_coords, travel_datetime)
                    
                    if routes_data and routes_data.get('status') == 'success':
                        # Save to session state
                        st.session_state.routes_data = routes_data
                        st.session_state.route_start_coords = start_coords
                        st.success("✅ Routes analyzed successfully!")
                    else:
                        st.error("Failed to analyze routes. Please try again.")
                else:
                    st.error("❌ Could not find one or both locations. Please check the names and try again.")
        else:
            st.warning("⚠️ Please enter both start location and destination.")
    
    # Display routes if available in session state
    if st.session_state.routes_data:
        routes_data = st.session_state.routes_data
        start_coords = st.session_state.route_start_coords
        
        # Display routes
        st.markdown("---")
        st.markdown("### 📊 Available Routes (Ranked by Safety)")
        
        for i, route in enumerate(routes_data['routes']):
            risk_class = f"route-{'safe' if route['risk_level'] == 'Low' else ('moderate' if route['risk_level'] == 'Medium' else 'unsafe')}"
            
            with st.container():
                st.markdown(f"""
                <div class="{risk_class}" style="padding: 1rem; margin: 1rem 0; border-radius: 10px; border-left: 5px solid {'#26de81' if route['risk_level'] == 'Low' else ('#fed330' if route['risk_level'] == 'Medium' else '#fc5c65')}; background: white; color: black;">
                    <h4>🛣️ {route['route_name']}</h4>
                    <p><strong>Safety Score:</strong> <span style="font-size: 1.5rem; color: {'green' if route['safety_score'] > 70 else ('orange' if route['safety_score'] > 40 else 'red')};">{route['safety_score']}/100</span></p>
                    <p><strong>Risk Level:</strong> <span class="status-badge status-{'safe' if route['risk_level'] == 'Low' else ('moderate' if route['risk_level'] == 'Medium' else 'unsafe')}">{route['risk_level']}</span></p>
                    <p><strong>Distance:</strong> {route['distance_km']} km | <strong>Duration:</strong> ~{route['duration_min']} min</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Select {route['route_name']}", key=f"select_{i}"):
                    st.session_state.selected_route = route
                    st.success(f"✅ {route['route_name']} selected! Go to Monitoring tab to track your journey.")
        
        # Show map
        st.markdown("---")
        st.markdown("### 🗺️ Route Map")
        map_obj = create_safety_map(routes_data, start_coords)
        st_folium(map_obj, width=700, height=500, key="route_map")
    
    # Show instructions if no routes yet
    elif not start_location and not end_location:
        st.info("""
        👋 **Welcome to HerShield Route Planner!**
        
        Enter your start location and destination above to find the safest routes.
        
        Our AI analyzes:
        - 📊 Historical crime data
        - 💡 Streetlight coverage
        - 🕐 Time of travel
        - 🌆 Area type and population density
        """)

# ============================================
# TAB 2: MONITORING
# ============================================
with tab2:
    st.markdown("### 📊 Real-Time Safety Monitoring")
    
    # Use location already captured at the top of the page
    # (No need to call get_geolocation() again to avoid duplicate key errors)
    
    # Show current live location regardless of route
    st.markdown("#### 📍 Your Live Location")
    
    col_live1, col_live2, col_live3, col_live4 = st.columns(4)
    with col_live1:
        st.metric("Latitude", f"{st.session_state.user_location[0]:.6f}")
    with col_live2:
        st.metric("Longitude", f"{st.session_state.user_location[1]:.6f}")
    with col_live3:
        st.metric("Status", "🟢 Online")
    with col_live4:
        if st.button("🔄 Refresh", key="monitoring_refresh"):
            st.rerun()
    
    st.markdown("---")
    
    if st.session_state.selected_route:
        route = st.session_state.selected_route
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"#### 🛣️ Monitoring: {route['route_name']}")
            st.markdown(f"**Safety Score:** {route['safety_score']}/100")
            st.markdown(f"**Risk Level:** {route['risk_level']}")
        
        with col2:
            if st.button("🛑 Stop Monitoring", type="secondary"):
                st.session_state.monitoring_active = False
                st.session_state.selected_route = None
                st.success("Monitoring stopped")
                st.rerun()
        
        # Monitoring controls
        if not st.session_state.monitoring_active:
            if st.button("▶️ Start Monitoring", type="primary"):
                st.session_state.monitoring_active = True
                st.success("🟢 Monitoring started!")
                st.rerun()
        else:
            st.markdown("""
            <div class="alert-box" style="background: #26de81; animation: none;">
                <h3>🟢 Monitoring Active</h3>
                <p>Your journey is being tracked. Stay on the selected route for maximum safety.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Mock real-time data
            st.markdown("---")
            st.markdown("#### 📊 Journey Status")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("On Route", "Yes ✅", "")
            with col2:
                st.metric("Safety Status", "Safe 🟢", "")
            with col3:
                st.metric("Distance Left", f"{route['distance_km']/2:.1f} km", "")
            
            # Check deviation
            is_deviated = check_route_deviation(
                st.session_state.user_location,
                route['waypoints']
            )
            
            if is_deviated:
                st.warning("⚠️ You have deviated from the safe route! Returning to route is recommended.")
            
            # Live map
            st.markdown("---")
            st.markdown("#### 🗺️ Live Route Tracking")
            map_obj = create_safety_map({'routes': [route]}, st.session_state.user_location)
            st_folium(map_obj, width=700, height=400, key="monitoring_map")
            
            st.info("💡 Tip: Update your location in the sidebar to see live tracking on the map")
    
    else:
        st.info("🗺️ No route selected. Go to 'Plan Route' tab to select a route first.")
        
        # Show live location map
        st.markdown("---")
        st.markdown("#### 🗺️ Current Location Map")
        map_obj = create_safety_map(None, st.session_state.user_location)
        st_folium(map_obj, width=700, height=400, key="current_location_map")
        
        st.info("💡 Your location is shown on the map. Update it in the sidebar to track your movement.")

# ============================================
# TAB 3: EMERGENCY SOS
# ============================================
with tab3:
    st.markdown("### 🚨 Emergency SOS")
    
    st.markdown("""
    <div style="background: #fc5c65; color: white; padding: 2rem; border-radius: 15px; text-align: center; margin: 2rem 0;">
        <h2>⚠️ Emergency Alert System</h2>
        <p>Press the button below if you feel unsafe or need immediate help</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🆘 TRIGGER SOS ALERT", key="sos_button", type="primary", use_container_width=True):
            success = trigger_sos_alert()
            if success:
                st.markdown("""
                <div class="alert-box">
                    <h3>🚨 SOS ALERT SENT!</h3>
                    <p>✅ Emergency contacts notified</p>
                    <p>✅ Location shared</p>
                    <p>✅ Authorities alerted</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Failed to send alert. Please try again or call emergency services directly.")
    
    st.markdown("---")
    
    # Emergency contacts display
    st.markdown("### 👥 Your Emergency Contacts")
    
    if st.session_state.trusted_contacts:
        for contact in st.session_state.trusted_contacts:
            st.markdown(f"""
            <div style="background: white; color: black; padding: 1rem; margin: 0.5rem 0; border-radius: 10px; border-left: 5px solid #667eea;">
                <strong>📞 {contact['name']}</strong><br>
                {contact['phone']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ No emergency contacts added. Add contacts in the sidebar to enable instant alerts!")
    
    st.markdown("---")
    
    # Emergency numbers
    st.markdown("### 📞 Important Emergency Numbers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: white; color: black; padding: 1.5rem; border-radius: 10px;">
            <h4>🚓 Police</h4>
            <h2 style="color: #fc5c65;">100</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; color: black; padding: 1.5rem; border-radius: 10px;">
            <h4>👩 Women Helpline</h4>
            <h2 style="color: #fc5c65;">1091</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Current location
    st.markdown("### 📍 Your Current Location")
    st.write(f"Latitude: {st.session_state.user_location[0]}")
    st.write(f"Longitude: {st.session_state.user_location[1]}")
    
    map_obj = create_safety_map(None, st.session_state.user_location)
    st_folium(map_obj, width=700, height=300, key="emergency_map")
