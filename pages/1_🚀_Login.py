import streamlit as st
from utils.auth import register_user, authenticate_user
from utils.database import db_client

st.set_page_config(
    page_title="BizBoost - Login",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3rem;
        font-weight: bold;
    }
    .header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .database-status {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
    .database-connected {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .database-disconnected {
        background: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

def show_login():
    # Database status
    if db_client.is_connected():
        st.markdown('<div class="database-status database-connected">✅ Connected to Cloud Database</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="database-status database-disconnected">⚠️ Using Secure Local Storage</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="header">
        <h1 style='color: #FF6B35;'>🚀 BizBoost</h1>
        <p style='color: #666;'>SME Growth Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Welcome Back!")
        
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            login_button = st.form_submit_button("🚀 Login to BizBoost")
            
            if login_button:
                if username and password:
                    with st.spinner("Authenticating..."):
                        success, message = authenticate_user(username, password)
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.username = username
                            st.success("✅ Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                else:
                    st.error("⚠️ Please fill in all fields")
    
    with tab2:
        st.subheader("Start Your Growth Journey")
        
        with st.form("register_form"):
            new_username = st.text_input("👤 Choose Username", help="Must be unique")
            new_password = st.text_input("🔒 Choose Password", type="password", help="At least 6 characters")
            confirm_password = st.text_input("✅ Confirm Password", type="password")
            business_name = st.text_input("🏢 Business Name", placeholder="e.g., Ngozi's Bakery")
            business_type = st.selectbox("📊 Business Type", [
                "Restaurant/Bakery", 
                "Retail Store", 
                "Services", 
                "Fashion/Boutique",
                "Supermarket",
                "Hotel/Lodging",
                "Other"
            ])
            register_button = st.form_submit_button("🎯 Create My Account")
            
            if register_button:
                if not all([new_username, new_password, confirm_password, business_name]):
                    st.error("⚠️ Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("❌ Passwords don't match")
                elif len(new_password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    with st.spinner("Creating your account..."):
                        success, message = register_user(new_username, new_password, business_name, business_type)
                        if success:
                            st.markdown("""
                            <div class="success-message">
                                <h4>🎉 Account Created Successfully!</h4>
                                <p>Your data is securely stored in the cloud. You can now login and start growing your business.</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error(f"❌ {message}")

    # Demo Access
    st.markdown("---")
    st.markdown("### 🎪 Quick Demo Access")
    st.info("""
    **Want to explore without registering?**
    - Use demo credentials: 
    - Username: `demo_bakery`
    - Password: `demo123`
    
    *All demo data is stored securely in the cloud*
    """)

# Check authentication
if 'authenticated' in st.session_state and st.session_state.authenticated:
    st.switch_page("pages/2_📊_Dashboard.py")
else:
    show_login()