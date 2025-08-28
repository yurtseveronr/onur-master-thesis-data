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
    
    .verification-container {
        background: rgba(72, 187, 120, 0.1);
        border: 2px solid rgba(72, 187, 120, 0.3);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .verification-code-input {
        font-family: monospace;
        font-size: 1.2rem;
        letter-spacing: 0.2rem;
        text-align: center;
    }
    
    .stForm {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        color: white !important;
        border-radius: 8px !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
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
    
    .success-message {
        background: rgba(72, 187, 120, 0.2);
        border: 1px solid rgba(72, 187, 120, 0.5);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: rgba(245, 101, 101, 0.2);
        border: 1px solid rgba(245, 101, 101, 0.5);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .info-message {
        background: rgba(66, 153, 225, 0.2);
        border: 1px solid rgba(66, 153, 225, 0.5);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .warning-message {
        background: rgba(237, 137, 54, 0.2);
        border: 1px solid rgba(237, 137, 54, 0.5);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
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
    def confirm_user(email: str, code: str) -> Dict[str, Any]:
        """Confirm user registration with code"""
        data = {
            'email': email,
            'code': code
        }
        return APIClient.make_request('POST', f"{API_URLS['auth']}/auth/confirm", data)

    @staticmethod
    def resend_code(email: str) -> Dict[str, Any]:
        """Resend confirmation code"""
        data = {
            'email': email
        }
        return APIClient.make_request('POST', f"{API_URLS['auth']}/auth/resend", data)

    @staticmethod
    def login_user(email: str, password: str) -> Dict[str, Any]:
        """User login"""
        data = {'email': email, 'password': password}
        return APIClient.make_request('POST', f"{API_URLS['auth']}/auth/login", data)

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
    """Login page with improved confirmation flow"""
    st.markdown('<div class="main-header"><h1>🎬 Streaming Platform</h1><p>Welcome to the World of Movies and TV Shows!</p></div>', unsafe_allow_html=True)
    
    # Check if we should show login tab after successful registration
    if st.session_state.get('show_login_tab', False):
        tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Sign Up"])
        st.session_state.show_login_tab = False
    else:
        tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Sign Up"])
    
    with tab1:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.subheader("Sign In to Your Account")
        
        with st.form("login_form"):
            username = st.text_input("Email Address", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_button = st.form_submit_button("Sign In", use_container_width=True)
            
            if login_button:
                if username and password:
                    with st.spinner("Signing in..."):
                        result = APIClient.login_user(username, password)
                    
                    if result['success']:
                        st.session_state.token = result['data']['token']
                        st.session_state.user_data = result['data']['user']
                        st.session_state.username = username
                        st.session_state.current_page = 'dashboard'
                        show_custom_message("success", "Successfully signed in!")
                        st.balloons()
                        st.rerun()
                    else:
                        error_code = result.get('error_code', '')
                        if error_code == 'UserNotConfirmedException':
                            show_custom_message("warning", "Please verify your email first. Check the Sign Up tab to verify.")
                            st.session_state.pending_verification_email = username
                        else:
                            show_custom_message("error", f"Sign in failed: {result['message']}")
                else:
                    show_custom_message("error", "Please fill in all fields!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        
        # Check current state
        current_state = st.session_state.get('registration_state', 'register')
        
        if current_state == 'register':
            show_registration_form()
        elif current_state == 'verify_email':
            show_verification_form()
        elif current_state == 'resend_verification':
            show_resend_verification()
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_registration_form():
    """Show registration form"""
    st.subheader("Create New Account")
    
    # Check if there's a pending verification from login attempt
    if st.session_state.get('pending_verification_email'):
        show_custom_message("info", f"You can verify your email address: {st.session_state.pending_verification_email}")
        if st.button("Verify This Email", use_container_width=True):
            st.session_state.registration_email = st.session_state.pending_verification_email
            st.session_state.registration_state = 'verify_email'
            del st.session_state.pending_verification_email
            st.rerun()
        st.divider()
    
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
                        show_custom_message("success", "Account created successfully!")
                        st.session_state.registration_email = email
                        st.session_state.registration_state = 'verify_email'
                        st.balloons()
                        st.rerun()
                    else:
                        error_code = result.get('error_code', '')
                        
                        if error_code == 'USER_UNCONFIRMED':
                            show_custom_message("warning", "This email is already registered but not verified.")
                            st.session_state.registration_email = email
                            st.session_state.registration_state = 'verify_email'
                            st.rerun()
                        elif error_code in ['USER_EXISTS_VERIFIED', 'UsernameExistsException']:
                            show_custom_message("error", "This email is already registered. Please sign in instead.")
                            st.session_state.show_login_tab = True
                            st.rerun()
                        else:
                            error_message = result.get('error', result.get('message', 'Unknown error'))
                            show_custom_message("error", f"Registration failed: {error_message}")
            else:
                show_custom_message("error", "Please fill in all fields!")

def show_verification_form():
    """Show email verification form"""
    st.subheader("Verify Your Email")
    
    email = st.session_state.get('registration_email', 'your email')
    
    st.markdown('<div class="verification-container">', unsafe_allow_html=True)
    show_custom_message("info", f"📧 Verification code sent to: {email}")
    st.markdown("**Check your email inbox** (including spam folder) for a message from:")
    st.markdown("- **From:** no-reply@verificationemail.com")
    st.markdown("- **Subject:** Your verification code")
    st.markdown("- **Content:** 6-digit verification code")
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.form("verification_form"):
        verification_code = st.text_input(
            "Enter 6-Digit Verification Code", 
            placeholder="123456",
            max_chars=6,
            help="Enter the 6-digit code from your email"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            verify_button = st.form_submit_button("Verify Email", use_container_width=True)
        with col2:
            resend_button = st.form_submit_button("Resend Code", use_container_width=True)
        
        if verify_button:
            if verification_code and len(verification_code) == 6:
                with st.spinner("Verifying your email..."):
                    result = APIClient.confirm_user(email, verification_code)
                
                if result['success']:
                    show_custom_message("success", "Email verified successfully! You can now sign in.")
                    # Clear verification state
                    st.session_state.registration_state = 'register'
                    if 'registration_email' in st.session_state:
                        del st.session_state.registration_email
                    st.session_state.show_login_tab = True
                    st.balloons()
                    st.rerun()
                else:
                    error_code = result.get('error_code', '')
                    if error_code == 'CodeMismatchException':
                        show_custom_message("error", "Invalid verification code. Please check your email and try again.")
                    elif error_code == 'ExpiredCodeException':
                        show_custom_message("warning", "Verification code has expired. Please request a new one.")
                        st.session_state.registration_state = 'resend_verification'
                        st.rerun()
                    else:
                        error_message = result.get('error', result.get('message', 'Unknown error'))
                        show_custom_message("error", f"Verification failed: {error_message}")
            else:
                show_custom_message("error", "Please enter a valid 6-digit verification code!")
        
        elif resend_button:
            st.session_state.registration_state = 'resend_verification'
            st.rerun()
    
    # Back to registration button
    if st.button("← Back to Registration"):
        st.session_state.registration_state = 'register'
        if 'registration_email' in st.session_state:
            del st.session_state.registration_email
        st.rerun()

def show_resend_verification():
    """Show resend verification form"""
    st.subheader("Resend Verification Code")
    
    email = st.session_state.get('registration_email', '')
    
    st.markdown("**Didn't receive the verification code?**")
    st.markdown("- Check your spam/junk folder")
    st.markdown("- Make sure the email address is correct")
    st.markdown("- Wait a few minutes for the email to arrive")
    
    with st.form("resend_form"):
        email_input = st.text_input("Email Address", value=email, placeholder="Enter your email")
        
        col1, col2 = st.columns(2)
        with col1:
            resend_button = st.form_submit_button("Resend Code", use_container_width=True)
        with col2:
            back_button = st.form_submit_button("Back to Verification", use_container_width=True)
        
        if resend_button:
            if email_input:
                with st.spinner("Sending new verification code..."):
                    result = APIClient.resend_code(email_input)
                
                if result['success']:
                    show_custom_message("success", "New verification code sent! Please check your email.")
                    st.session_state.registration_email = email_input
                    st.session_state.registration_state = 'verify_email'
                    st.rerun()
                else:
                    show_custom_message("error", f"Failed to resend code: {result['message']}")
            else:
                show_custom_message("error", "Please enter your email address!")
        
        elif back_button:
            st.session_state.registration_state = 'verify_email'
            st.rerun()

def show_dashboard():
    """Dashboard page"""
    st.markdown('<div class="main-header"><h1>🎬 Welcome to Your Dashboard</h1></div>', unsafe_allow_html=True)
    
    user = st.session_state.get('user_data', {})
    st.write(f"Welcome back, {user.get('username', 'User')}!")
    
    # Sample dashboard content
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Movies Watched", "42", "5")
    with col2:
        st.metric("TV Shows", "18", "2")
    with col3:
        st.metric("Watch Time", "156h", "12h")
    
    st.subheader("Continue Watching")
    st.info("🎬 The Matrix Reloaded - 45 minutes left")
    st.info("📺 Breaking Bad S3E8 - New episode")
    
    st.subheader("Recommended for You")
    st.success("🎬 Inception - Based on your sci-fi preferences")
    st.success("📺 Westworld - You might enjoy this")

def logout():
    """Logout user"""
    # Clear all session state
    keys_to_clear = ['token', 'user_data', 'username', 'current_page', 'registration_state', 'registration_email', 'pending_verification_email']
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
        st.session_state.registration_state = 'register'
    
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
        # Check registration state
        registration_state = st.session_state.get('registration_state', 'register')
        
        if registration_state == 'verify_email':
            show_verification_form()
        elif registration_state == 'resend_verification':
            show_resend_verification()
        else:
            show_login_page()

if __name__ == "__main__":
    main()