import psutil
import time
from influxdb import InfluxDBClient

# InfluxDB Client configuration
client = InfluxDBClient(host='localhost', port=8086, database='system_monitoring')

def get_system_metrics():
    """
    Collects system metrics: CPU usage, memory utilization, and disk space.

    Returns:
        A dictionary containing the collected metrics.
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory()
    disk_usage = psutil.disk_usage('/')

    metrics = {
        'cpu_usage': cpu_percent,
        'memory_used': memory_usage.used,
        'memory_total': memory_usage.total,
        'disk_used': disk_usage.used,
        'disk_total': disk_usage.total
    }

    return metrics

def send_to_influxdb(metrics):
    """
    Sends the collected metrics to the InfluxDB database.

    Args:
        metrics: A dictionary containing the metrics to be sent.
    """
    json_body = [
        {
            "measurement": "system_metrics",
            "time": time.time_ns(),
            "fields": metrics
        }
    ]

    try:
        client.write_points(json_body)
        print("Data written to InfluxDB.")
    except Exception as e:
        print(f"Error writing to InfluxDB: {e}")

if __name__ == "__main__":
    try:
        while True:
            metrics = get_system_metrics()
            send_to_influxdb(metrics)
            time.sleep(10)  # Collect data every 10 seconds
    except KeyboardInterrupt:
        print("\nMonitoring stopped gracefully.")
