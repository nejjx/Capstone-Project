from flask import Flask
from flask import render_template, request, redirect, session, Response, jsonify, url_for, stream_with_context
import time
import requests


import os
import getpass
import langchain
import pandas as pd
import numpy as np
import pickle

from geopy.geocoders import Nominatim

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.preprocessing import MinMaxScaler

from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.agents import load_tools
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain.chains.api.prompt import API_RESPONSE_PROMPT
from langchain.chains import APIChain
# from langchain.prompts.prompt import PromptTemplate
from langchain.chains.api import open_meteo_docs
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.tools import DuckDuckGoSearchRun
from duckduckgo_search import DDGS





app= Flask(__name__)



@app.route("/")
def index():
    return render_template("index.html")

current_directory = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_directory, "xgb_model.pkl")
crop_prediction_model = pickle.load(open(model_path, "rb"))

os.environ["GOOGLE_API_KEY"] = "AIzaSyCsAmxS0aDzRx6isQpC9qSCerDiZtnYkVY"

geolocator = Nominatim(user_agent="geo_locator")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
open_meteo_api = open_meteo_docs.OPEN_METEO_DOCS
search = DDGS()

tools = load_tools(["ddg-search"], llm=llm)

# for the Weather API LLM Agent
limit_to_domains = [f"https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&daily=temperature_2m_max,temperature_2m_min,rain_sum,&timezone=Australia%2FSydney"]

# Define crops and their associated data
crop_labels = ["Maize", "Potatoes", "Rice, paddy", "Sorghum", "Soybeans", "Sweet potatoes", "Wheat"]


# Initialize a dictionary to store pesticide amounts for each crop
pesticides_amount = {}

global temperature 
global avg_temperature 
global rainfall


le_item = LabelEncoder()
scaler = StandardScaler()

def locate_user_address(address):
    location = geolocator.geocode(address)
    return location

def retrieve_weather_data(location):
    chain = APIChain.from_llm_and_api_docs(llm, open_meteo_api, verbose=True, limit_to_domains=limit_to_domains)
    temperature_response = chain.run(f'What is the temperature like in {location} Australia in the next seven days?')
    rainfall_response = chain.run(f'What is the total rainfall like {location} Australia in the next seven days?')
    return temperature_response, rainfall_response

def extract_temperature_values(temperature_response):
    temperature_extraction_prompt = PromptTemplate(input_variables=["text_input"], template="Extract the minimum and maximum temperature values. Only 2 temperature values are expected to be there.:\n\n {text_input}")
    temperature_extraction_agent = LLMChain(llm=llm, prompt=temperature_extraction_prompt)
    temperature = temperature_extraction_agent.run(temperature_response)
    try:
        if temperature is None:
            temperature = 0
        if not temperature[0].isdigit():
            temperature = 0
    except:
        temperature = 0
    return temperature

def calculate_average_temperature(temperature):
    global avg_temperature
    avg_temperature_calculation_prompt = PromptTemplate(input_variables=["text_input"], template="Calculate the average temperature. Give me just the average temperature with no text and no unit:\n\n {text_input}")
    avg_temperature_calculation_agent = LLMChain(llm=llm, prompt=avg_temperature_calculation_prompt)
    avg_temperature = avg_temperature_calculation_agent.run(temperature)
    print(avg_temperature)
    return avg_temperature

def extract_rainfall_values(rainfall_response):
    global rainfall
    rainfall_extraction_prompt = PromptTemplate(input_variables=["text_input"], template="Extract the total rainfall and multiply this by 4 and give the answer with no unit. :\n\n {text_input}")
    rainfall_extraction_agent = LLMChain(llm=llm, prompt=rainfall_extraction_prompt)
    rainfall = rainfall_extraction_agent.run(rainfall_response)
    print(type(rainfall))
    try:
        if rainfall is None:
            rainfall = 0
        else:
            rainfall = float(rainfall)
    except: 
        rainfall = 0
    return rainfall


