# 📊 Forecast Demanding – Supply Chain Prediction Dashboard

This project focuses on demand forecasting in supply chain management using Python. It includes data loading, preprocessing, demand prediction, and dashboard visualization with MongoDB integration.

## 📁 Project Structure
```bash
Forecast_demanding/
├── dashboard.py # Code for dashboard UI and interaction
├── load_to_mongo.py # Script to load processed data to MongoDB
├── main.py # Main data processing and forecasting script
├── supply_chain_data.csv # Supply chain dataset used for forecasting
├── pycache/ # Python bytecode cache
└── README.md # Project documentation
```


## 🧠 Features

- 📦 Load and preprocess supply chain data
- 📈 Forecast product demand using time series or regression models
- 💾 Store predictions in MongoDB
- 📉 Visualize insights through an interactive dashboard (e.g., Streamlit, Dash)

## 🛠 Technologies Used

- Python (pandas, scikit-learn)
- MongoDB for data storage
- Dashboarding: Streamlit / Dash
- CSV for input data

## 🚀 How to Run

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Vaishnavishatagopam77/Forecast_demanding.git
   cd Forecast_demanding
Install requirements:

pip install -r requirements.txt
Run forecasting and load to MongoDB:

python main.py
python load_to_mongo.py
Launch the dashboard:
python dashboard.py
```
# 📊 Output
Demand trends and predictions by product, region, and date

Database-backed visualization of forecast results

Real-time insights for business decision-making

👩‍💻 Author
Vaishnavi Shatagopam
