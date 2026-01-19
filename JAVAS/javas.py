import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import json
import random
import os
import datetime
import webbrowser
import wikipedia
import requests
import speech_recognition as sr
import pyttsx3

# --- CONFIGURATION & INITIALIZATION ---

class Assistant:
    """Main class for the voice assistant's backend logic."""
    def __init__(self):
        try:
            with open('config.json') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print("Error: config.json not found. Please create it.")
            exit()

        self.engine = pyttsx3.init('sapi5')
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id) # Index 0 for male, 1 for female

        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1
        self.recognizer.energy_threshold = 300 # Adjust if needed for your mic

        self.gui = None # Will be set by the GUI class

    def set_gui(self, gui_instance):
        """Link the backend to the GUI instance for updates."""
        self.gui = gui_instance

    def speak(self, text):
        """Convert text to speech and update the GUI."""
        if self.gui:
            self.gui.update_output(f"Aura: {text}\n")
            self.gui.update_status(f"Speaking...")
        self.engine.say(text)
        self.engine.runAndWait()
        if self.gui:
            self.gui.update_status("Idle")

    def listen(self, is_wake_word=False):
        """Listen for audio input and recognize it as text."""
        with sr.Microphone() as source:
            if not is_wake_word and self.gui:
                self.gui.update_status("Listening...")
            
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = self.recognizer.listen(source)

        try:
            if self.gui:
                self.gui.update_status("Processing...")
            command = str(self.recognizer.recognize_amazon(audio)).lower()
            if self.gui and not is_wake_word:
                self.gui.update_output(f"You: {command}\n")
            return command
        except sr.UnknownValueError:
            if not is_wake_word:
                self.speak("Sorry, I didn't catch that. Please try again.")
            return None
        except sr.RequestError:
            self.speak("Sorry, my speech service is down.")
            return None
            
# --- COMMAND FUNCTIONS ---

def get_time(assistant):
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    assistant.speak(f"The current time is {current_time}.")

def get_date(assistant):
    current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
    assistant.speak(f"Today is {current_date}.")

def greet_user(assistant):
    hour = datetime.datetime.now().hour
    user_name = assistant.config.get('user_name', 'User')
    if 0 <= hour < 12:
        greeting = f"Good morning, {user_name}!"
    elif 12 <= hour < 18:
        greeting = f"Good afternoon, {user_name}!"
    else:
        greeting = f"Good evening, {user_name}!"
    assistant.speak(f"{greeting} I am Aura. How can I help you today?")

def search_wikipedia(assistant):
    assistant.speak("What topic would you like me to search for on Wikipedia?")
    query = assistant.listen()
    if query:
        try:
            assistant.speak(f"Searching Wikipedia for {query}...")
            results = wikipedia.summary(query, sentences=2)
            assistant.speak("According to Wikipedia:")
            assistant.speak(results)
        except wikipedia.exceptions.PageError:
            assistant.speak(f"Sorry, I couldn't find a Wikipedia page for {query}.")
        except wikipedia.exceptions.DisambiguationError:
            assistant.speak(f"That term is ambiguous. Please be more specific.")

def open_website(assistant, site_name, url):
    webbrowser.open(url)
    assistant.speak(f"Opening {site_name}.")

def search_google(assistant):
    assistant.speak("What would you like me to search for on Google?")
    query = assistant.listen()
    if query:
        webbrowser.open(f"https://www.google.com/search?q={query}")
        assistant.speak(f"Here are the search results for {query}.")

def play_music(assistant):
    music_dir = assistant.config.get("music_directory")
    if music_dir and os.path.isdir(music_dir):
        songs = [s for s in os.listdir(music_dir) if s.endswith(('.mp3', '.wav', '.flac'))]
        if songs:
            random_song = random.choice(songs)
            os.startfile(os.path.join(music_dir, random_song))
            assistant.speak(f"Now playing {random_song.split('.')[0]}.")
        else:
            assistant.speak("I couldn't find any music files in your music folder.")
    else:
        assistant.speak("The music directory path in your config file is invalid or not set.")

def get_weather(assistant):
    api_key = assistant.config.get("weather_api_key")
    city = assistant.config.get("city")
    if not api_key or api_key == "YOUR_OPENWEATHERMAP_API_KEY":
        assistant.speak("Please set your OpenWeatherMap API key in the config file.")
        return
    if not city:
        assistant.speak("Please set your city in the config file.")
        return

    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(base_url)
        data = response.json()
        if data["cod"] == 200:
            main = data["main"]
            weather_desc = data["weather"][0]["description"]
            temp = main["temp"]
            feels_like = main["feels_like"]
            assistant.speak(f"The weather in {city} is currently {weather_desc}.")
            assistant.speak(f"The temperature is {temp}° Celsius, but it feels like {feels_like}° Celsius.")
        else:
            assistant.speak("Sorry, I couldn't retrieve the weather information.")
    except requests.ConnectionError:
        assistant.speak("I couldn't connect to the weather service.")

