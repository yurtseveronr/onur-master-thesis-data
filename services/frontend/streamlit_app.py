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
    
    .success-message {
        background: rgba(76, 175, 80, 0.1);
        border: 1px solid rgba(76, 175, 80, 0.3);
        color: #4CAF50;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: rgba(244, 67, 54, 0.1);
        border: 1px solid rgba(244, 67, 54, 0.3);
        color: #F44336;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .warning-message {
        background: rgba(255, 152, 0, 0.1);
        border: 1px solid rgba(255, 152, 0, 0.3);
        color: #FF9800;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .info-message {
        background: rgba(33, 150, 243, 0.1);
        border: 1px solid rgba(33, 150, 243, 0.3);
        color: #2196F3;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# API Base URLs
API_URLS = {
    'auth': 'http://authentication.services.svc.cluster.local:5000',
    'user': 'http://user.services.svc.cluster.local:8080',
    'movies': 'http://movies.services.svc.cluster.local:8081',
    'series': 'http://series.services.svc.cluster.local:8082',
    'search': 'http://search.services.svc.cluster.local:8084',
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
            
            if 'token' in st.session_state:
                headers['Authorization'] = f'Bearer {st.session_state.token}'
            
            response = None
            if method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                try:
                    return {'success': True, 'data': response.json()}
                except:
                    return {'success': True, 'data': {'message': 'Success'}}
            else:
                try:
                    error_data = response.json()
                    return {
                        'success': False, 
                        'message': error_data.get('error', f'HTTP {response.status_code}'),
                        'error_code': error_data.get('error_code', 'UNKNOWN')
                    }
                except:
                    return {'success': False, 'message': f'HTTP {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            return {'success': False, 'message': f'Connection error: {str(e)}'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def register_user(email: str, password: str) -> Dict[str, Any]:
        """User registration"""
        data = {'email': email, 'password': password}
        return APIClient.make_request('POST', f"{API_URLS['auth']}/auth/signup", data)

    @staticmethod
    def login_user(email: str, password: str) -> Dict[str, Any]:
        """User login"""
        data = {'email': email, 'password': password}
        return APIClient.make_request('POST', f"{API_URLS['auth']}/auth/login", data)

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
    def get_favorite_movies(email: str) -> Dict[str, Any]:
        """Get user's favorite movies"""
        return APIClient.make_request('GET', f"{API_URLS['user']}/api/favorites/movies/{email}")

    @staticmethod
    def get_favorite_series(email: str) -> Dict[str, Any]:
        """Get user's favorite series"""
        return APIClient.make_request('GET', f"{API_URLS['user']}/api/favorites/series/{email}")

    @staticmethod
    def add_favorite_movie(email: str, title: str) -> Dict[str, Any]:
        """Add movie to favorites"""
        return APIClient.make_request('POST', f"{API_URLS['user']}/api/favorites/movies/{email}/{title}")

    @staticmethod
    def add_favorite_series(email: str, title: str) -> Dict[str, Any]:
        """Add series to favorites"""
        return APIClient.make_request('POST', f"{API_URLS['user']}/api/favorites/series/{email}/{title}")

    @staticmethod
    def chat_with_bot(message: str) -> Dict[str, Any]:
        """Chat with chatbot"""
        data = {'message': message}
        return APIClient.make_request('POST', f"{API_URLS['chatbot']}/chat", data)

def show_custom_message(message_type: str, message: str):
    """Show custom styled messages"""
    if message_type == "success":
        st.markdown(f'<div class="success-message">✅ {message}</div>', unsafe_allow_html=True)
    elif message_type == "error":
        st.markdown(f'<div class="error-message">❌ {message}</div>', unsafe_allow_html=True)
    elif message_type == "info":
        st.markdown(f'<div class="info-message">ℹ️ {message}</div>', unsafe_allow_html=True)
    elif message_type == "warning":
        st.markdown(f'<div class="warning-message">⚠️ {message}</div>', unsafe_allow_html=True)

def show_login_page():
    """Login page with simple auth flow"""
    st.markdown('<div class="main-header"><h1>🎬 Streaming Platform</h1><p>Welcome to the World of Movies and TV Shows!</p></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Sign Up"])
    
    with tab1:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.subheader("Sign In to Your Account")
        
        with st.form("login_form"):
            email = st.text_input("Email Address", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_button = st.form_submit_button("Sign In", use_container_width=True)
            
            if login_button:
                if email and password:
                    with st.spinner("Signing in..."):
                        result = APIClient.login_user(email, password)
                    
                    if result['success']:
                        st.session_state.token = result['data']['token']
                        st.session_state.user_data = result['data']['user']
                        st.session_state.username = email
                        st.session_state.current_page = 'dashboard'
                        show_custom_message("success", "Successfully signed in!")
                        st.balloons()
                        st.rerun()
                    else:
                        error_message = result.get('message', 'Unknown error')
                        show_custom_message("error", f"Sign in failed: {error_message}")
                else:
                    show_custom_message("error", "Please fill in all fields!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.subheader("Create New Account")
        
        with st.form("register_form"):
            email = st.text_input("Email Address", placeholder="Enter your email address")
            password = st.text_input("Password", type="password", placeholder="Minimum 8 characters")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            register_button = st.form_submit_button("Create Account", use_container_width=True)
            
            if register_button:
                if email and password and confirm_password:
                    if password != confirm_password:
                        show_custom_message("error", "Passwords don't match!")
                    elif len(password) < 8:
                        show_custom_message("error", "Password must be at least 8 characters!")
                    else:
                        with st.spinner("Creating your account..."):
                            result = APIClient.register_user(email, password)
                        
                        if result['success']:
                            show_custom_message("success", "Account created successfully! You can now sign in.")
                            st.balloons()
                            # Switch to login tab
                            st.session_state.show_login_tab = True
                            st.rerun()
                        else:
                            error_code = result.get('error_code', '')
                            if error_code == 'USER_EXISTS_VERIFIED':
                                show_custom_message("error", "This email is already registered. Please sign in instead.")
                                st.session_state.show_login_tab = True
                                st.rerun()
                            else:
                                error_message = result.get('message', 'Unknown error')
                                show_custom_message("error", f"Registration failed: {error_message}")
                else:
                    show_custom_message("error", "Please fill in all fields!")
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_dashboard():
    """Dashboard page"""
    st.markdown('<div class="main-header"><h1>🎬 Welcome to Your Dashboard</h1></div>', unsafe_allow_html=True)
    
    user = st.session_state.get('user_data', {})
    username = user.get('username', 'User')
    st.write(f"Welcome back, {username}!")
    
    # Get user favorites
    email = st.session_state.get('username', '')
    if email:
        # Get favorite movies count
        movies_result = APIClient.get_favorite_movies(email)
        movies_count = len(movies_result.get('data', [])) if movies_result.get('success') else 0
        
        # Get favorite series count
        series_result = APIClient.get_favorite_series(email)
        series_count = len(series_result.get('data', [])) if series_result.get('success') else 0
        
        # Get recommendations
        recommendations_result = APIClient.get_recommendations()
        recommendations = recommendations_result.get('data', []) if recommendations_result.get('success') else []
    else:
        movies_count = 0
        series_count = 0
        recommendations = []
    
    # Dashboard metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Movies Watched", movies_count)
    with col2:
        st.metric("TV Shows", series_count)
    
    # Recommended for You
    st.subheader("Recommended for You")
    if recommendations:
        for rec in recommendations:
            st.success(f"🎬 {rec.get('title', 'Unknown')} - {rec.get('reason', 'Recommended for you')}")
    else:
        st.info("No personalized recommendations found")
    
    # Navigation tabs
    st.subheader("Navigation")
    tab1, tab2, tab3, tab4 = st.tabs(["🎬 Movies", "📺 Series", "🔍 Search", "🤖 Chatbot"])
    
    with tab1:
        show_movies_page(email)
    
    with tab2:
        show_series_page(email)
    
    with tab3:
        show_search_page(email)
    
    with tab4:
        show_chatbot_page()

def show_movies_page(email: str):
    """Movies page showing user's favorite movies"""
    st.subheader("🎬 Your Favorite Movies")
    
    if not email:
        st.warning("Please login to view your favorite movies")
        return
    
    result = APIClient.get_favorite_movies(email)
    
    if result.get('success'):
        movies = result.get('data', [])
        if movies:
            # Display movies in a grid
            cols = st.columns(3)
            for i, movie in enumerate(movies):
                with cols[i % 3]:
                    st.write(f"**{movie.get('Title', 'Unknown')}**")
                    # Try to get poster from search service
                    search_result = APIClient.search_movies(movie.get('Title', ''))
                    if search_result.get('success') and search_result.get('data', {}).get('data', {}).get('Poster'):
                        poster_url = search_result['data']['data']['Poster']
                        if poster_url != "N/A":
                            st.image(poster_url, width=150, caption=movie.get('Title', ''))
                    st.write(f"IMDB ID: {movie.get('imdbID', 'Unknown')}")
                    st.divider()
        else:
            st.info("No favorite movies found. Add some movies to your favorites!")
    else:
        st.error(f"Error loading movies: {result.get('message', 'Unknown error')}")

def show_series_page(email: str):
    """Series page showing user's favorite series"""
    st.subheader("📺 Your Favorite Series")
    
    if not email:
        st.warning("Please login to view your favorite series")
        return
    
    result = APIClient.get_favorite_series(email)
    
    if result.get('success'):
        series = result.get('data', [])
        if series:
            # Display series in a grid
            cols = st.columns(3)
            for i, show in enumerate(series):
                with cols[i % 3]:
                    st.write(f"**{show.get('Title', 'Unknown')}**")
                    # Try to get poster from search service
                    search_result = APIClient.search_series(show.get('Title', ''))
                    if search_result.get('success') and search_result.get('data', {}).get('data', {}).get('Poster'):
                        poster_url = search_result['data']['data']['Poster']
                        if poster_url != "N/A":
                            st.image(poster_url, width=150, caption=show.get('Title', ''))
                    st.write(f"IMDB ID: {show.get('imdbID', 'Unknown')}")
                    st.divider()
        else:
            st.info("No favorite series found. Add some series to your favorites!")
    else:
        st.error(f"Error loading series: {result.get('message', 'Unknown error')}")

def show_search_page(email: str):
    """Search page for movies and series"""
    st.subheader("🔍 Search Movies & Series")
    
    search_type = st.selectbox("Search for:", ["movie", "series"])
    search_query = st.text_input("Enter title to search:", placeholder="e.g., Matrix, Breaking Bad")
    
    if st.button("Search"):
        if search_query:
            with st.spinner("Searching..."):
                if search_type == "movie":
                    result = APIClient.search_movies(search_query)
                else:
                    result = APIClient.search_series(search_query)
            
            if result.get('success'):
                data = result.get('data', {}).get('data', {})
                if data and data.get('Response') == 'True':
                    # Display search result
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        poster_url = data.get('Poster', '')
                        if poster_url and poster_url != "N/A":
                            st.image(poster_url, width=200, caption=data.get('Title', ''))
                    
                    with col2:
                        st.write(f"**Title:** {data.get('Title', 'Unknown')}")
                        st.write(f"**Year:** {data.get('Year', 'Unknown')}")
                        st.write(f"**Genre:** {data.get('Genre', 'Unknown')}")
                        st.write(f"**Director:** {data.get('Director', 'Unknown')}")
                        st.write(f"**Plot:** {data.get('Plot', 'Unknown')}")
                        st.write(f"**Rating:** {data.get('imdbRating', 'Unknown')}/10")
                        
                        # Add to favorites button
                        if email:
                            if st.button(f"❤️ Add to Favorites"):
                                if search_type == "movie":
                                    add_result = APIClient.add_favorite_movie(email, data.get('Title', ''))
                                else:
                                    add_result = APIClient.add_favorite_series(email, data.get('Title', ''))
                                
                                if add_result.get('success'):
                                    st.success("Added to favorites!")
                                    st.rerun()
                                else:
                                    st.error(f"Error: {add_result.get('message', 'Unknown error')}")
                        else:
                            st.warning("Login to add to favorites")
                else:
                    st.warning("Not Found")
            else:
                st.error(f"Search error: {result.get('message', 'Unknown error')}")

def show_chatbot_page():
    """Chatbot page"""
    st.subheader("🤖 AI Chatbot")
    st.write("Chat with our AI assistant about movies and series!")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about movies or series..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = APIClient.chat_with_bot(prompt)
                
                if result.get('success'):
                    response = result.get('data', {}).get('response', 'Sorry, I could not process your request.')
                else:
                    response = f"Error: {result.get('message', 'Unknown error')}"
                
                st.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})

def logout():
    """Logout user"""
    # Clear all session state
    keys_to_clear = ['token', 'user_data', 'username', 'current_page']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def is_logged_in() -> bool:
    """Check if user is logged in"""
    return 'token' in st.session_state and 'user_data' in st.session_state

def main():
    """Main function"""
    # Initialize session state
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.current_page = 'login'
    
    # Check if user is logged in
    if is_logged_in():
        # Sidebar navigation
        with st.sidebar:
            st.markdown("### 🎬 Navigation")
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.current_page = 'dashboard'
            
            st.divider()
            if st.button("🚪 Logout", use_container_width=True):
                logout()
                st.rerun()
        
        # Show dashboard
        show_dashboard()
    else:
        show_login_page()

if __name__ == "__main__":
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.sidebar.markdown("**Version:** 2.0 - Auto-verified flow")
    main()