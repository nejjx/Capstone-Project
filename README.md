# AgroAdvisor – LLM-Assisted Virtual Agent for Crop Yield Prediction

## Overview

**AgroAdvisor** is an AI-powered virtual assistant designed to support Australian farmers by predicting crop yields and providing personalized agronomic recommendations. The system leverages a large language model (LLM) alongside weather data and machine learning to offer location-specific, actionable insights for improved crop management.

---

## Core Features

- **Location-Aware Predictions**  
  Users input their location, and AgroAdvisor fetches 7-day weather forecasts (temperature and rainfall) from the Open-Meteo API. A large language model (LLM) processes and reasons over this data to support predictions and advice.

- **Smart Yield Estimation**  
  An XGBoost regression model predicts crop yields based on normalized environmental factors, pesticide usage, and crop selection parameters.

- **LLM-Powered Guidance**  
  Using Google Gemini Pro through LangChain, the assistant provides tailored advice on:  
  - The best crop to grow based on yield forecasts  
  - Ideal soil conditions, irrigation schedules, and pest management

- **Conversational Workflow**  
  The user interacts through a Flask-based web app simulating an intelligent virtual assistant, enabling a natural and informative experience.

---

## Technical Stack

- **Large Language Model (LLM):** Google Gemini Pro via LangChain  
- **Machine Learning Model:** XGBoost for crop yield prediction  
- **APIs:** Open-Meteo (weather), DuckDuckGo Search  
- **Frameworks & Libraries:** Flask, Pandas, scikit-learn, geopy

---

## Project Structure

- `app.py` – Main Flask application integrating APIs, ML model, and LLM logic  
- `Initial Project Draft (detailed).ipynb` – Jupyter notebook documenting data exploration, model development, and project context  
- `xgb_model.pkl` – Pre-trained XGBoost regression model  
- `templates/` and `static/` – Flask app frontend files and assets

---

## Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/nejjx/Capstone-Project.git
   cd Capstone-Project

2. **Create and activate a Python virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate     # On Windows: venv\Scripts\activate

3. **Install required packages**

   ```bash
   pip install flask pandas scikit-learn xgboost geopy langchain

4. **Set environment variables**
   Configure API keys needed for Google Gemini Pro, Open-Meteo, or any other services you use.

5. **Run the Flask application**

   ```bash
   python app.py
   
6. **Open your browser and go to**

   ```bash
   http://localhost:5000

---

## Notes & Future Work

- Current model and LLM usage require valid API credentials and internet access.

- Future improvements could include expanding supported crops, refining yield model accuracy with more datasets, and enhancing the conversational UI.

---

## Credits

- Developed by the AgroAdvisor team as part of the AI/Analytics Capstone Project at University of Technology Sydney supervised by Dr. YiFei Dong
  
- Team members: Neja Abeywickrama, Neha Yogeswaran, Hanlin Liao, Lang Li

- **Neja Abeywickrama** — Project lead, responsible for LLM and API integration, data exploration, creating the comprehensive Google Colab notebook (initial draft), and assisting with backend integration.

- Thanks to open-source libraries and APIs that power this project.