def tell_joke(assistant):
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "I told my wife she was drawing her eyebrows too high. She looked surprised.",
        "What do you call a fish wearing a bowtie? Sofishticated.",
    ]
    assistant.speak(random.choice(jokes))
    
def system_shutdown(assistant, action="shutdown"):
    action_word = "shut down" if action == "shutdown" else "restart"
    assistant.speak(f"Are you sure you want to {action_word} the computer?")
    confirmation = assistant.listen()
    if confirmation and "yes" in confirmation:
        assistant.speak(f"{action.capitalize()}ing the system now. Goodbye!")
        if action == "shutdown":
            os.system("shutdown /s /t 1")
        else:
            os.system("shutdown /r /t 1")
    else:
        assistant.speak("Operation cancelled.")


# --- COMMAND REGISTRY ---

COMMANDS = {
    "time": get_time,
    "date": get_date,
    "wikipedia": search_wikipedia,
    "open youtube": lambda assistant: open_website(assistant, "YouTube", "https://www.youtube.com"),
    "open google": lambda assistant: open_website(assistant, "Google", "https://www.google.com"),
    "search": search_google,
    "play music": play_music,
    "weather": get_weather,
    "joke": tell_joke,
    "shut down": lambda assistant: system_shutdown(assistant, "shutdown"),
    "restart": lambda assistant: system_shutdown(assistant, "restart")
}

# --- MAIN APPLICATION LOGIC ---

class AuraAssistantGUI(tk.Tk):
    """Main class for the GUI using tkinter."""
    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant
        self.assistant.set_gui(self)
        
        self.title("Aura Virtual Assistant")
        self.geometry("700x500")
        
        self.style = ttk.Style(self)
        self.style.theme_use('clam') # Other themes: 'alt', 'default', 'classic'

        # Main frame
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        self.title_label = ttk.Label(self.main_frame, text="Aura - Your Virtual Assistant", font=("Helvetica", 18, "bold"))
        self.title_label.pack(pady=10)

        # Output box
        self.output_box = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, font=("Helvetica", 12), state='disabled')
        self.output_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Status bar
        self.status_label = ttk.Label(self.main_frame, text="Status: Idle", font=("Helvetica", 10))
        self.status_label.pack(fill=tk.X, padx=10, pady=5)

        # Button frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=10)
        
        # --- THREADING CONTROL ---
        self.listening_thread = None
        self.is_listening = False
        self.stop_listening_event = threading.Event()

        # Buttons
        self.listen_button = ttk.Button(self.button_frame, text="▶️ Start Listening", command=self.toggle_listening)
        self.listen_button.grid(row=0, column=0, padx=10)

        self.exit_button = ttk.Button(self.button_frame, text="❌ Exit", command=self.close_app)
        self.exit_button.grid(row=0, column=1, padx=10)
        
        self.protocol("WM_DELETE_WINDOW", self.close_app)

        # Initial greeting in a separate thread
        threading.Thread(target=lambda: greet_user(self.assistant), daemon=True).start()

    def update_output(self, text):
        """Thread-safe method to update the output box."""
        self.output_box.configure(state='normal')
        self.output_box.insert(tk.END, text)
        self.output_box.yview(tk.END)
        self.output_box.configure(state='disabled')

    def update_status(self, text):
        """Thread-safe method to update the status bar."""
        self.status_label.config(text=f"Status: {text}")

    def execute_command_from_thread(self, command):
        """Executes a command based on the registered commands."""
        if not command:
            return
            
        if 'exit' in command or 'stop' in command:
            self.close_app()
            return
        
        for key in COMMANDS:
            if key in command:
                COMMANDS[key](self.assistant)
                return
        self.assistant.speak("I'm not sure how to handle that command.")

    def continuous_listen_loop(self):
        """The main loop for background wake word listening."""
        wake_word = self.assistant.config.get("wake_word", "aura")
        while not self.stop_listening_event.is_set():
            command = self.assistant.listen(is_wake_word=True)
            if command and wake_word in command:
                self.assistant.speak("Yes?")
                task_command = self.assistant.listen()
                if task_command:
                    # Offload the command execution to another thread to keep listening responsive
                    threading.Thread(target=self.execute_command_from_thread, args=(task_command,), daemon=True).start()

    def toggle_listening(self):
        """Starts or stops the background listening thread."""
        if not self.is_listening:
            self.is_listening = True
            self.listen_button.config(text="⏹️ Stop Listening")
            self.update_status("Listening for wake word...")
            self.stop_listening_event.clear()
            self.listening_thread = threading.Thread(target=self.continuous_listen_loop, daemon=True)
            self.listening_thread.start()
        else:
            self.is_listening = False
            self.listen_button.config(text="▶️ Start Listening")
            self.update_status("Idle")
            self.stop_listening_event.set()
            if self.listening_thread:
                self.listening_thread.join(timeout=1)

    def close_app(self):
        """Gracefully closes the application."""
        self.assistant.speak("Goodbye!")
        self.stop_listening_event.set()
        self.destroy()

if __name__ == "__main__":
    assistant_backend = Assistant()
    app = AuraAssistantGUI(assistant_backend)
    app.mainloop()