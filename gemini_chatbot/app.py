import os
from dotenv import load_dotenv
import google.generativeai as genai
from serpapi import GoogleSearch
import re
import time

# Load API keys from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# Validate keys
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")
if not SERPAPI_KEY:
    raise ValueError("SERPAPI_KEY not found in environment variables.")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="models/gemini-pro")
chat = model.start_chat(history=[])

# Enhanced Google Search Function
def search_google(query):
    """Perform a Google search and return formatted results"""
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 3  # Get top 3 results
    }
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Try to extract different types of results
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        
        if "featured_snippet" in results and "snippet" in results["featured_snippet"]:
            return f"Featured snippet: {results['featured_snippet']['snippet']}"
        
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]
        
        # Compile top organic results
        if "organic_results" in results:
            snippets = []
            for i, res in enumerate(results["organic_results"][:3], 1):
                if "snippet" in res:
                    snippets.append(f"{i}. {res['snippet']}")
                elif "link" in res:
                    snippets.append(f"{i}. {res.get('title', 'No title')} - {res['link']}")
            
            if snippets:
                return "\n".join(snippets)
                
        return "I couldn't find any relevant information."
        
    except Exception as e:
        print(f"Search error: {e}")
        return "There was an error performing the search."

# Check if query needs live data
def needs_live_data(query):
    """Determine if a query requires live information"""
    query = query.lower()
    live_keywords = [
        "weather", "temperature", "forecast",
        "price", "stock", "currency", "exchange rate",
        "time", "date", "current", "now", "today", 
        "news", "headlines", "update", "latest"
    ]
    
    # Check for time/date patterns
    time_patterns = [
        r"time in .+",
        r"what time is it",
        r"current time",
        r"date today",
        r"what's the date"
    ]
    
    if any(kw in query for kw in live_keywords):
        return True
        
    for pattern in time_patterns:
        if re.search(pattern, query):
            return True
            
    return False

# Format response with typing effect
def print_with_typing(text, delay=0.02):
    """Print text with typing effect"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

# Main chat loop
print("Hello! I'm Gemini. Ask me anything. Type 'exit' to quit.")
print("I can also fetch live information like weather, prices, time, and news.\n")

while True:
    try:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
            
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye!")
            break

        # Handle special commands
        if user_input.lower() in ['help', '/help']:
            print("\nAvailable commands:")
            print("- 'exit' or 'quit': End conversation")
            print("- 'clear': Reset conversation history")
            print("- 'help': Show this help message")
            print("- Ask normally for other queries\n")
            continue
            
        if user_input.lower() == 'clear':
            chat = model.start_chat(history=[])
            print("Conversation history cleared.")
            continue

        # Check for live data needs
        if needs_live_data(user_input):
            print("🔍 Searching for live information...")
            answer = search_google(user_input)
            print("\nGemini (Live Results):")
            print_with_typing(answer)
            continue

        # Get Gemini response
        print("💭 Thinking...", end='\r')
        response = chat.send_message(user_input)
        print(" " * 15, end='\r')  # Clear "Thinking" message
        print("\nGemini:")
        print_with_typing(response.text)
        
    except Exception as e:
        print(f"\n⚠️ An error occurred: {e}")
        print("Please try again or rephrase your question.\n")