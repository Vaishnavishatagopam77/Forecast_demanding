# Import necessary modules
from fastapi import FastAPI  # FastAPI for building the web API
from pydantic import BaseModel  # Pydantic for request/response model validation
from pymongo import MongoClient  # MongoClient to connect to MongoDB
from bson import json_util  # Utility to convert BSON to JSON
import pandas as pd  # Pandas for data manipulation
from prophet import Prophet  # Prophet for time-series forecasting
import json  # JSON for response formatting
from transformers import pipeline  # HuggingFace pipeline for NLP tasks

# Initialize the FastAPI app
app = FastAPI()

# ----------------------------------------
# === MongoDB Connection Setup ===
# ----------------------------------------

# Create a connection to the local MongoDB server
client = MongoClient("mongodb://localhost:27017/")

# Select the database named 'supply_chain_db'
db = client["supply_chain_db"]

# Select the collection (table equivalent) named 'sales_data'
collection = db["sales_data"]

# ----------------------------------------
# === Endpoint 1: Get All Data ===
# ----------------------------------------

@app.get("/all_data")
def get_all_data():
    """
    Returns all documents from the 'sales_data' collection in MongoDB.
    Data is converted to JSON-compatible format.
    """
    # Fetch all records as a list of documents
    data = list(collection.find())

    # Convert BSON data to JSON (handles ObjectId and datetime)
    return json.loads(json_util.dumps(data))

# ----------------------------------------
# === Endpoint 2: Forecast Sales for Product ===
# ----------------------------------------

@app.get("/forecast/{product_id}")
def forecast_demand(product_id: str):
    """
    Returns a 30-day demand forecast using Prophet for the specified product.
    """
    # Step 1: Get historical sales data for given product_id
    data = list(collection.find({"product_id": product_id}))

    # Step 2: Handle case when product is not found
    if not data:
        return {"error": "Product not found"}

    # Step 3: Convert MongoDB documents into a pandas DataFrame
    df = pd.DataFrame(data)

    # Convert 'date' column to datetime type
    df["date"] = pd.to_datetime(df["date"])

    # Sort data by date for time series modeling
    df = df.sort_values("date")

    # Step 4: Prepare the data for Prophet (rename columns as required)
    df_prophet = df[["date", "sales_quantity"]].rename(columns={
        "date": "ds",    # Prophet expects 'ds' for datetime
        "sales_quantity": "y"  # Prophet expects 'y' for the target variable
    })

    # Step 5: Initialize and train the Prophet model
    model = Prophet()
    model.fit(df_prophet)

    # Step 6: Create a DataFrame for the next 30 days to forecast
    future = model.make_future_dataframe(periods=30)

    # Step 7: Generate predictions
    forecast = model.predict(future)

    # Step 8: Select the last 30 days of predictions and return as JSON
    result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(30)
    return json.loads(result.to_json(orient="records", date_format="iso"))

# ----------------------------------------
# === Endpoint 3: Inventory Optimization ===
# ----------------------------------------

@app.get("/inventory_optimize/{product_id}")
def optimize_inventory(product_id: str):
    """
    Calculates inventory recommendations using Reorder Point formula.
    Includes demand forecast, safety stock, and reorder quantity.
    """
    # Step 1: Fetch product-specific data
    data = list(collection.find({"product_id": product_id}))
    if not data:
        return {"error": "Product not found"}

    # Step 2: Convert to DataFrame and clean/prepare
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    # Extract current inventory level from latest record
    current_inventory = int(df.iloc[-1]["inventory_level"])

    # Step 3: Forecast future demand using Prophet
    df_prophet = df[["date", "sales_quantity"]].rename(columns={"date": "ds", "sales_quantity": "y"})
    model = Prophet()
    model.fit(df_prophet)
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    next_30_days = forecast.tail(30)

    # Step 4: Calculate inventory metrics
    lead_time_days = 5  # Days it takes to receive new stock
    holding_cost_per_unit = 2.5  # Optional; not used in current logic

    # Calculate Safety Stock using 90% confidence (1.65 * std deviation)
    safety_stock = next_30_days["yhat"].std() * 1.65

    # Average daily demand (used in reorder point calculation)
    avg_daily_demand = next_30_days["yhat"].mean()

    # Reorder Point formula
    reorder_point = (avg_daily_demand * lead_time_days) + safety_stock

    # Recommended reorder quantity
    reorder_qty = reorder_point - current_inventory
    reorder_qty = max(0, reorder_qty)  # Avoid negative values

    # Return all calculated values in a JSON response
    return {
        "product_id": str(product_id),
        "current_inventory": current_inventory,
        "predicted_avg_daily_demand": round(float(avg_daily_demand), 2),
        "predicted_demand_std_dev": round(float(next_30_days['yhat'].std()), 2),
        "lead_time_days": lead_time_days,
        "safety_stock": round(float(safety_stock), 2),
        "reorder_point": round(float(reorder_point), 2),
        "recommended_reorder_quantity": int(round(reorder_qty)),
        "note": "Uses Reorder Point formula with safety stock (90% confidence)"
    }

# ----------------------------------------
# === Endpoint 4: Market Sentiment Analysis ===
# ----------------------------------------

# Load HuggingFace transformer pipeline for sentiment analysis
sentiment_analyzer = pipeline("sentiment-analysis")

@app.post("/market_analysis")
def analyze_market_trend(text: str):
    """
    Uses HuggingFace Transformers to analyze market sentiment from text.
    Returns sentiment label, confidence score, and suggested action.
    """
    # Perform sentiment analysis
    result = sentiment_analyzer(text)

    # Extract the label (POSITIVE/NEGATIVE) and confidence score
    sentiment = result[0]['label']
    score = result[0]['score']

    # Suggest action based on sentiment
    if sentiment == "NEGATIVE":
        action = "⚠️ Consider lowering demand forecast or pausing stock."
    elif sentiment == "POSITIVE":
        action = "✅ Consider boosting inventory for increased demand."
    else:
        action = "🔍 Monitor closely."

    # Return structured response
    return {
        "text": text,
        "sentiment": sentiment,
        "confidence": round(score, 2),
        "suggested_action": action
    }
