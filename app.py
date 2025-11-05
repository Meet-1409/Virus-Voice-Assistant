import pyttsx3
import speech_recognition as sr
import datetime
import pyjokes
import time as time_module
import json
import os
import threading
import subprocess
import platform
import psutil
import random
import math

# Initialize TTS engine once
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
engine.setProperty('rate', 165)
engine.setProperty('volume', 1.0)

# File paths for data storage
REMINDERS_FILE = "virus_reminders.json"
ALARMS_FILE = "virus_alarms.json"
NOTES_FILE = "virus_notes.txt"
CONTACTS_FILE = "virus_contacts.json"
TODO_FILE = "virus_todo.json"

# Initialize data storage
def load_data(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except:
            return [] if filename != CONTACTS_FILE else {}
    return [] if filename != CONTACTS_FILE else {}

def save_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

reminders = load_data(REMINDERS_FILE)
alarms = load_data(ALARMS_FILE)
contacts = load_data(CONTACTS_FILE)
todos = load_data(TODO_FILE)
timers = []

def speech_to_text():
    """Convert speech to text"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nListening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("Processing...")
            data = recognizer.recognize_google(audio)
            print(f"You said: {data}")
            return data.lower()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"API error: {e}")
            return ""
        except Exception as e:
            print(f"Error: {e}")
            return ""

def text_to_speech(text):
    """Convert text to speech"""
    print(f"\nVirus: {text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except:
        pass

def get_current_time():
    """Get current time"""
    now = datetime.datetime.now()
    current_time = now.strftime("%I:%M %p")
    text_to_speech(f"The current time is {current_time}")

def get_current_date():
    """Get current date"""
    now = datetime.datetime.now()
    current_date = now.strftime("%A, %B %d, %Y")
    text_to_speech(f"Today is {current_date}")

def set_timer(seconds, label="Timer"):
    """Set a countdown timer"""
    def timer_thread():
        print(f"\nTimer started: {label} for {seconds} seconds")
        time_module.sleep(seconds)
        print(f"\n\n*** TIMER ALERT: {label} is up! ***\n")
        text_to_speech(f"Timer alert! {label} is up!")
        for _ in range(3):
            print("\a")
            time_module.sleep(0.5)
    
    thread = threading.Thread(target=timer_thread, daemon=True)
    thread.start()
    timers.append({"label": label, "seconds": seconds})
    text_to_speech(f"{label} set for {seconds} seconds")

def set_alarm(alarm_time, label="Alarm"):
    """Set an alarm for specific time"""
    alarm_data = {"time": alarm_time, "label": label, "active": True}
    alarms.append(alarm_data)
    save_data(ALARMS_FILE, alarms)
    text_to_speech(f"Alarm set for {alarm_time}")
    
    def alarm_thread():
        while alarm_data["active"]:
            current_time = datetime.datetime.now().strftime("%H:%M")
            if current_time == alarm_time:
                print(f"\n\n*** ALARM RINGING: {label} ***\n")
                text_to_speech(f"Alarm! {label}! It's {alarm_time}")
                for _ in range(5):
                    print("\a")
                    time_module.sleep(1)
                alarm_data["active"] = False
                break
            time_module.sleep(30)
    
    thread = threading.Thread(target=alarm_thread, daemon=True)
    thread.start()

def add_reminder(reminder_text, remind_time=None):
    """Add a reminder"""
    reminder = {
        "text": reminder_text,
        "time": remind_time if remind_time else datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "completed": False
    }
    reminders.append(reminder)
    save_data(REMINDERS_FILE, reminders)
    text_to_speech(f"Reminder added: {reminder_text}")

def show_reminders():
    """Show all active reminders"""
    active_reminders = [r for r in reminders if not r.get("completed", False)]
    if not active_reminders:
        text_to_speech("You have no active reminders")
        return
    
    print("\n--- Your Reminders ---")
    text_to_speech(f"You have {len(active_reminders)} reminder{'s' if len(active_reminders) != 1 else ''}")
    for idx, reminder in enumerate(active_reminders, 1):
        print(f"{idx}. {reminder['text']} - Created: {reminder['created']}")
        text_to_speech(f"Reminder {idx}: {reminder['text']}")

def add_todo(task):
    """Add a task to todo list"""
    todo = {
        "task": task,
        "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "completed": False
    }
    todos.append(todo)
    save_data(TODO_FILE, todos)
    text_to_speech(f"Added to your to-do list: {task}")

def show_todos():
    """Show all todos"""
    active_todos = [t for t in todos if not t.get("completed", False)]
    if not active_todos:
        text_to_speech("Your to-do list is empty")
        return
    
    print("\n--- Your To-Do List ---")
    text_to_speech(f"You have {len(active_todos)} task{'s' if len(active_todos) != 1 else ''}")
    for idx, todo in enumerate(active_todos, 1):
        print(f"{idx}. {todo['task']}")
        text_to_speech(f"Task {idx}: {todo['task']}")

def take_note(note_text):
    """Take a quick note"""
    with open(NOTES_FILE, "a", encoding='utf-8') as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {note_text}\n")
    text_to_speech("Note saved successfully")

def read_notes():
    """Read saved notes"""
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r", encoding='utf-8') as f:
            notes = f.readlines()
            if notes:
                print("\n--- Your Recent Notes ---")
                text_to_speech(f"You have {len(notes)} note{'s' if len(notes) != 1 else ''}")
                for note in notes[-5:]:
                    print(note.strip())
            else:
                text_to_speech("You have no notes")
    else:
        text_to_speech("You have no notes")

def add_contact(name, number):
    """Add a contact"""
    contacts[name.lower()] = number
    save_data(CONTACTS_FILE, contacts)
    text_to_speech(f"Contact {name} added with number {number}")

def get_contact(name):
    """Get a contact"""
    name_lower = name.lower()
    if name_lower in contacts:
        number = contacts[name_lower]
        print(f"\n{name}: {number}")
        text_to_speech(f"{name}'s number is {number}")
    else:
        text_to_speech(f"I couldn't find {name} in your contacts")

def list_contacts():
    """List all contacts"""
    if not contacts:
        text_to_speech("Your contact list is empty")
        return
    
    print("\n--- Your Contacts ---")
    text_to_speech(f"You have {len(contacts)} contact{'s' if len(contacts) != 1 else ''}")
    for name, number in contacts.items():
        print(f"{name.title()}: {number}")

def calculate(expression):
    """Perform calculations"""
    try:
        expression = expression.replace("plus", "+").replace("minus", "-")
        expression = expression.replace("times", "*").replace("multiply", "*").replace("multiplied by", "*")
        expression = expression.replace("divided by", "/").replace("divide", "/")
        expression = expression.replace("power", "**").replace("to the power of", "**")
        expression = expression.replace("squared", "**2").replace("cubed", "**3")
        expression = expression.replace("square root of", "math.sqrt(").replace("sqrt", "math.sqrt(")
        
        if "sqrt" in expression or "math.sqrt" in expression:
            expression = expression.replace("math.sqrt(", "math.sqrt(") + ")" if expression.count("(") > expression.count(")") else expression
        
        result = eval(expression, {"__builtins__": {}, "math": math})
        print(f"\nCalculation: {expression}")
        print(f"Result: {result}")
        text_to_speech(f"The answer is {result}")
        return result
    except Exception as e:
        text_to_speech("Sorry, I couldn't calculate that")
        return None

def convert_units(value, from_unit, to_unit):
    """Convert between units"""
    conversions = {
        ("celsius", "fahrenheit"): lambda x: (x * 9/5) + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
        ("kilometers", "miles"): lambda x: x * 0.621371,
        ("miles", "kilometers"): lambda x: x * 1.60934,
        ("meters", "feet"): lambda x: x * 3.28084,
        ("feet", "meters"): lambda x: x * 0.3048,
        ("kilograms", "pounds"): lambda x: x * 2.20462,
        ("pounds", "kilograms"): lambda x: x * 0.453592,
    }
    
    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        result = conversions[key](value)
        text_to_speech(f"{value} {from_unit} is {result:.2f} {to_unit}")
        print(f"{value} {from_unit} = {result:.2f} {to_unit}")
    else:
        text_to_speech(f"Sorry, I can't convert from {from_unit} to {to_unit}")

def get_system_info():
    """Get system information"""
    info = {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "CPU Usage": f"{psutil.cpu_percent(interval=1)}%",
        "Memory Usage": f"{psutil.virtual_memory().percent}%",
        "Battery": f"{psutil.sensors_battery().percent}%" if psutil.sensors_battery() else "Not Available"
    }
    
    print("\n--- System Information ---")
    for key, value in info.items():
        print(f"{key}: {value}")
    
    text_to_speech(f"Your system is running {info['OS']} with {info['CPU Usage']} CPU usage and {info['Memory Usage']} memory usage")

def open_application(app_name):
    """Open applications on PC"""
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "command prompt": "cmd.exe",
        "file explorer": "explorer.exe",
        "task manager": "taskmgr.exe",
        "control panel": "control.exe",
        "settings": "ms-settings:",
        "browser": "start chrome" if platform.system() == "Windows" else "open -a 'Google Chrome'",
    }
    
    app_name_lower = app_name.lower()
    if app_name_lower in apps:
        try:
            if platform.system() == "Windows":
                subprocess.Popen(apps[app_name_lower], shell=True)
            else:
                os.system(apps[app_name_lower])
            text_to_speech(f"Opening {app_name}")
        except Exception as e:
            text_to_speech(f"Sorry, I couldn't open {app_name}")
    else:
        text_to_speech(f"I don't know how to open {app_name}")

def get_weather_info():
    """Get weather information"""
    text_to_speech("Weather information requires internet API. In command prompt mode, I can tell you to check your weather app or provide temperature conversions if you tell me the temperature.")

def get_definitions(word):
    """Get word definitions"""
    print(f"\n--- Definition of '{word}' ---")
    text_to_speech(f"In command prompt mode, I cannot fetch live definitions. Please use a dictionary app or tell me to search online.")

def flip_coin():
    """Flip a coin"""
    result = random.choice(["Heads", "Tails"])
    text_to_speech(f"The coin landed on {result}")
    print(f"\nCoin Flip Result: {result}")

def roll_dice(sides=6):
    """Roll a dice"""
    result = random.randint(1, sides)
    text_to_speech(f"You rolled a {result}")
    print(f"\nDice Roll: {result} (out of {sides})")

def tell_joke():
    """Tell a joke"""
    joke = pyjokes.get_joke(language="en", category="neutral")
    print(f"\n{joke}")
    text_to_speech(joke)

def create_meeting(title, time_str):
    """Create a meeting/event"""
    meeting = {
        "title": title,
        "time": time_str,
        "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    meetings_file = "virus_meetings.json"
    meetings = load_data(meetings_file)
    meetings.append(meeting)
    save_data(meetings_file, meetings)
    text_to_speech(f"Meeting '{title}' scheduled for {time_str}")

def process_command(command):
    """Process voice commands"""
    if not command:
        return True
    
    # Greetings
    if any(word in command for word in ["hello", "hi", "hey virus", "hey"]):
        greetings = [
            "Hello! How can I help you?",
            "Hi there! What can I do for you?",
            "Hey! I'm Virus, your PC assistant. What do you need?",
            "Hello! Ready to assist you."
        ]
        text_to_speech(random.choice(greetings))
    
    # Identity
    elif "your name" in command or "who are you" in command:
        text_to_speech("I am Virus, your personal voice assistant for PC. I can help you with tasks, reminders, calculations, system information, and much more!")
    
    elif "what can you do" in command or "help" in command or "your features" in command:
        help_text = """
I am Virus, your PC assistant. I can:
- Tell time and date
- Set timers, alarms, and reminders
- Manage your to-do list
- Take and read notes
- Manage contacts
- Perform calculations and unit conversions
- Open applications
- Get system information
- Tell jokes
- Flip coins and roll dice
- Create meetings
- And much more!
"""
        print(help_text)
        text_to_speech("I can do many things like manage your schedule, take notes, perform calculations, open applications, tell you system information, and help you stay organized. Just ask me!")
    
    # Time and Date
    elif "time" in command and "timer" not in command:
        get_current_time()
    
    elif "date" in command or "what day" in command or "today" in command:
        get_current_date()
    
    # Timer
    elif "timer" in command or "set a timer" in command:
        try:
            if "minute" in command:
                mins = int(''.join([c for c in command.split("minute")[0].split()[-1] if c.isdigit()]))
                set_timer(mins * 60, f"{mins} minute timer")
            elif "second" in command:
                secs = int(''.join([c for c in command.split("second")[0].split()[-1] if c.isdigit()]))
                set_timer(secs, f"{secs} second timer")
            elif "hour" in command:
                hrs = int(''.join([c for c in command.split("hour")[0].split()[-1] if c.isdigit()]))
                set_timer(hrs * 3600, f"{hrs} hour timer")
            else:
                text_to_speech("Please specify the timer duration, like 5 minutes or 30 seconds")
        except:
            text_to_speech("I couldn't understand the timer duration. Please try again.")
    
    # Alarm
    elif "alarm" in command or "wake me" in command:
        text_to_speech("What time should I set the alarm for? Say it in 24-hour format, like 07 30")
        alarm_input = speech_to_text()
        if alarm_input:
            try:
                digits = ''.join([c for c in alarm_input if c.isdigit() or c == ':'])
                if len(digits) >= 4:
                    if ':' not in digits:
                        alarm_time = f"{digits[:2]}:{digits[2:4]}"
                    else:
                        alarm_time = digits[:5]
                    set_alarm(alarm_time, "Wake up alarm")
                else:
                    text_to_speech("Invalid time format")
            except:
                text_to_speech("I couldn't set the alarm")
    
    # Reminders
    elif "remind" in command:
        if "show" in command or "list" in command or "what are" in command:
            show_reminders()
        else:
            text_to_speech("What should I remind you about?")
            reminder_text = speech_to_text()
            if reminder_text:
                add_reminder(reminder_text)
    
    # To-Do List
    elif "todo" in command or "to do" in command or "task" in command:
        if "add" in command or "new" in command or "create" in command:
            text_to_speech("What task should I add?")
            task = speech_to_text()
            if task:
                add_todo(task)
        elif "show" in command or "list" in command or "what" in command:
            show_todos()
        else:
            text_to_speech("What task should I add to your to-do list?")
            task = speech_to_text()
            if task:
                add_todo(task)
    
    # Notes
    elif "note" in command or "write this down" in command:
        if "read" in command or "show" in command or "my notes" in command:
            read_notes()
        else:
            text_to_speech("What should I note down?")
            note = speech_to_text()
            if note:
                take_note(note)
    
    # Contacts
    elif "contact" in command:
        if "add" in command or "new" in command or "save" in command:
            text_to_speech("What is the contact name?")
            name = speech_to_text()
            if name:
                text_to_speech("What is the phone number?")
                number = speech_to_text()
                if number:
                    add_contact(name, number)
        elif "show" in command or "list" in command or "all" in command:
            list_contacts()
        elif "find" in command or "get" in command or "call" in command:
            contact_name = command.replace("contact", "").replace("find", "").replace("get", "").replace("call", "").strip()
            if contact_name:
                get_contact(contact_name)
            else:
                text_to_speech("Which contact do you want?")
                name = speech_to_text()
                if name:
                    get_contact(name)
    
    # Calculations
    elif any(word in command for word in ["calculate", "what is", "plus", "minus", "times", "divided", "multiply"]):
        expression = command.replace("calculate", "").replace("what is", "").replace("what's", "").strip()
        if expression:
            calculate(expression)
    
    # Unit Conversion
    elif "convert" in command:
        try:
            parts = command.replace("convert", "").strip().split()
            value = float(parts[0])
            from_unit = parts[1]
            to_unit = parts[3] if "to" in parts else parts[-1]
            convert_units(value, from_unit, to_unit)
        except:
            text_to_speech("Please say convert followed by value, unit, to, and target unit")
    
    # System Info
    elif "system" in command or "battery" in command or "cpu" in command or "memory" in command:
        get_system_info()
    
    # Open Applications
    elif "open" in command:
        app = command.replace("open", "").strip()
        if app:
            open_application(app)
        else:
            text_to_speech("Which application should I open?")
    
    # Weather
    elif "weather" in command:
        get_weather_info()
    
    # Definition
    elif "define" in command or "definition" in command or "meaning of" in command:
        word = command.replace("define", "").replace("definition", "").replace("meaning of", "").strip()
        if word:
            get_definitions(word)
    
    # Fun Features
    elif "flip a coin" in command or "coin flip" in command:
        flip_coin()
    
    elif "roll a dice" in command or "roll dice" in command or "dice roll" in command:
        if "sided" in command:
            try:
                sides = int(''.join([c for c in command.split("sided")[0].split()[-1] if c.isdigit()]))
                roll_dice(sides)
            except:
                roll_dice()
        else:
            roll_dice()
    
    elif "joke" in command or "make me laugh" in command or "tell me a joke" in command:
        tell_joke()
    
    # Meeting
    elif "meeting" in command or "schedule" in command:
        text_to_speech("What is the meeting title?")
        title = speech_to_text()
        if title:
            text_to_speech("When is the meeting?")
            meeting_time = speech_to_text()
            if meeting_time:
                create_meeting(title, meeting_time)
    
    # Exit
    elif "exit" in command or "quit" in command or "bye" in command or "goodbye" in command or "stop" in command:
        text_to_speech("Goodbye! Have a great day!")
        return False
    
    # Unknown
    else:
        responses = [
            "I'm not sure about that. Try asking me something else.",
            "I didn't quite get that. Could you rephrase?",
            "I'm still learning. Try saying 'help' to see what I can do.",
            "Sorry, I don't understand that command yet."
        ]
        text_to_speech(random.choice(responses))
    
    return True

def main():
    """Main function"""
    print("=" * 70)
    print(" " * 20 + "VIRUS - PC Voice Assistant")
    print("=" * 70)
    print("\nWelcome! I'm Virus, your personal PC assistant.")
    print("Say 'help' to learn what I can do.")
    print("Say 'exit' to quit.")
    print("=" * 70)
    
    text_to_speech("Hello! I am Virus, your personal voice assistant for PC. How can I help you today?")
    
    while True:
        try:
            command = speech_to_text()
            if command and not process_command(command):
                break
        except KeyboardInterrupt:
            text_to_speech("Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            text_to_speech("Sorry, I encountered an error")

if __name__ == '__main__':
    main()
