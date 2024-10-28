import streamlit as st
from copilot import Copilot
import requests
import os

st.title("💬 Chat with Columbia Copilot")
st.caption("🚀 A Streamlit chatbot powered by OpenAI")
st.caption("[View the source code](https://github.com/Bingzhao-hub/llamaindex-chat-with-student-handbook)")

# Get OpenAI API Key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    openai_api_key = st.text_input("Please enter your OpenAI API Key", type="password")

# Get Weather API Key
weather_api_key = "a4b430940703037c0e0153bca6f54f08"
if not weather_api_key:
    weather_api_key = st.text_input("Please enter your OpenWeatherMap API Key", type="password")

# Only proceed if both API keys are available
if openai_api_key and weather_api_key:
    if "messages" not in st.session_state.keys():  # Initialize chat messages history
        st.session_state.messages = [
            {"role": "assistant", "content": "I am Columbia Copilot. You can ask me about Columbia University, especially any questions specific to the marketing department at CBS. I am also an expert of weather, ask me about the weather in any city!"}
        ]

    @st.cache_resource
    def load_copilot():
        return Copilot()

    if "chat_copilot" not in st.session_state.keys():  # Initialize the chat engine
        st.session_state.chat_copilot = load_copilot()

    # Function to fetch weather data
    def get_weather(city):
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
            return f"Weather in {city}:\n\nTemperature: {temp}°C\n\nFeels Like: {feels_like}°C\n\nWeather: {weather_desc}\n\nHumidity: {humidity}%"

        else:
            return f"Sorry, I couldn't find the weather for {city}. Please check the city name."

    # Detect if the user prompt is related to weather
    def is_weather_query(prompt):
        keywords = ["weather", "temperature", "forecast", "rain", "sunny"]
        return any(keyword in prompt.lower() for keyword in keywords)

    if prompt := st.chat_input("Ask something, like 'What's the weather in London?'"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        if is_weather_query(prompt):  # Check if the prompt is a weather query
            # Extract city from prompt (default to Columbia if not specified)
            city = prompt.split("in")[-1].strip() if "in" in prompt else "Columbia"
            weather_info = get_weather(city)
            st.session_state.messages.append({"role": "assistant", "content": weather_info})
        else:
            # Process normal chat via Copilot
            retrived_info, answer = st.session_state.chat_copilot.ask(prompt, messages=st.session_state.messages[:-1], openai_key=openai_api_key)

            if isinstance(answer, str):
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                def generate():
                    for chunk in answer:
                        content = chunk.choices[0].delta.content
                        if content:
                            yield content
                stream_answer = st.write_stream(generate())
                st.session_state.messages.append({"role": "assistant", "content": stream_answer})

    # Display the message history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
