import streamlit as st
import bcrypt
import pandas as pd
from datetime import datetime
from .database import get_users_collection, get_sales_data_collection, db_client

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    """Verify a password against its hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def init_demo_user():
    """Initialize demo user if MongoDB is connected"""
    users_collection = get_users_collection()
    if users_collection is not None:
        demo_user = users_collection.find_one({"username": "demo_bakery"})
        if not demo_user:
            users_collection.insert_one({
                'username': 'demo_bakery',
                'password': hash_password('demo123'),
                'business_name': "Ngozi's Bakery (Demo)",
                'business_type': "Restaurant/Bakery",
                'created_at': datetime.now().isoformat(),
                'last_login': None
            })
            print("✅ Demo user created in MongoDB")

def register_user(username, password, business_name, business_type):
    """Register a new user in MongoDB"""
    users_collection = get_users_collection()
    
    if users_collection is None:
        return False, "Database connection failed"
    
    # Check if username exists
    if users_collection.find_one({"username": username}):
        return False, "Username already exists"
    
    # Create user document
    user_doc = {
        'username': username,
        'password': hash_password(password),
        'business_name': business_name,
        'business_type': business_type,
        'created_at': datetime.now().isoformat(),
        'last_login': None,
        'updated_at': datetime.now().isoformat()
    }
    
    try:
        users_collection.insert_one(user_doc)
        return True, "Registration successful"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"

def authenticate_user(username, password):
    """Authenticate a user from MongoDB"""
    users_collection = get_users_collection()
    
    if users_collection is None:
        return False, "Database connection failed"
    
    user = users_collection.find_one({"username": username})
    
    if not user:
        return False, "User not found"
    
    if not verify_password(password, user['password']):
        return False, "Invalid password"
    
    # Update last login
    users_collection.update_one(
        {"username": username},
        {"$set": {"last_login": datetime.now().isoformat()}}
    )
    
    return True, "Login successful"

def get_user_data(username):
    """Get user data from MongoDB"""
    users_collection = get_users_collection()
    
    if users_collection is None:
        return {}
    
    user = users_collection.find_one({"username": username}, {'password': 0})  # Exclude password
    return user or {}

def save_user_sales_data(username, data):
    """Save sales data to MongoDB"""
    sales_collection = get_sales_data_collection()
    
    if sales_collection is None:
        return False
    
    try:
        # Convert DataFrame to dictionary if needed
        if isinstance(data, pd.DataFrame):
            records = data.to_dict('records')
        else:
            records = data
        
        # Delete existing data for this user
        sales_collection.delete_many({"username": username})
        
        # Insert new data with username and timestamp
        documents = []
        for record in records:
            document = {
                "username": username,
                "data": record,
                "uploaded_at": datetime.now().isoformat()
            }
            documents.append(document)
        
        if documents:
            sales_collection.insert_many(documents)
        
        return True
    except Exception as e:
        print(f"Error saving sales data: {e}")
        return False

def load_user_sales_data(username):
    """Load sales data from MongoDB"""
    sales_collection = get_sales_data_collection()
    
    if sales_collection is None:
        return None
    
    try:
        # Get all sales data for this user
        cursor = sales_collection.find({"username": username})
        records = [doc["data"] for doc in cursor]
        
        if records:
            return pd.DataFrame(records)
        return None
    except Exception as e:
        print(f"Error loading sales data: {e}")
        return None

def delete_user_data(username):
    """Delete all user data from MongoDB"""
    sales_collection = get_sales_data_collection()
    
    if sales_collection is not None:
        sales_collection.delete_many({"username": username})
    
    return True

# Initialize demo user when module loads
init_demo_user()