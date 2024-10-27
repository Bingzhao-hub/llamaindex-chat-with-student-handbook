import streamlit as st
from copilot import Copilot
import requests
import os

### set openai key and weather API key, first check if they are in environment variables, if not, prompt the user for input

st.title("💬 Chat with Columbia Copilot")
st.caption("🚀 A Streamlit chatbot powered by OpenAI")
st.caption("[View the source code](https://github.com/Bingzhao-hub/llamaindex-chat-with-student-handbook)")

# Get OpenAI API Key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    openai_api_key = st.text_input("Please enter your OpenAI API Key", type="password")

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")

# Get Weather API Key
weather_api_key = os.getenv("WEATHER_API_KEY")
if not weather_api_key:
    weather_api_key = st.text_input("Please enter your OpenWeatherMap API Key", type="password")

if not weather_api_key:
    st.info("Please add your Weather API key to get weather information.", icon="☁️")
    
# Proceed only if both keys are entered
if openai_api_key and weather_api_key:
    if "messages" not in st.session_state.keys():  # Initialize the chat messages history
        st.session_state.messages = [
            {"role": "assistant", "content": "I am Columbia Copilot, your personal assistant. You can ask me about Columbia University. Especially, I am trained to be an expert of the Marketing Division at Columbia Business School."}
        ]

    @st.cache_resource
    def load_copilot():
        return Copilot()

    if "chat_copilot" not in st.session_state.keys():  # Initialize the chat engine
        st.session_state.chat_copilot = load_copilot()

    if prompt := st.chat_input("Introduce the Marketing Division at Columbia Business School"):  # Prompt for user input and save to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

    for message in st.session_state.messages:  # Write message history to UI
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # If last message is not from assistant, generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            retrived_info, answer = st.session_state.chat_copilot.ask(prompt, messages=st.session_state.messages[:-1], openai_key=openai_api_key)
            
            if isinstance(answer, str):
                st.write(answer)
            else:
                ### write stream answer to UI
                def generate():
                    for chunk in answer:
                        content = chunk.choices[0].delta.content
                        if content:
                            yield content
                answer = st.write_stream(generate())

            st.session_state.messages.append({"role": "assistant", "content": answer})

    ### Add weather functionality below
    def get_weather(city="New York"):
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = f"{base_url}q={city}&appid={weather_api_key}&units=metric"
        
        response = requests.get(complete_url)
        
        if response.status_code == 200:
            data = response.json()
            main = data['main']
            weather_desc = data['weather'][0]['description']
            temp = main['temp']
            feels_like = main['feels_like']
            humidity = main['humidity']

            st.write(f"### Weather in {city}")
            st.write(f"**Temperature**: {temp}°C")
            st.write(f"**Feels Like**: {feels_like}°C")
            st.write(f"**Weather**: {weather_desc}")
            st.write(f"**Humidity**: {humidity}%")
        else:
            st.error(f"City {city} not found. Please check the spelling.")

    st.write("---")  # Separator for UI

    st.write("## Check the weather")
    city = st.text_input("Enter city name to get the weather (default is New York)", "New York")
    if st.button("Get Weather"):
        get_weather(city)