def predict_yield(avg_temperature, rainfall, pesticides_input):
    le_item.fit(crop_labels)
    avg_temp_normalized = scaler.fit_transform(np.array(avg_temperature).reshape(-1, 1))
    rainfall_normalized = scaler.fit_transform(np.array(rainfall).reshape(-1, 1))
    
    results = []

    with open('predicted_yield.txt', 'w') as file:
        for pesticide in pesticides_input:
            crop = pesticide['crop']
            amount = float(pesticide['amount'])

            item_encoded = le_item.transform([crop])[0]
            
            X_predict = np.array([
                item_encoded,
                amount,
                avg_temp_normalized[0][0],
                rainfall_normalized[0][0]
            ]).reshape(1, -1)
            
            y_pred = crop_prediction_model.predict(X_predict)
            
            result = f"Predicted Yield for {crop}: {y_pred[0]}"
            results.append(result)
            file.write(result + "\n")
    
    return "\n".join(results)

def recommend_crop(predicted_yield):
    crop_recommendation_prompt = PromptTemplate(input_variables=["text_input"], template="Extract and recommend the farmer the best crop to grow.:\n\n {text_input}")
    crop_recommendation_agent = LLMChain(llm=llm, prompt=crop_recommendation_prompt)
    recommended_crop_name = (crop_recommendation_agent.run(predicted_yield))
    return recommended_crop_name

def recommend_crop_exact(predicted_yield):
    crop_recommendation_prompt = PromptTemplate(input_variables=["text_input"], template="Extract and recommend the farmer the best crop to grow. Give only the full crop name :\n\n {text_input}")
    crop_recommendation_agent = LLMChain(llm=llm, prompt=crop_recommendation_prompt)
    recommended_crop_name_exact = (crop_recommendation_agent.run(predicted_yield))
    return recommended_crop_name_exact

def info_retrieval(recommended_crop_name_exact, option):
    agent = initialize_agent(tools,
                         llm,
                         agent="zero-shot-react-description",
                         verbose=True,                  
                         )
    
    # Run the corresponding query based on the user's query
    if option.lower() == "soil":
        query = f"What are the ideal soil conditions for {recommended_crop_name_exact} cultivation in Australia?"
    elif option.lower() == "pests":
        query = f"What are few possible threats from pests for {recommended_crop_name_exact} cultivation in Australia?"
    elif option.lower() == "irrigation":
        query = f"What are the ideal watering measures for {recommended_crop_name_exact} cultivation in Australia?"
    elif option.lower() == "agricultural practices":
        query = f"What are a few agricultural practices for large-scale {recommended_crop_name_exact} cultivation in Australia? Give them as facts"
    else:
        print("Invalid option.")

    response = agent.run(query)
    
    return response
    



@app.route('/process_user_input', methods=['POST'])
def process_user_input():
    # Extract user input from JSON request
    user_input = request.json.get('user_input')
    # extract_temperature_values(temperature_response)

    # Process user input to get location, weather data, recommended crop
    location = locate_user_address(user_input)
    temperature_response, rainfall_response = retrieve_weather_data(location)
    temperature = extract_temperature_values(temperature_response)
    avg_temperature = calculate_average_temperature(temperature)
    rainfall = extract_rainfall_values(rainfall_response)


    # Construct initial message with weather data and recommended crop
    message =''
    message += f"{temperature_response}\n"
    message += f"{rainfall_response}\n"


    return jsonify({'message': message})

@app.route('/process_pesticides_input', methods=['POST'])
def process_pesticides_input():
    pesticides_input = request.json.get('user_input')
    print(pesticides_input)

    predicted_yield = predict_yield(avg_temperature, rainfall, pesticides_input)
    
    with open("predicted_yield.txt", "r") as file:
        predicted_yield_file = file.read()

    recommended_crop = recommend_crop(predicted_yield_file)

    message =''
    message += f"{recommended_crop}\n"

    return jsonify({'message': message})

@app.route('/process_information_request_input', methods=['POST'])
def process_information_request_input():

    option = request.json.get('user_input')

    with open("predicted_yield.txt", "r") as file:
        predicted_yield_file = file.read()
        
    recommended_crop_name_exact = recommend_crop_exact(predicted_yield_file)

    response = info_retrieval(recommended_crop_name_exact, option)

    message =''
    message += f"{response}"

    return jsonify({'message': message})







# @app.route("/get", methods=["GET", "POST"])
# def chat():
#     msg = request.form["message"]
#     input = msg
#     return get_chat_response(input)


# @app.route('/get_chatbot_messages')
# def get_chatbot_messages():
#     return jsonify({'messages': [llm_answer]})




if __name__ == "__main__":
    app.run(debug = True)

