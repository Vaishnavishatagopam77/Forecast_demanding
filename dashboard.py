# === Required Libraries ===
import streamlit as st            # For building the frontend web app
import requests                   # To make API requests to the FastAPI backend
import pandas as pd              # For data handling (like JSON to dataframe)
import plotly.express as px      # For interactive plotting

# === Configuration ===
FASTAPI_URL = "http://localhost:8000"  # URL of the FastAPI backend (can also be hosted on cloud)

# Set the layout and page title of your Streamlit app
st.set_page_config(page_title="📦 Supply Chain Analytics", layout="wide")

# === Sidebar Navigation ===
st.sidebar.title("Supply Chain Tools")              # Sidebar title
tabs = ["📈 Demand Forecast", "📦 Inventory Optimizer", "🧠 Market Sentiment"]  # List of tab options
selected_tab = st.sidebar.radio("Navigate", tabs)   # Radio button for switching between tabs

# === TAB 1: Demand Forecast (uses Prophet model) ===
if selected_tab == "📈 Demand Forecast":
    st.title("📈 Demand Forecast (Prophet)")          # Title of the first tab
    product_id = st.text_input("Enter Product ID:", "P001")  # Text input to enter a product ID

    if st.button("Get Forecast"):                    # Button to trigger forecast request
        # Make a GET request to FastAPI backend to get forecast data for the given product
        res = requests.get(f"{FASTAPI_URL}/forecast/{product_id}")
        
        if res.status_code == 200:
            data = pd.DataFrame(res.json())          # Convert response JSON to DataFrame
            st.success("Forecast Loaded!")           # Show success message
            
            # Create line chart using Plotly
            fig = px.line(data, x="ds", y="yhat", title="30-Day Forecast")
            st.plotly_chart(fig)                     # Display the plot in Streamlit
            st.dataframe(data)                       # Display forecast data as a table
        else:
            st.error("Product ID not found.")        # Error message if product not in DB

# === TAB 2: Inventory Optimizer ===
elif selected_tab == "📦 Inventory Optimizer":
    st.title("📦 Inventory Optimization")            # Title of second tab

    # Another text input, with a different key to avoid conflicts
    product_id = st.text_input("Enter Product ID:", "P001", key="inventory")

    if st.button("Get Inventory Suggestion"):
        # Call FastAPI route to get optimized inventory numbers
        res = requests.get(f"{FASTAPI_URL}/inventory_optimize/{product_id}")
        
        if res.status_code == 200:
            result = res.json()                      # Parse JSON result

            # Display metrics using Streamlit's KPI style boxes
            st.metric("📦 Current Inventory", result['current_inventory'])
            st.metric("📈 Reorder Point", result['reorder_point'])
            st.metric("✅ Reorder Quantity", result['recommended_reorder_quantity'])

            # Display additional note/info and raw JSON
            st.info(result['note'])                  # Optional note or context
            st.json(result)                          # Full JSON object for debugging or deeper view
        else:
            st.error("Product ID not found.")        # Error if product doesn't exist

# === TAB 3: Market Sentiment Analysis using NLP ===
elif selected_tab == "🧠 Market Sentiment":
    st.title("🧠 Market Sentiment Analysis")         # Title of third tab

    # Text area to enter raw news or reviews
    input_text = st.text_area("Enter market news, customer reviews, or text:")

    if st.button("Analyze"):                         # Trigger analysis
        # Send POST request to FastAPI NLP endpoint with user input
        res = requests.post(f"{FASTAPI_URL}/market_analysis", params={"text": input_text})
        
        if res.status_code == 200:
            result = res.json()                      # Get JSON response

            # Show sentiment result with confidence
            st.success(f"Sentiment: {result['sentiment']} ({result['confidence']*100:.2f}%)")

            # Display any recommended action based on the analysis
            st.info(result["suggested_action"])
        else:
            st.error("Analysis failed.")             # Error handling
