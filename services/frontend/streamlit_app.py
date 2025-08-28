import streamlit as st
import requests
import json
from datetime import datetime
from typing import Optional, Dict, Any

st.set_page_config(
    page_title="Streaming Platform",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .auth-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Form container fix */
    .stForm {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    
    /* Input fields styling */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        color: white !important;
        border-radius: 8px !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 8px 8px 0 0 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.2) !important;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .content-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    .nav-button {
        margin: 0.2rem 0;
    }
    
    /* Dashboard specific styles */
    .dashboard-container {
        display: flex;
        height: 100vh;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .sidebar-nav {
        width: 250px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-right: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .main-content {
        flex: 1;
        padding: 2rem;
        overflow-y: auto;
    }
    
    .user-welcome {
        text-align: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
    }
    
    .nav-item {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        text-align: center;
    }
    
    .nav-item:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateX(5px);
    }
    
    .nav-item.active {
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .search-section {
        margin-bottom: 2rem;
    }
    
    .search-bar {
        width: 100%;
        padding: 1rem;
        border-radius: 25px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        background: rgba(255, 255, 255, 0.1);
        color: white;
        font-size: 1rem;
        margin-bottom: 1rem;
    }
    
    .search-bar::placeholder {
        color: rgba(255, 255, 255, 0.7);
    }
    
    .search-buttons {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .search-btn {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        background: rgba(255, 255, 255, 0.1);
        color: white;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .search-btn:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    
    .search-btn.active {
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .content-section {
        margin-bottom: 3rem;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: white;
    }
    
    .content-cards {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
    }
    
    .content-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.3s, box-shadow 0.3s;
        cursor: pointer;
        color: white;
    }
    
    .content-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    }
    
    .card-image {
        width: 100%;
        height: 150px;
        background: linear-gradient(45deg, #667eea, #764ba2);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .card-title {
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        color: white;
    }
    
    .card-info {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.8);
    }
</style>
""", unsafe_allow_html=True)

# API Base URLs
API_URLS = {
    'auth': 'http://authentication.services.svc.cluster.local:5000',
    'user': 'http://user.services.svc.cluster.local:8000',
    'movies': 'http://movies.services.svc.cluster.local:8081',
    'series': 'http://series.services.svc.cluster.local:8082',
    'search': 'http://search.services.svc.cluster.local:8080',
    'chatbot': 'http://chatbot.ai.svc.cluster.local:8091',
    'personalize': 'http://personalize.recommendation.svc.cluster.local:8001'
}

class APIClient:
    @staticmethod
    def make_request(method: str, url: str, data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Helper function for API requests"""
        try:
            if headers is None:
                headers = {'Content-Type': 'application/json'}
            
            # Add token to header if available
            if 'token' in st.session_state:
                headers['Authorization'] = f'Bearer {st.session_state.token}'
            
            if method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return {'success': False, 'message': 'Unsupported HTTP method'}
            
            if response.status_code in [200, 201]:
                return {'success': True, 'data': response.json()}
            else:
                error_msg = response.json().get('error', 'Unknown error') if response.content else f'HTTP {response.status_code}'
                return {'success': False, 'message': error_msg}
                
        except requests.exceptions.RequestException as e:
            return {'success': False, 'message': f'Connection error: {str(e)}'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def register_user(username: str, email: str, password: str, full_name: str) -> Dict[str, Any]:
        """User registration"""
        data = {
            'email': email,
            'password': password
        }
        return APIClient.make_request('POST', f"{API_URLS['auth']}/auth/signup", data)

    @staticmethod
    def login_user(username: str, password: str) -> Dict[str, Any]:
        """User login"""
        data = {
            'email': username,  # Frontend username olarak gönderiyor ama backend email bekliyor
            'password': password
        }
        return APIClient.make_request('POST', f"{API_URLS['auth']}/auth/login", data)

    @staticmethod
    def verify_token() -> Dict[str, Any]:
        """Token verification"""
        return APIClient.make_request('GET', f"{API_URLS['auth']}/auth/verify")

    @staticmethod
    def logout_user() -> Dict[str, Any]:
        """User logout"""
        return APIClient.make_request('POST', f"{API_URLS['auth']}/auth/logout")

    @staticmethod
    def get_movies() -> Dict[str, Any]:
        """Get movies from movies service"""
        return APIClient.make_request('GET', f"{API_URLS['movies']}/movies")

    @staticmethod
    def get_series() -> Dict[str, Any]:
        """Get series from series service"""
        return APIClient.make_request('GET', f"{API_URLS['series']}/series")

    @staticmethod
    def search_movies(query: str) -> Dict[str, Any]:
        """Search movies"""
        return APIClient.make_request('GET', f"{API_URLS['movies']}/search?q={query}")

    @staticmethod
    def search_series(query: str) -> Dict[str, Any]:
        """Search series"""
        return APIClient.make_request('GET', f"{API_URLS['series']}/search?q={query}")

    @staticmethod
    def get_recommendations() -> Dict[str, Any]:
        """Get personalized recommendations"""
        return APIClient.make_request('GET', f"{API_URLS['personalize']}/recommendations")

    @staticmethod
    def chat_with_bot(message: str) -> Dict[str, Any]:
        """Chat with chatbot"""
        data = {'message': message}
        return APIClient.make_request('POST', f"{API_URLS['chatbot']}/chat", data)

def is_logged_in() -> bool:
    """Check if user is logged in"""
    if 'token' in st.session_state and 'user_data' in st.session_state:
        # Verify token validity
        result = APIClient.verify_token()
        return result['success']
    return False

def logout():
    """Logout user"""
    if 'token' in st.session_state:
        APIClient.logout_user()
    
    # Clear session state
    for key in ['token', 'user_data', 'username', 'current_page']:
        if key in st.session_state:
            del st.session_state[key]

def navigate_to(page: str):
    """Navigate to a specific page"""
    st.session_state.current_page = page
    st.rerun()

def show_login_page():
    """Login page"""
    st.markdown('<div class="main-header"><h1>🎬 Streaming Platform</h1><p>Welcome to the World of Movies and TV Shows!</p></div>', unsafe_allow_html=True)
    
    # Tabs for login and registration
    # Check if we should show login tab after successful registration
    if st.session_state.get('show_login_tab', False):
        tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Sign Up"])
        st.session_state.show_login_tab = False
    else:
        tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Sign Up"])
    
    with tab1:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.subheader("Sign In")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_button = st.form_submit_button("🚀 Sign In", use_container_width=True)
            
            if login_button:
                if username and password:
                    with st.spinner("Signing in..."):
                        result = APIClient.login_user(username, password)
                    
                    if result['success']:
                        st.session_state.token = result['data']['token']
                        st.session_state.user_data = result['data']['user']
                        st.session_state.username = username
                        st.session_state.current_page = 'dashboard'
                        st.success("✅ Successfully signed in!")
                        st.rerun()
                    else:
                        st.error(f"❌ Sign in error: {result['message']}")
                else:
                    st.error("⚠️ Please fill in all fields!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Designer footer
    st.markdown('<div class="designer-footer">✨ Designed by Onur Yurtsever</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.subheader("Sign Up")
        
        with st.form("register_form"):
            full_name = st.text_input("Full Name", placeholder="Enter your full name")
            reg_username = st.text_input("Username", key="reg_username", placeholder="Choose a username")
            email = st.text_input("Email", key="reg_email", placeholder="Enter your email")
            reg_password = st.text_input("Password", type="password", key="reg_password", placeholder="At least 6 characters")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            register_button = st.form_submit_button("📝 Sign Up", use_container_width=True)
            
            if register_button:
                if all([full_name, reg_username, email, reg_password, confirm_password]):
                    if reg_password != confirm_password:
                        st.error("❌ Passwords don't match!")
                    elif len(reg_password) < 6:
                        st.error("❌ Password must be at least 6 characters!")
                    else:
                        with st.spinner("Creating account..."):
                            result = APIClient.register_user(reg_username, email, reg_password, full_name)
                        
                        if result['success']:
                            st.success("✅ Account created successfully! You can now sign in.")
                            st.balloons()
                            
                            # Prevent double submission
                            st.session_state.show_login_tab = True
                            st.session_state.registration_success = True
                            # Don't call st.rerun() here - let the form reset naturally
                        else:
                            st.error(f"❌ Registration error: {result['message']}")
                else:
                    st.error("⚠️ Please fill in all fields!")
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_dashboard():
    """Dashboard page with wireframe layout"""
    # Initialize session state for search
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    if 'search_type' not in st.session_state:
        st.session_state.search_type = "movies"
    
    # Main dashboard layout
    st.markdown("""
    <div class="dashboard-container">
        <div class="sidebar-nav">
            <div class="user-welcome">
                <h3>👋 Welcome</h3>
                <p><strong>{}</strong></p>
                <p>@{}</p>
            </div>
            
            <div class="nav-item" onclick="navigateTo('dashboard')">
                🏠 Dashboard
            </div>
            <div class="nav-item" onclick="navigateTo('movies')">
                🎬 Movies
            </div>
            <div class="nav-item" onclick="navigateTo('series')">
                📺 Series
            </div>
            <div class="nav-item" onclick="navigateTo('personalize')">
                ⭐ Personalize
            </div>
            <div class="nav-item" onclick="navigateTo('chatbot')">
                🤖 Chatbot
            </div>
        </div>
        
        <div class="main-content">
            <div class="search-section">
                <input type="text" class="search-bar" placeholder="🔍 Search bar" id="searchInput">
                <div class="search-buttons">
                    <button class="search-btn" onclick="searchMovies()">🎬 Movies</button>
                    <button class="search-btn" onclick="searchSeries()">📺 Series</button>
                </div>
            </div>
            
            <div class="content-section">
                <div class="section-title">🏆 Top Rated TV Shows</div>
                <div class="content-cards">
                    <div class="content-card">
                        <div class="card-image">📺</div>
                        <div class="card-title">Breaking Bad</div>
                        <div class="card-info">⭐ 9.5 | 2008-2013 | Crime Drama</div>
                    </div>
                    <div class="content-card">
                        <div class="card-image">🐉</div>
                        <div class="card-title">Game of Thrones</div>
                        <div class="card-info">⭐ 9.3 | 2011-2019 | Fantasy</div>
                    </div>
                    <div class="content-card">
                        <div class="card-image">🔍</div>
                        <div class="card-title">Sherlock</div>
                        <div class="card-info">⭐ 9.1 | 2010-2017 | Mystery</div>
                    </div>
                    <div class="content-card">
                        <div class="card-image">👽</div>
                        <div class="card-title">Stranger Things</div>
                        <div class="card-info">⭐ 8.7 | 2016-2025 | Sci-Fi</div>
                    </div>
                </div>
            </div>
            
            <div class="content-section">
                <div class="section-title">🎬 Top Rated Movies</div>
                <div class="content-cards">
                    <div class="content-card">
                        <div class="card-image">🕴️</div>
                        <div class="card-title">The Matrix</div>
                        <div class="card-info">⭐ 8.7 | 1999 | Sci-Fi Action</div>
                    </div>
                    <div class="content-card">
                        <div class="card-image">🌀</div>
                        <div class="card-title">Inception</div>
                        <div class="card-info">⭐ 8.8 | 2010 | Sci-Fi Thriller</div>
                    </div>
                    <div class="content-card">
                        <div class="card-image">🦇</div>
                        <div class="card-title">The Dark Knight</div>
                        <div class="card-info">⭐ 9.0 | 2008 | Action Crime</div>
                    </div>
                    <div class="content-card">
                        <div class="card-image">👑</div>
                        <div class="card-title">The Godfather</div>
                        <div class="card-info">⭐ 9.2 | 1972 | Crime Drama</div>
                    </div>
                    <div class="content-card">
                        <div class="card-image">🪐</div>
                        <div class="card-title">Interstellar</div>
                        <div class="card-info">⭐ 8.6 | 2014 | Sci-Fi Drama</div>
                    </div>
                    <div class="content-card">
                        <div class="card-image">🔫</div>
                        <div class="card-title">Pulp Fiction</div>
                        <div class="card-info">⭐ 8.9 | 1994 | Crime Thriller</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """.format(
        st.session_state.user_data.get('full_name', 'User'),
        st.session_state.user_data.get('username', '')
    ), unsafe_allow_html=True)
    
    # Add JavaScript for navigation and search
    st.markdown("""
    <script>
        function navigateTo(page) {
            // This would trigger navigation in Streamlit
            console.log('Navigating to:', page);
        }
        
        function searchMovies() {
            const query = document.getElementById('searchInput').value;
            console.log('Searching movies for:', query);
        }
        
        function searchSeries() {
            const query = document.getElementById('searchInput').value;
            console.log('Searching series for:', query);
        }
    </script>
    """, unsafe_allow_html=True)

def show_movies():
    """Movies page"""
    st.markdown('<div class="main-header"><h1>🎬 Movies</h1></div>', unsafe_allow_html=True)
    
    # Search functionality
    search_query = st.text_input("🔍 Search movies...", placeholder="Enter movie title")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎬 Search Movies", use_container_width=True):
            if search_query:
                with st.spinner("Searching movies..."):
                    result = APIClient.search_movies(search_query)
                    if result['success']:
                        st.success(f"Found {len(result['data'])} movies")
                        for movie in result['data']:
                            st.info(f"🎬 {movie.get('title', 'Unknown')} ({movie.get('year', 'N/A')})")
                    else:
                        st.error(f"Search error: {result['message']}")
            else:
                st.warning("Please enter a search query")
    
    with col2:
        if st.button("📋 Show All Movies", use_container_width=True):
            with st.spinner("Loading movies..."):
                result = APIClient.get_movies()
                if result['success']:
                    st.success(f"Loaded {len(result['data'])} movies")
                    for movie in result['data']:
                        st.info(f"🎬 {movie.get('title', 'Unknown')} ({movie.get('year', 'N/A')})")
                else:
                    st.error(f"Error loading movies: {result['message']}")
    
    st.divider()
    
    # Movie grid
    st.subheader("🎭 Popular Movies")
    
    movies = [
        {"title": "The Matrix", "year": 1999, "rating": 8.7, "genre": "Sci-Fi"},
        {"title": "Inception", "year": 2010, "rating": 8.8, "genre": "Sci-Fi"},
        {"title": "Pulp Fiction", "year": 1994, "rating": 8.9, "genre": "Crime"},
        {"title": "The Dark Knight", "year": 2008, "rating": 9.0, "genre": "Action"},
        {"title": "Forrest Gump", "year": 1994, "rating": 8.8, "genre": "Drama"},
        {"title": "The Godfather", "year": 1972, "rating": 9.2, "genre": "Crime"},
    ]
    
    cols = st.columns(3)
    for i, movie in enumerate(movies):
        with cols[i % 3]:
            st.info(f"""
            **{movie['title']}** ({movie['year']})
            
            Genre: {movie['genre']}
            
            ⭐ {movie['rating']}/10
            """)

def show_series():
    """TV Shows page"""
    st.markdown('<div class="main-header"><h1>📺 TV Shows</h1></div>', unsafe_allow_html=True)
    
    # Search functionality
    search_query = st.text_input("🔍 Search TV shows...", placeholder="Enter show title")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📺 Search Series", use_container_width=True):
            if search_query:
                with st.spinner("Searching series..."):
                    result = APIClient.search_series(search_query)
                    if result['success']:
                        st.success(f"Found {len(result['data'])} series")
                        for series in result['data']:
                            st.success(f"📺 {series.get('title', 'Unknown')} ({series.get('year', 'N/A')})")
                    else:
                        st.error(f"Search error: {result['message']}")
            else:
                st.warning("Please enter a search query")
    
    with col2:
        if st.button("📋 Show All Series", use_container_width=True):
            with st.spinner("Loading series..."):
                result = APIClient.get_series()
                if result['success']:
                    st.success(f"Loaded {len(result['data'])} series")
                    for series in result['data']:
                        st.success(f"📺 {series.get('title', 'Unknown')} ({series.get('year', 'N/A')})")
                else:
                    st.error(f"Error loading series: {result['message']}")
    
    st.divider()
    
    # TV Shows grid
    st.subheader("🏆 Top Rated Shows")
    
    shows = [
        {"title": "Breaking Bad", "seasons": 5, "rating": 9.5, "genre": "Drama"},
        {"title": "Game of Thrones", "seasons": 8, "rating": 9.3, "genre": "Fantasy"},
        {"title": "Stranger Things", "seasons": 4, "rating": 8.7, "genre": "Sci-Fi"},
        {"title": "The Office", "seasons": 9, "rating": 9.0, "genre": "Comedy"},
        {"title": "Friends", "seasons": 10, "rating": 8.9, "genre": "Comedy"},
        {"title": "Sherlock", "seasons": 4, "rating": 9.1, "genre": "Mystery"},
    ]
    
    cols = st.columns(3)
    for i, show in enumerate(shows):
        with cols[i % 3]:
            st.success(f"""
            **{show['title']}**
            
            Seasons: {show['seasons']}
            
            Genre: {show['genre']}
            
            ⭐ {show['rating']}/10
            """)

def show_personalize():
    """Personalize page"""
    st.markdown('<div class="main-header"><h1>⭐ Personalized Recommendations</h1></div>', unsafe_allow_html=True)
    
    st.subheader("🎯 Recommended for You")
    
    # Get recommendations from ML service
    with st.spinner("Loading personalized recommendations..."):
        result = APIClient.get_recommendations()
        if result['success']:
            recommendations = result['data']
            st.success(f"✅ Loaded {len(recommendations)} recommendations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🎬 Movies You Might Like")
                for rec in recommendations.get('movies', []):
                    st.info(f"""
                    **{rec.get('title', 'Unknown')}**
                    Match: {rec.get('match', 'N/A')}% | {rec.get('reason', 'Based on your preferences')}
                    """)
            
            with col2:
                st.markdown("### 📺 TV Shows You Might Like")
                for rec in recommendations.get('series', []):
                    st.success(f"""
                    **{rec.get('title', 'Unknown')}**
                    Match: {rec.get('match', 'N/A')}% | {rec.get('reason', 'Based on your preferences')}
                    """)
        else:
            st.error(f"❌ Error loading recommendations: {result['message']}")
            
            # Fallback recommendations
            st.markdown("### 🎬 Movies You Might Like")
            fallback_movies = [
                {"title": "Blade Runner 2049", "match": "95%", "reason": "Because you liked Sci-Fi movies"},
                {"title": "Interstellar", "match": "92%", "reason": "Based on your viewing history"},
                {"title": "Ex Machina", "match": "89%", "reason": "Similar to your favorites"},
            ]
            
            for rec in fallback_movies:
                st.info(f"""
                **{rec["title"]}**
                Match: {rec["match"]} | {rec["reason"]}
                """)
            
            st.markdown("### 📺 TV Shows You Might Like")
            fallback_series = [
                {"title": "Westworld", "match": "96%", "reason": "Because you liked Sci-Fi shows"},
                {"title": "Black Mirror", "match": "94%", "reason": "Based on your preferences"},
                {"title": "Altered Carbon", "match": "91%", "reason": "Similar themes you enjoy"},
            ]
            
            for rec in fallback_series:
                st.success(f"""
                **{rec["title"]}**
                Match: {rec["match"]} | {rec["reason"]}
                """)

def show_chatbot():
    """AI Chatbot page"""
    st.markdown('<div class="main-header"><h1>🤖 AI Chat Assistant</h1></div>', unsafe_allow_html=True)
    
    st.write("💬 Ask me anything about movies and TV shows!")
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your AI assistant. How can I help you find movies or TV shows today?"}
        ]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Send to chatbot service
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = APIClient.chat_with_bot(prompt)
                if result['success']:
                    response = result['data'].get('response', 'I understand your question. This is a demo response.')
                else:
                    response = f"I understand you're asking about: '{prompt}'. This is a demo response. The actual AI chatbot service will provide intelligent recommendations!"
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

def main():
    """Main function"""
    # Initialize session state
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.current_page = 'dashboard'
    
    # Check if user is logged in
    if is_logged_in():
        # Navigation logic
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'dashboard'
        
        # Sidebar navigation
        with st.sidebar:
            st.markdown("### 🎬 Navigation")
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.current_page = 'dashboard'
            if st.button("🎬 Movies", use_container_width=True):
                st.session_state.current_page = 'movies'
            if st.button("📺 Series", use_container_width=True):
                st.session_state.current_page = 'series'
            if st.button("⭐ Personalize", use_container_width=True):
                st.session_state.current_page = 'personalize'
            if st.button("🤖 Chatbot", use_container_width=True):
                st.session_state.current_page = 'chatbot'
            
            st.divider()
            if st.button("🚪 Logout", use_container_width=True):
                logout()
                st.rerun()
        
        # Page routing
        if st.session_state.current_page == 'dashboard':
            show_dashboard()
        elif st.session_state.current_page == 'movies':
            show_movies()
        elif st.session_state.current_page == 'series':
            show_series()
        elif st.session_state.current_page == 'personalize':
            show_personalize()
        elif st.session_state.current_page == 'chatbot':
            show_chatbot()
    else:
        show_login_page()

if __name__ == "__main__":
    main()