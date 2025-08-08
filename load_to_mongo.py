# Import necessary libraries
import pandas as pd  # For reading and handling CSV data
from pymongo import MongoClient  # For connecting and interacting with MongoDB

# ==========================
# 1. CONNECT TO MONGODB
# ==========================

# Create a MongoClient instance to connect to the local MongoDB server
# "localhost" refers to your local machine
# "27017" is the default port number on which MongoDB runs
client = MongoClient("mongodb://localhost:27017/")

# Create or access a database named "supply_chain_db"
# If it doesn't exist, MongoDB will create it automatically
db = client["supply_chain_db"]

# Create or access a collection (similar to a table in SQL) named "sales_data"
collection = db["sales_data"]

# ==========================
# 2. LOAD CSV FILE INTO PANDAS
# ==========================

# Read the CSV file using pandas
# Replace 'supply_chain_data.csv' with the correct path to your file if it's not in the same directory
df = pd.read_csv("supply_chain_data.csv")

# Convert the pandas DataFrame into a list of dictionaries
# Each dictionary represents one row of data and will be inserted as one document in MongoDB
data = df.to_dict(orient="records")

# ==========================
# 3. INSERT DATA INTO MONGODB
# ==========================

# Optional: Clear old data from the collection before inserting new data
# This ensures you don't get duplicate data if you run the script multiple times
collection.delete_many({})  # Deletes all documents from the collection

# Insert the list of dictionaries (records) into MongoDB
# insert_many allows you to insert all rows at once
collection.insert_many(data)

# ==========================
# 4. SUCCESS MESSAGE
# ==========================

# Print confirmation message to indicate successful upload
print("✅ Data loaded successfully into MongoDB!")
