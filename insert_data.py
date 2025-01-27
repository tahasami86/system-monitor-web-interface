import sqlite3
import psutil
import time
import shutil  # For disk usage
import platform  # For system info
import subprocess  # Missing import for subprocess

# Path to your SQLite database
DB_PATH = "/var/www/system_monitoring.db"

def convert_bytes(bytes_value):
    """Convert bytes to a human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"  # If the size is extremely large, use PB

def get_system_temp():
    """Fetch system temperature using vcgencmd."""
    try:
        # Execute the vcgencmd command to get the temperature
        result = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True, text=True)
        if result.returncode == 0:
            temp_str = result.stdout.strip()  # Output example: "temp=58.0'C"
            temp = temp_str.split('=')[1].split("'")[0]  # Extract the numeric value
            return float(temp)
        else:
            return None
    except Exception as e:
        print(f"Error getting system temperature: {e}")
        return None

def get_system_info():
    """Fetch system information from /etc/os-release."""
    try:
        with open("/etc/os-release", "r") as file:
            os_info = file.readlines()
        os_data = {}
        for line in os_info:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                os_data[key] = value.strip('"')
        return os_data
    except Exception as e:
        print(f"Error getting system information: {e}")
        return None

def insert_system_data():
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get system metrics
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_usage = memory.percent

    # Disk usage
    disk_usage = shutil.disk_usage('/')
    disk_percent =  psutil.disk_usage('/').percent

    # Disk I/O
    disk_io = psutil.disk_io_counters()
    read_bytes = disk_io.read_bytes
    write_bytes = disk_io.write_bytes

    # Network usage
    net_io = psutil.net_io_counters()
    bytes_sent = net_io.bytes_sent
    bytes_recv = net_io.bytes_recv

    # Get system temperature and info
    cpu_temp = get_system_temp()
    system_info = get_system_info()

    # Temperature (if available)
    try:
        temp = psutil.sensors_temperatures()
        cpu_temp = temp.get('coretemp', [{}])[0].current if 'coretemp' in temp else None
    except Exception:
        cpu_temp = None

    # Convert byte values to human-readable format
    read_bytes = convert_bytes(read_bytes)
    write_bytes = convert_bytes(write_bytes)
    bytes_sent = convert_bytes(bytes_sent)
    bytes_recv = convert_bytes(bytes_recv)

    # Insert data into the database
    cursor.execute("""
        INSERT INTO system_data
        (cpu_usage, memory_usage, disk_usage, read_bytes, write_bytes, bytes_sent, bytes_recv, cpu_temp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (cpu_usage, memory_usage, disk_percent, read_bytes, write_bytes, bytes_sent, bytes_recv, cpu_temp))

    conn.commit()
    print(f"Inserted data - CPU: {cpu_usage}%, Memory: {memory_usage}%, Disk: {disk_percent}%, CPU_TEMP: {cpu_temp}")

    conn.close()

def main():
    try:
        while True:
            insert_system_data()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nMonitoring stopped gracefully.\n")

if __name__ == "__main__":
    main()
