import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from utils.auth import get_user_data, save_user_sales_data, load_user_sales_data, delete_user_data
from utils.analytics import analyze_sales_trends, generate_business_tips, generate_advanced_recommendations, create_demo_data
from utils.database import db_client

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("🔐 Please log in to access the dashboard")
    st.switch_page("pages/1_🚀_Login.py")

username = st.session_state.username
user_data = get_user_data(username)

# Set demo data for demo user
if username == "demo_bakery" and load_user_sales_data(username) is None:
    demo_df = create_demo_data()
    save_user_sales_data(username, demo_df)

st.set_page_config(
    page_title=f"BizBoost - {user_data.get('business_name', 'Dashboard')}",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .welcome-header {
        background: linear-gradient(45deg, #FF6B35, #00A8E8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 5px solid #FF6B35;
    }
    .insight-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem;
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
</style>
""", unsafe_allow_html=True)

def main_dashboard():
    # Database status
    if db_client.is_connected():
        st.markdown('<div class="database-status database-connected">✅ Your data is securely stored in the cloud</div>', unsafe_allow_html=True)
    
    # Welcome header
    business_name = user_data.get('business_name', 'Your Business')
    st.markdown(f'<div class="welcome-header">👋 Welcome back, {business_name}!</div>', unsafe_allow_html=True)
    
    # Navigation
    st.sidebar.title("🚀 Navigation")
    page = st.sidebar.radio("Go to", [
        "📊 Business Dashboard", 
        "🤖 AI Recommendations", 
        "⚙️ Account Settings"
    ])
    
    # Quick stats in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("📈 Quick Stats")
    
    df = load_user_sales_data(username)
    if df is not None and not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df['revenue'] = df['quantity'] * df['price']
        
        # Recent performance
        recent_7_days = df[df['date'] > (df['date'].max() - timedelta(days=7))]
        if not recent_7_days.empty:
            weekly_revenue = recent_7_days['revenue'].sum()
            st.sidebar.metric("7-Day Revenue", f"₦{weekly_revenue:,.0f}")
            
            # Growth indicator
            previous_7_days = df[
                (df['date'] > (df['date'].max() - timedelta(days=14))) & 
                (df['date'] <= (df['date'].max() - timedelta(days=7)))
            ]
            if not previous_7_days.empty:
                previous_revenue = previous_7_days['revenue'].sum()
                growth = ((weekly_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
                st.sidebar.metric("Weekly Growth", f"{growth:+.1f}%")
    
    # User info
    st.sidebar.markdown("---")
    st.sidebar.subheader("👤 Account Info")
    st.sidebar.write(f"**Business:** {business_name}")
    st.sidebar.write(f"**Type:** {user_data.get('business_type', 'Not specified')}")
    st.sidebar.write(f"**Data Storage:** {'☁️ Cloud' if db_client.is_connected() else '💾 Local'}")
    
    if st.sidebar.button("🚪 Logout", type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Page routing
    if "AI Recommendations" in page:
        st.switch_page("pages/3_🚀_AI_Recommendations.py")
    elif "Account Settings" in page:
        show_account_settings()
    else:
        show_dashboard()

def show_dashboard():
    st.header("📊 Business Intelligence Dashboard")
    
    # Data Upload Section
    st.subheader("📤 Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Sales Data (CSV/Excel)", 
            type=['csv', 'xlsx'],
            help="Upload file with columns: date, product, quantity, price"
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                if all(col in df.columns for col in ['date', 'product', 'quantity', 'price']):
                    save_user_sales_data(username, df)
                    st.success("✅ Data uploaded to cloud successfully!")
                    st.rerun()
                else:
                    st.error("❌ Missing required columns: date, product, quantity, price")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col2:
        st.info("""
        **📊 Data Format:**
        - date: YYYY-MM-DD
        - product: Product name
        - quantity: Number sold
        - price: Price per unit
        
        **Example:**
        ```
        date,product,quantity,price
        2024-01-01,Cake,2,2500
        2024-01-01,Drink,5,500
        ```
        """)
        
        if st.button("🔄 Load Demo Data", help="Load sample data for testing"):
            demo_df = create_demo_data()
            save_user_sales_data(username, demo_df)
            st.success("✅ Demo data loaded to cloud!")
            st.rerun()
    
    # Load and display data
    df = load_user_sales_data(username)
    
    if df is None or df.empty:
        show_empty_state()
        return
    
    # Data preparation
    df['date'] = pd.to_datetime(df['date'])
    df['revenue'] = df['quantity'] * df['price']
    df['day_of_week'] = df['date'].dt.day_name()
    df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday'])
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("📅 Start Date", 
                                 value=df['date'].min().date(),
                                 min_value=df['date'].min().date(),
                                 max_value=df['date'].max().date())
    with col2:
        end_date = st.date_input("📅 End Date", 
                               value=df['date'].max().date(),
                               min_value=df['date'].min().date(),
                               max_value=df['date'].max().date())
    
    # Filter data
    mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
    filtered_df = df[mask]
    
    if filtered_df.empty:
        st.error("❌ No data available for selected date range")
        return
    
    # Key Metrics
    st.subheader("💰 Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = filtered_df['revenue'].sum()
        st.metric("Total Revenue", f"₦{total_revenue:,.0f}")
    
    with col2:
        total_orders = len(filtered_df)
        st.metric("Total Orders", f"{total_orders:,}")
    
    with col3:
        avg_order_value = filtered_df['revenue'].mean()
        st.metric("Avg Order Value", f"₦{avg_order_value:,.0f}")
    
    with col4:
        best_product = filtered_df.groupby('product')['revenue'].sum().idxmax()
        st.metric("Top Product", best_product)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by product
        product_revenue = filtered_df.groupby('product')['revenue'].sum().sort_values(ascending=False)
        fig1 = px.bar(product_revenue, 
                     title="📦 Revenue by Product",
                     labels={'value': 'Revenue (₦)', 'product': 'Product'},
                     color=product_revenue.values,
                     color_continuous_scale='viridis')
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Revenue trend
        daily_revenue = filtered_df.groupby(filtered_df['date'].dt.date)['revenue'].sum()
        fig2 = px.area(daily_revenue, 
                      title="📈 Daily Revenue Trend",
                      labels={'value': 'Revenue (₦)', 'date': 'Date'})
        st.plotly_chart(fig2, use_container_width=True)
    
    # Advanced Analytics
    st.subheader("🤖 AI Business Insights")
    
    try:
        with st.spinner("🔄 Analyzing your business data..."):
            insights = analyze_sales_trends(filtered_df)
            tips = generate_business_tips(insights)
        
        # Display insights in columns
        cols = st.columns(2)
        
        with cols[0]:
            st.markdown("#### 🔍 Patterns Discovered")
            for insight in insights[:3]:
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #FF6B35;">
                    <strong>{insight['title']}</strong>
                    <p style="margin: 0.5rem 0 0 0; color: #666;">{insight['description']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown("#### 💡 Recommended Actions")
            for i, tip in enumerate(tips[:3], 1):
                st.markdown(f"""
                <div style="background: #e8f5e8; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #28a745;">
                    <strong>Tip #{i}: {tip['action']}</strong>
                    <p style="margin: 0.5rem 0 0 0; color: #666;">{tip['reason']}</p>
                </div>
                """, unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"❌ Error generating insights: {str(e)}")
    
    # Navigation to AI Recommendations
    st.markdown("---")
    st.subheader("🚀 Ready for Advanced AI Insights?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("Get personalized AI recommendations tailored to your business growth.")
    
    with col2:
        if st.button("🤖 Get AI Recommendations", use_container_width=True):
            st.switch_page("pages/3_🚀_AI_Recommendations.py")

def show_empty_state():
    """Show empty state when no data is available"""
    st.warning("""
    ## 📊 No Data Available
    
    To unlock BizBoost's full potential, upload your sales data to get AI-powered insights.
    
    **Your data will be securely stored in the cloud.**
    """)
    
    st.info("💡 **Don't have data ready?** Try our demo data to explore features instantly!")

def show_account_settings():
    st.header("⚙️ Account Settings")
    
    user_data = get_user_data(username)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏢 Business Information")
        st.write(f"**Username:** {username}")
        st.write(f"**Business Name:** {user_data.get('business_name', 'Not set')}")
        st.write(f"**Business Type:** {user_data.get('business_type', 'Not set')}")
        st.write(f"**Member Since:** {user_data.get('created_at', 'Unknown')[:10]}")
        st.write(f"**Data Storage:** {'☁️ Cloud' if db_client.is_connected() else '💾 Local'}")
    
    with col2:
        st.subheader("🛠️ Data Management")
        
        if st.button("🗑️ Clear All My Data", type="secondary"):
            delete_user_data(username)
            st.success("✅ All your data has been cleared from the cloud!")
            st.rerun()
        
        # Export data
        df = load_user_sales_data(username)
        if df is not None:
            st.download_button(
                label="💾 Export My Data",
                data=df.to_csv(index=False),
                file_name=f"bizboost_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.button("💾 Export My Data", disabled=True, use_container_width=True)

# Run the dashboard
main_dashboard()