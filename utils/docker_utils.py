import subprocess
import time

def start_docker():
    commands = [
        """start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe""",
        "docker-compose down -v",
        "docker-compose up -d",
        "docker ps",
    ]

    for command in commands:
        try:
            result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
            print(f"Command '{command}' executed successfully:\n{result.stdout}")
            time.sleep(30 if "Docker Desktop.exe" in command else 10)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while executing '{command}': {e.stderr}")
        except FileNotFoundError:
            print(f"Command not found or not executable: '{command}'")
