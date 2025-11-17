import streamlit as st
import pandas as pd
from datetime import datetime
from utils.auth import get_user_data, load_user_sales_data, save_user_sales_data
from utils.analytics import generate_advanced_recommendations, create_demo_data
from utils.database import db_client

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("🔐 Please log in to access recommendations")
    st.switch_page("pages/1_🚀_Login.py")

username = st.session_state.username
user_data = get_user_data(username)

st.set_page_config(
    page_title="BizBoost - AI Recommendations",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS for recommendations
st.markdown("""
<style>
    .recommendation-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border-left: 5px solid;
        transition: transform 0.2s;
    }
    .recommendation-card:hover {
        transform: translateY(-2px);
    }
    .immediate-action {
        border-left-color: #dc3545;
        background: linear-gradient(135deg, #fff5f5, #ffffff);
    }
    .strategic-action {
        border-left-color: #fd7e14;
        background: linear-gradient(135deg, #fff4e6, #ffffff);
    }
    .predictive-insight {
        border-left-color: #20c997;
        background: linear-gradient(135deg, #e6fcf5, #ffffff);
    }
    .competitive-analysis {
        border-left-color: #0d6efd;
        background: linear-gradient(135deg, #e7f1ff, #ffffff);
    }
    .risk-alert {
        border-left-color: #6f42c1;
        background: linear-gradient(135deg, #f8f9fa, #ffffff);
    }
    .impact-high { color: #dc3545; font-weight: bold; }
    .impact-medium { color: #fd7e14; font-weight: bold; }
    .impact-low { color: #20c997; font-weight: bold; }
    .severity-high { color: #dc3545; font-weight: bold; }
    .severity-medium { color: #fd7e14; font-weight: bold; }
    .severity-low { color: #20c997; font-weight: bold; }
    .impact-summary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 2rem;
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
</style>
""", unsafe_allow_html=True)

def main():
    # Database status
    if db_client.is_connected():
        st.markdown('<div class="database-status database-connected">✅ Your insights are powered by cloud AI analytics</div>', unsafe_allow_html=True)
    
    st.title("🚀 AI-Powered Business Recommendations")
    st.markdown("### Your personalized growth strategy powered by advanced analytics")
    
    # Load user data
    df = load_user_sales_data(username)
    
    if df is None or df.empty:
        st.warning("""
        ## 📊 Data Required for AI Insights
        
        To generate personalized recommendations, please upload your sales data first.
        
        **What you'll get:**
        - 🤖 Immediate actionable insights
        - 📈 Strategic growth initiatives  
        - 🔮 Predictive business forecasts
        - 🏆 Competitive market analysis
        - ⚠️ Risk detection & mitigation
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Upload Data Now", use_container_width=True):
                st.switch_page("pages/2_📊_Dashboard.py")
        with col2:
            if st.button("🎯 Try Demo Data", use_container_width=True):
                demo_df = create_demo_data()
                save_user_sales_data(username, demo_df)
                st.success("✅ Demo data loaded to cloud! Generating insights...")
                st.rerun()
        return
    
    # Generate recommendations
    with st.spinner("🤖 AI is analyzing your business data... This may take a few moments."):
        try:
            results = generate_advanced_recommendations(df)
            recommendations = results['recommendations']
            business_impact = results['business_impact']
        except Exception as e:
            st.error(f"❌ Error generating recommendations: {str(e)}")
            return
    
    # Business Impact Summary
    st.markdown("---")
    st.subheader("💰 Expected Business Impact")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Revenue Increase", 
            f"₦{business_impact['revenue_increase']:,.0f}+",
            "15-30% potential"
        )
    
    with col2:
        st.metric(
            "Cost Reduction", 
            f"₦{business_impact['cost_reduction']:,.0f}+",
            "10-20% potential"
        )
    
    with col3:
        st.metric(
            "Efficiency Gain", 
            f"{business_impact['efficiency_gains']}%+",
            "Time & operations"
        )
    
    with col4:
        st.metric(
            "Risk Mitigation", 
            "High",
            "Financial stability"
        )
    
    # Executive Summary
    st.markdown("---")
    st.markdown("## 🎯 Executive Summary")
    
    st.markdown(f"""
    <div class="impact-summary">
        <h3>🚀 Your Growth Opportunity</h3>
        <p>Based on analysis of {len(df)} transactions, BizBoost has identified <strong>₦{business_impact['revenue_increase']:,.0f}+</strong> 
        in additional revenue potential through AI-optimized strategies.</p>
        <p><strong>Key Focus Areas:</strong> {len(recommendations['immediate_actions'])} immediate actions, 
        {len(recommendations['strategic_actions'])} strategic initiatives, and {len(recommendations['risk_alerts'])} risk mitigations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Immediate Actions
    st.markdown("---")
    st.subheader("🎯 Immediate Actions (Implement Now)")
    
    if recommendations['immediate_actions']:
        for action in recommendations['immediate_actions']:
            impact_class = f"impact-{action['impact']}"
            st.markdown(f"""
            <div class="recommendation-card immediate-action">
                <h4>⚡ {action['title']}</h4>
                <p>{action['description']}</p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
                    <span class="{impact_class}">🎯 Impact: {action['impact'].upper()}</span>
                    <strong>💡 {action['expected_benefit']}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ No immediate actions recommended based on current data patterns")
    
    # Strategic Actions
    st.subheader("📈 Strategic Growth Initiatives")
    
    if recommendations['strategic_actions']:
        for action in recommendations['strategic_actions']:
            impact_class = f"impact-{action['impact']}"
            st.markdown(f"""
            <div class="recommendation-card strategic-action">
                <h4>🎯 {action['title']}</h4>
                <p>{action['description']}</p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
                    <span class="{impact_class}">📊 Impact: {action['impact'].upper()}</span>
                    <strong>🎯 {action.get('expected_benefit', 'Long-term growth')}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ No strategic actions recommended based on current data")
    
    # Predictive Insights
    st.subheader("🔮 Predictive Insights & Forecasts")
    
    if recommendations['predictive_insights']:
        for insight in recommendations['predictive_insights']:
            st.markdown(f"""
            <div class="recommendation-card predictive-insight">
                <h4>🔍 {insight['title']}</h4>
                <p>{insight['description']}</p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
                    <span class="impact-{insight['impact']}">📈 Impact: {insight['impact'].upper()}</span>
                    <strong>📊 {insight.get('next_30_days', insight.get('projection', 'Future outlook'))}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ No predictive insights available with current data depth")
    
    # Competitive Analysis
    st.subheader("🏆 Market & Competitive Positioning")
    
    if recommendations['competitive_analysis']:
        for analysis in recommendations['competitive_analysis']:
            st.markdown(f"""
            <div class="recommendation-card competitive-analysis">
                <h4>🎯 {analysis['title']}</h4>
                <p>{analysis['description']}</p>
                <p><strong>💡 Recommendation:</strong> {analysis['recommendation']}</p>
                <span class="impact-{analysis['impact']}">🏆 Strategic Impact: {analysis['impact'].upper()}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ No competitive analysis available with current data")
    
    # Risk Alerts
    st.subheader("⚠️ Risk Alerts & Mitigation")
    
    if recommendations['risk_alerts']:
        for risk in recommendations['risk_alerts']:
            severity_class = f"severity-{risk['severity']}"
            st.markdown(f"""
            <div class="recommendation-card risk-alert">
                <h4>🚨 {risk['title']}</h4>
                <p>{risk['description']}</p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
                    <span class="{severity_class}">⚠️ Severity: {risk['severity'].upper()}</span>
                    <strong>🛡️ {risk['mitigation']}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No critical risks identified - your business is well-positioned!")
    
    # Implementation Roadmap
    st.markdown("---")
    st.subheader("🎪 Implementation Roadmap")
    
    tab1, tab2, tab3 = st.tabs(["🚀 Week 1", "📈 Month 1", "🏆 Quarter 1"])
    
    with tab1:
        st.markdown("""
        **Immediate Actions (Days 1-7):**
        - Implement pricing optimizations from AI recommendations
        - Launch quick promotional campaigns for underperforming products
        - Address inventory issues identified by risk analysis
        - Set up basic customer tracking systems
        - Test one cross-selling bundle
        """)
        
        if recommendations['immediate_actions']:
            st.info("**This Week's Focus:** " + recommendations['immediate_actions'][0]['title'])
    
    with tab2:
        st.markdown("""
        **Short-term Initiatives (Month 1):**
        - Develop and launch customer loyalty program
        - Optimize product portfolio based on performance data
        - Implement seasonal planning strategies
        - Start competitive monitoring system
        - Set up automated reporting dashboards
        """)
        
        if recommendations['strategic_actions']:
            st.info("**Next Month's Focus:** " + recommendations['strategic_actions'][0]['title'])
    
    with tab3:
        st.markdown("""
        **Long-term Strategy (Quarter 1):**
        - Expand successful product lines
        - Develop comprehensive market positioning
        - Implement advanced predictive analytics
        - Scale successful promotional initiatives
        - Build customer lifetime value models
        """)
        
        st.success("**Expected Quarterly Impact:** 25-40% revenue growth")
    
    # Download Report
    st.markdown("---")
    st.subheader("📥 Export Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="💾 Download Full Report",
            data=generate_report_text(recommendations, business_impact),
            file_name=f"bizboost_ai_recommendations_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        if st.button("🔄 Refresh Recommendations", use_container_width=True):
            st.rerun()

def generate_report_text(recommendations, business_impact):
    """Generate a comprehensive text report"""
    report = "BIZBOOST AI RECOMMENDATION REPORT\n"
    report += "=" * 50 + "\n"
    report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    report += f"Business: {user_data.get('business_name', 'N/A')}\n"
    report += "=" * 50 + "\n\n"
    
    report += "EXECUTIVE SUMMARY\n"
    report += "-" * 30 + "\n"
    report += f"Total Revenue Potential: ₦{business_impact['revenue_increase']:,.0f}+\n"
    report += f"Cost Reduction Potential: ₦{business_impact['cost_reduction']:,.0f}+\n"
    report += f"Efficiency Gains: {business_impact['efficiency_gains']}%+\n\n"
    
    for category, items in recommendations.items():
        if items:
            report += f"{category.upper().replace('_', ' ')}\n"
            report += "-" * 30 + "\n"
            for i, item in enumerate(items, 1):
                report += f"{i}. {item['title']}\n"
                report += f"   {item['description']}\n"
                if 'expected_benefit' in item:
                    report += f"   Expected: {item['expected_benefit']}\n"
                if 'impact' in item:
                    report += f"   Impact: {item['impact'].upper()}\n"
                report += "\n"
    
    report += "\nIMPLEMENTATION ROADMAP\n"
    report += "-" * 30 + "\n"
    report += "Week 1: Immediate actions and quick wins\n"
    report += "Month 1: Strategic initiatives and optimizations\n"
    report += "Quarter 1: Long-term growth and scaling\n"
    
    return report

if __name__ == "__main__":
    main()