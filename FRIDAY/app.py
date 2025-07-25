import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import openai
import geopy
from geopy.geocoders import Nominatim
import gmplot
import os
import subprocess
import math
import webbrowser
import requests
import json
import time
import threading
import googletrans
from googletrans import Translator
import pytz
import wolframalpha
import pyautogui
import psutil
import screen_brightness_control as sbc
from pygame import mixer

# Initialize components
recognizer = sr.Recognizer()
engine = pyttsx3.init()
translator = Translator()
mixer.init()

# Configure voice
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Female voice
engine.setProperty('rate', 180)  # Slightly faster speech
engine.setProperty('volume', 1.0)

# API setup
openai.api_key = os.getenv("YOUR_OPENAI_API_KEY")
wolfram_client = wolframalpha.Client(os.getenv("WOLFRAM_ALPHA_APPID"))
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Global state
current_language = "en"  # Default language
reminders = []

# Supported languages with codes
SUPPORTED_LANGUAGES = {
    "english": "en",
    "hindi": "hi",
    "marathi": "mr",
    "tamil": "ta",
    "telugu": "te",
    "bengali": "bn",
    "gujarati": "gu",
    "kannada": "kn",
    "malayalam": "ml",
    "punjabi": "pa",
    "spanish": "es",
    "french": "fr",
    "german": "de"
}

def speak(text, language=None):
    """Speak text with optional language translation"""
    global current_language
    
    print(f"Friday: {text}")
    
    if language and language != current_language:
        try:
            translated = translator.translate(text, dest=language)
            text = translated.text
            current_language = language
        except:
            pass
    
    engine.say(text)
    engine.runAndWait()

def recognize_speech():
    """Capture and recognize speech with multilingual support"""
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.8)
        try:
           audio = recognizer.listen(source, timeout=8)
        except sr.WaitTimeoutError:
           print("Listening timed out, please try again.")
           return None

        
        try:
            text = recognizer.recognize_google(audio, language="en-IN")
            print(f"User: {text}")
            return text.lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            speak("Sorry, I'm having trouble connecting to the internet")
            return ""
        except Exception as e:
            print(f"Recognition error: {e}")
            return ""

def set_language(command):
    """Change assistant language"""
    global current_language
    
    for lang_name, lang_code in SUPPORTED_LANGUAGES.items():
        if lang_name in command:
            current_language = lang_code
            speak(f"Language changed to {lang_name}", "en")
            return True
    return False

def handle_reminders():
    """Check and notify about reminders"""
    while True:
        now = datetime.datetime.now()
        for reminder in reminders[:]:
            if now >= reminder["time"]:
                speak(f"Reminder: {reminder['message']}")
                reminders.remove(reminder)
        time.sleep(30)

def calculate(command):
    """Handle mathematical calculations"""
    try:
        # Wolfram Alpha for complex calculations
        res = wolfram_client.query(command)
        answer = next(res.results).text
        speak(f"The answer is {answer}")
    except:
        # Fallback to simple calculations
        try:
            if '+' in command:
                parts = command.split('+')
                result = sum(float(p) for p in parts)
            elif '-' in command:
                parts = command.split('-')
                result = float(parts[0]) - float(parts[1])
            elif '×' in command or '*' in command:
                parts = command.split('×') if '×' in command else command.split('*')
                result = float(parts[0]) * float(parts[1])
            elif '÷' in command or '/' in command:
                parts = command.split('÷') if '÷' in command else command.split('/')
                result = float(parts[0]) / float(parts[1])
            elif 'sqrt' in command:
                num = float(command.split('sqrt')[1])
                result = math.sqrt(num)
            elif '^' in command:
                base, exp = command.split('^')
                result = math.pow(float(base), float(exp))
            else:
                speak("I couldn't understand that calculation")
                return
            
            speak(f"The result is {result}")
        except Exception as e:
            print(f"Calculation error: {e}")
            speak("Sorry, I couldn't perform that calculation")

def get_weather(city=None):
    """Get weather information"""
    if not city:
        city = "current location"
    
    try:
        if city == "current location":
            # Get location by IP
            location = requests.get('https://ipinfo.io').json()
            city = location.get('city', 'Mumbai')
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        
        if data["cod"] != 200:
            speak("Sorry, I couldn't get weather information")
            return
        
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        
        speak(f"Current weather in {city}: {description}, Temperature: {temp}°C, "
              f"Humidity: {humidity}%, Wind speed: {wind} m/s")
    except Exception as e:
        print(f"Weather error: {e}")
        speak("Sorry, I couldn't retrieve weather information")

