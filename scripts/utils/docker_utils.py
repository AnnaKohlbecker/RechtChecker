import subprocess
import time
import psutil

# List of required container names
REQUIRED_CONTAINERS = [
    "rechtchecker-mongodb-1",
    "rechtchecker-timescaledb-1",
    "rechtchecker-neo4j-1",
    "rechtchecker-minio-1",
    "rechtchecker-redis-1",
]

def is_docker_desktop_running():
    """Check if Docker Desktop process is running."""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'Docker Desktop.exe':
            return True
    return False

def get_running_containers():
    """Get the list of running container names."""
    try:
        result = subprocess.run("docker ps --format '{{.Names}}'", shell=True, check=True, text=True, capture_output=True)
        running_containers = result.stdout.strip().split('\n')
        # Clean up container names to ensure accurate comparison
        return [container.strip().strip("'") for container in running_containers if container.strip()]
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while checking running containers: {e.stderr}")
        return []

def start_docker_desktop():
    """Start Docker Desktop."""
    try:
        print("Starting Docker Desktop...")
        subprocess.run("""start "" "C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe""", shell=True, check=True)
        time.sleep(50)
    except subprocess.CalledProcessError as e:
        print(f"Error starting Docker Desktop: {e.stderr}")

def start_docker_services():
    """Start Docker services using docker-compose."""
    commands = [
        "docker-compose down -v",
        "docker-compose up -d"
    ]
    for command in commands:
        try:
            subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
            time.sleep(10)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while executing '{command}': {e.stderr}")
        except FileNotFoundError:
            print(f"Command not found or not executable: '{command}'")

def verify_containers():
    """Verify if all required containers are running."""
    running_containers = get_running_containers()
    missing_containers = [container for container in REQUIRED_CONTAINERS if container not in running_containers]
    
    if missing_containers:
        print("Starting missing containers...")
        start_docker_services()
    
    running_containers = get_running_containers()
    print("Running containers:", running_containers)

def start_docker():
    if not is_docker_desktop_running():
        start_docker_desktop()
    else:
        print("Docker Desktop is running.")
    verify_containers()
    print("Docker and containers initialized.")
