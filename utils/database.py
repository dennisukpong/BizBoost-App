import os
import pymongo
import streamlit as st

class MongoDBClient:
    def __init__(self):
        self.uri = st.secrets.get("MONGODB_URI", "mongodb://localhost:27017")
        self.database_name = st.secrets.get("DATABASE_NAME", "bizboost")
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.database_name]
            # Test connection
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB successfully")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection error: {e}")
            # Fallback to local storage for demo
            self.client = None
            self.db = None
            return False
    
    def get_collection(self, collection_name):
        """Get a collection from the database"""
        if self.db is None:
            return None
        return self.db[collection_name]
    
    def is_connected(self):
        """Check if MongoDB is connected"""
        return self.client is not None and self.db is not None

# Global database instance
db_client = MongoDBClient()

# Collection names
USERS_COLLECTION = "users"
SALES_DATA_COLLECTION = "sales_data"

def get_users_collection():
    return db_client.get_collection(USERS_COLLECTION)

def get_sales_data_collection():
    return db_client.get_collection(SALES_DATA_COLLECTION)