def system_control(command):
    """Control system functions"""
    if 'volume up' in command:
        pyautogui.press('volumeup')
        speak("Volume increased")
    elif 'volume down' in command:
        pyautogui.press('volumedown')
        speak("Volume decreased")
    elif 'mute' in command:
        pyautogui.press('volumemute')
        speak("Sound muted")
    elif 'brightness' in command:
        if 'increase' in command:
            current = sbc.get_brightness()[0]
            sbc.set_brightness(min(current + 20, 100))
            speak("Brightness increased")
        elif 'decrease' in command:
            current = sbc.get_brightness()[0]
            sbc.set_brightness(max(current - 20, 0))
            speak("Brightness decreased")
    elif 'screenshot' in command:
        pyautogui.screenshot().save('screenshot.png')
        speak("Screenshot taken and saved")
    elif 'battery' in command:
        battery = psutil.sensors_battery()
        speak(f"Battery is at {battery.percent}%")
    elif 'sleep' in command:
        speak("Putting system to sleep")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")  # Windows
    else:
        speak("System command not recognized")

def set_reminder(command):
    """Set a reminder"""
    try:
        if 'in' in command:
            idx = command.index('in')
            message = command[:idx].replace('set a reminder', '').strip()
            time_part = command[idx+2:].strip()
            
            # Parse time (e.g., "30 minutes", "2 hours")
            if 'minute' in time_part:
                minutes = int(time_part.split()[0])
            elif 'hour' in time_part:
                minutes = int(time_part.split()[0]) * 60
            else:
                speak("Please specify time in minutes or hours")
                return
            
            reminder_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
            reminders.append({
                "message": message,
                "time": reminder_time
            })
            speak(f"Reminder set for {message} in {minutes} minutes")
    except Exception as e:
        print(f"Reminder error: {e}")
        speak("Sorry, I couldn't set that reminder")

def handle_conversation(command):
    """Handle conversational queries using GPT-3"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Friday, a helpful AI assistant. Respond concisely."},
                {"role": "user", "content": command}
            ]
        )
        reply = response.choices[0].message.content
        speak(reply)
    except Exception as e:
        print(f"GPT error: {e}")
        speak("I'm having trouble processing that request right now")

def process_command(command):
    """Process user commands"""
    if not command:
        return
    
    # Wake word handling
    if 'friday' in command:
        command = command.replace('friday', '').strip()
    
    # Language switching
    if set_language(command):
        return
    
    # Command routing
    if any(word in command for word in ['play', 'song', 'music']):
        song = command.replace('play', '').strip()
        if song:
            speak(f"Playing {song}")
            pywhatkit.playonyt(song)
    
    elif any(word in command for word in ['hi', 'hello', 'hey']):
        greetings = ["Hello sir!", "Hi there!", "Hey, how can I help?"]
        speak(greetings[datetime.datetime.now().second % len(greetings)])
    
    elif 'your name' in command:
        speak('I am Friday, your personal assistant!')
    
    elif 'time' in command:
        tz = pytz.timezone('Asia/Kolkata')
        current_time = datetime.datetime.now(tz).strftime('%I:%M %p')
        speak(f"Current time is {current_time}")
    
    elif 'date' in command:
        today = datetime.datetime.now().strftime('%B %d, %Y')
        speak(f"Today is {today}")
    
    elif any(word in command for word in ['who is', 'what is', 'wikipedia']):
        query = command.replace('wikipedia', '').replace('who is', '').replace('what is', '').strip()
        if query:
            try:
                summary = wikipedia.summary(query, sentences=2)
                speak(summary)
            except:
                speak(f"Sorry, I couldn't find information about {query}")
    
    elif 'joke' in command:
        speak(pyjokes.get_joke())
    
    elif any(word in command for word in ['calculate', 'math', 'solve']):
        calculate(command)
    
    elif any(word in command for word in ['weather', 'temperature']):
        city = command.replace('weather', '').replace('in', '').strip()
        get_weather(city if city != "" else None)
    
    elif any(word in command for word in ['remind', 'reminder']):
        set_reminder(command)
    
    elif any(word in command for word in ['location', 'where am i']):
        try:
            location = requests.get('https://ipinfo.io').json()
            city = location.get('city', 'Unknown')
            region = location.get('region', 'Unknown')
            speak(f"You're in {city}, {region}")
        except:
            speak("Couldn't determine your current location")
    
    elif any(word in command for word in ['open', 'launch']):
        app = command.replace('open', '').replace('launch', '').strip()
        if 'chrome' in app:
            webbrowser.open('https://google.com')
            speak("Opening Chrome")
        elif 'youtube' in app:
            webbrowser.open('https://youtube.com')
            speak("Opening YouTube")
        elif 'notepad' in app:
            os.startfile('notepad.exe')  # Windows
            speak("Opening Notepad")
    
    elif any(word in command for word in ['volume', 'brightness', 'screenshot', 'battery']):
        system_control(command)
    
    elif any(word in command for word in ['exit', 'quit', 'goodbye']):
        speak("Goodbye! Have a great day!")
        exit()
    
    else:
        handle_conversation(command)

def main():
    """Main application loop"""
    # Start reminder thread
    reminder_thread = threading.Thread(target=handle_reminders, daemon=True)
    reminder_thread.start()
    
    speak("Friday activated. How can I help you today?", "en")
    
    while True:
        command = recognize_speech()
        process_command(command)
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Goodbye!")