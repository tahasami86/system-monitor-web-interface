#!/usr/bin/python3
import sqlite3
import html
from datetime import datetime
import random  # For generating random CPU temperature

# Path to your SQLite database
DB_PATH = "/var/www/system_monitoring.db"

# CGI Header
print("Content-type: text/html\n")

try:
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch the last 10 entries
    cursor.execute("SELECT * FROM system_data ORDER BY timestamp DESC LIMIT 10")
    rows = cursor.fetchall()

    # Generate HTML
    print("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>System Monitoring Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; background-color: #f4f4f4; }
            h1 { color: #333; text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
            table { width: 100%; border-collapse: collapse; background-color: white; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            th { background-color: #007bff; color: white; padding: 12px; text-align: left; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            tr:hover { background-color: #e6e6e6; }
            td { padding: 10px; border-bottom: 1px solid #ddd; }
        </style>
    </head>
    <body>
        <h1> System Monitoring Dashboard</h1>
        <table>
            <tr>
                <th>ID</th>
                <th>Timestamp</th>
                <th>CPU Usage (%)</th>
                <th>Memory Usage (%)</th>
                <th>Disk Usage (%)</th>
                <th>Read Bytes</th>
                <th>Write Bytes</th>
                <th>Bytes Sent</th>
                <th>Bytes Received</th>
                <th>CPU Temp</th>
                <th>System Info</th>
            </tr>
    """)

    # Print rows
    for row in rows:
        print("<tr>")
        for idx, cell in enumerate(row):
            # Format Timestamp as a more readable date
            if idx == 1:
                formatted_date = datetime.strptime(cell, "%Y-%m-%d %H:%M:%S").strftime("%b %d, %Y %I:%M %p")
                print(f"<td>{html.escape(formatted_date)}</td>")
            # Convert bytes to human-readable format
            elif isinstance(cell, str) and ('MB' in cell or 'GB' in cell or 'KB' in cell or 'B' in cell):
                print(f"<td>{html.escape(cell)}</td>")
            # Handle None values for missing data
            elif cell is None:
                print("<td>N/A</td>")
            # Display system info dictionary as a formatted string
            elif idx == 10:
                sys_info = eval(cell) if isinstance(cell, str) else {}
                formatted_info = "<br>".join([f"<b>{key}</b>: {value}" for key, value in sys_info.items()])
                print(f"<td>{formatted_info}</td>")
            else:
                print(f"<td>{html.escape(str(cell))}</td>")
        print("</tr>")

    print("""
        </table>
    </body>
    </html>
    """)

except sqlite3.Error as e:
    print(f"Database Error: {html.escape(str(e))}")
except Exception as e:
    print(f"Error: {html.escape(str(e))}")
finally:
    # Close database connection if it was opened
    if 'conn' in locals():
        conn.close()
