import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')
import streamlit as st
from .recommendation_engine import AdvancedRecommendationEngine, calculate_business_impact

@st.cache_data(ttl=3600)
def analyze_sales_trends(df):
    """
    Analyze sales data and return key insights
    """
    insights = []
    
    # Convert date and calculate revenue
    df['date'] = pd.to_datetime(df['date'])
    df['revenue'] = df['quantity'] * df['price']
    df['day_of_week'] = df['date'].dt.day_name()
    df['month'] = df['date'].dt.month_name()
    
    # Insight 1: Best selling products
    product_revenue = df.groupby('product')['revenue'].sum()
    if not product_revenue.empty:
        top_product = product_revenue.idxmax()
        top_product_revenue = product_revenue.max()
        total_revenue = df['revenue'].sum()
        
        insights.append({
            'title': f"Top Performing Product: {top_product}",
            'description': f"{top_product} generates ₦{top_product_revenue:,.0f} in revenue, accounting for {top_product_revenue/total_revenue*100:.1f}% of your total sales.",
            'impact': "High"
        })
    
    # Insight 2: Weekly patterns
    daily_revenue = df.groupby('day_of_week')['revenue'].sum()
    if not daily_revenue.empty:
        best_day = daily_revenue.idxmax()
        best_day_revenue = daily_revenue.max()
        
        # Reorder days for proper calculation
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_revenue = daily_revenue.reindex(days_order, fill_value=0)
        
        weekend_revenue = daily_revenue[['Saturday', 'Sunday']].sum() if 'Saturday' in daily_revenue.index and 'Sunday' in daily_revenue.index else 0
        weekday_revenue = daily_revenue[['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']].sum()
        
        if weekend_revenue > weekday_revenue / 5 * 2 and weekday_revenue > 0:
            insights.append({
                'title': "Weekend Sales Boost",
                'description': f"Your sales are {(weekend_revenue/(weekday_revenue/5)*100 - 100):.0f}% higher on weekends compared to average weekdays. {best_day} is your best day.",
                'impact': "Medium"
            })
    
    # Insight 3: Product performance gaps
    product_performance = df.groupby('product').agg({
        'revenue': 'sum',
        'quantity': 'sum'
    })
    product_performance['price_point'] = df.groupby('product')['price'].mean()
    
    if not product_performance.empty:
        avg_quantity = product_performance['quantity'].mean()
        underperforming = product_performance[product_performance['quantity'] < avg_quantity * 0.5]
        
        if not underperforming.empty:
            product_name = underperforming.index[0]
            insights.append({
                'title': f"Underperforming Product: {product_name}",
                'description': f"{product_name} has low sales volume despite its price point. Consider promotions or bundle deals.",
                'impact': "Medium"
            })
    
    # Insight 4: Revenue trends over time
    monthly_revenue = df.groupby(df['date'].dt.to_period('M'))['revenue'].sum()
    if len(monthly_revenue) > 1:
        growth_rate = (monthly_revenue.iloc[-1] - monthly_revenue.iloc[-2]) / monthly_revenue.iloc[-2] * 100 if monthly_revenue.iloc[-2] > 0 else 0
        trend = "growing" if growth_rate > 0 else "declining"
        insights.append({
            'title': f"Revenue Trend: {trend.capitalize()}",
            'description': f"Your revenue is {trend} at a rate of {abs(growth_rate):.1f}% month-over-month.",
            'impact': "High" if abs(growth_rate) > 10 else "Medium"
        })
    
    return insights

@st.cache_data(ttl=3600)
def generate_business_tips(insights):
    """
    Generate actionable business tips based on insights
    """
    tips = []
    
    for insight in insights:
        title = insight['title']
        
        if "Top Performing Product" in title:
            product = title.split(": ")[1]
            tips.append({
                'action': f"Create a Special Promotion for {product}",
                'reason': f"This is your best-selling product. Capitalize on its popularity by creating limited-time offers or bundles.",
                'expected_outcome': "Increase overall sales volume and attract new customers"
            })
            
            tips.append({
                'action': f"Use {product} as a Lead Magnet",
                'reason': "Feature this product prominently in your marketing and use it to attract customers who might buy other items.",
                'expected_outcome': "Higher customer acquisition and cross-selling opportunities"
            })
        
        elif "Weekend Sales Boost" in title:
            tips.append({
                'action': "Launch Weekend Specials",
                'reason': "Your customers prefer shopping on weekends. Create exclusive weekend bundles or promotions.",
                'expected_outcome': "Maximize revenue during peak days and build weekend customer loyalty"
            })
            
            tips.append({
                'action': "Increase Weekend Marketing",
                'reason': "Focus your social media and WhatsApp marketing on Thursdays and Fridays to build weekend anticipation.",
                'expected_outcome': "Higher weekend footfall and increased sales"
            })
        
        elif "Underperforming Product" in title:
            product = title.split(": ")[1]
            tips.append({
                'action': f"Revamp {product} Strategy",
                'reason': "This product isn't meeting sales expectations. Consider bundling, price adjustments, or featured promotions.",
                'expected_outcome': "Better inventory turnover and reduced waste"
            })
    
    # Add general tips if we don't have enough
    if len(tips) < 4:
        tips.extend([
            {
                'action': "Implement Customer Loyalty Program",
                'reason': "Retaining existing customers is 5x cheaper than acquiring new ones. Start with simple punch cards or digital points.",
                'expected_outcome': "20-30% increase in repeat customers"
            },
            {
                'action': "Collect Customer Contact Information",
                'reason': "Build a database for targeted promotions. Offer small discounts for WhatsApp number sign-ups.",
                'expected_outcome': "Direct marketing channel and better customer insights"
            }
        ])
    
    return tips[:4]

@st.cache_data(ttl=3600)
def generate_advanced_recommendations(df):
    """Generate advanced AI-powered recommendations"""
    engine = AdvancedRecommendationEngine()
    recommendations = engine.generate_comprehensive_recommendations(df)
    business_impact = calculate_business_impact(recommendations)
    
    return {
        'recommendations': recommendations,
        'business_impact': business_impact
    }

@st.cache_data(ttl=3600)
def create_demo_data():
    """Create comprehensive demo data for presentation"""
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', end='2024-03-20', freq='D')
    products = ['Chocolate Cake', 'Vanilla Cake', 'Small Chops', 'Meat Pie', 'Doughnut', 'Sandwich', 'Juice']
    
    data = []
    for date in dates:
        # Base daily sales
        daily_sales = np.random.randint(8, 25)
        
        for _ in range(daily_sales):
            product = np.random.choice(products, p=[0.25, 0.2, 0.15, 0.15, 0.1, 0.1, 0.05])
            quantity = np.random.randint(1, 4)
            
            # Dynamic pricing and patterns
            base_prices = {
                'Chocolate Cake': 2800, 'Vanilla Cake': 2400, 'Small Chops': 600,
                'Meat Pie': 350, 'Doughnut': 250, 'Sandwich': 1200, 'Juice': 500
            }
            
            price = base_prices[product]
            
            # Weekend boost for cakes
            if product in ['Chocolate Cake', 'Vanilla Cake'] and date.weekday() >= 5:
                quantity += np.random.randint(1, 3)
                price *= 1.1  # 10% weekend premium
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'product': product,
                'quantity': quantity,
                'price': price
            })
    
    return pd.DataFrame(data)