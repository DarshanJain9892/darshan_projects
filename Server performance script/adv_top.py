import paramiko
import time
import csv
import os
from datetime import datetime
import re
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore", message="invalid escape sequence '\\s'")
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)

def convert_res_to_mb(value):
    """Convert RES values like '6.9g' to MB."""
    if isinstance(value, str):
        if 'g' in value.lower():
            return float(value.lower().replace('g', '')) * 1024  # GB to MB
        elif 'm' in value.lower():
            return float(value.lower().replace('m', ''))  # MB as is
        elif 'k' in value.lower():
            return float(value.lower().replace('k', '')) / 1024  # KB to MB
    try:
        return float(value)
    except ValueError:
        return None

def generate_graph(file_path):
    """Generate graphs from the CSV data."""
    try:
        data = pd.read_csv(file_path)
        data_filtered = data[['Timestamp', 'Load Avg (15m)', 'RES', '%CPU', '%MEM']]
        data_filtered.loc[:, 'Timestamp'] = pd.to_datetime(data_filtered['Timestamp'])
        data_filtered.loc[:, 'RES'] = data_filtered['RES'].apply(convert_res_to_mb)
        data_filtered.dropna(inplace=True)

        output_image = os.path.splitext(file_path)[0] + '.png'
        plt.figure(figsize=(14, 10))

        plt.subplot(2, 2, 1)
        plt.plot(data_filtered['Timestamp'], data_filtered['Load Avg (15m)'], label='Load Avg (15m)', color='blue', linewidth=1.5)
        plt.xlabel('Time')
        plt.ylabel('Load Avg (15m)')
        plt.title('Load Avg (15m) vs Time')
        plt.xticks(rotation=30, ha='right')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()

        plt.subplot(2, 2, 2)
        plt.plot(data_filtered['Timestamp'], data_filtered['RES'], label='RES (MB)', color='orange', linewidth=1.5)
        plt.xlabel('Time')
        plt.ylabel('RES (MB)')
        plt.title('RES (MB) vs Time')
        plt.xticks(rotation=30, ha='right')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()

        plt.subplot(2, 2, 3)
        plt.plot(data_filtered['Timestamp'], data_filtered['%CPU'], label='%CPU', color='green', linewidth=1.5)
        plt.xlabel('Time')
        plt.ylabel('%CPU')
        plt.title('%CPU vs Time')
        plt.xticks(rotation=30, ha='right')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()

        plt.subplot(2, 2, 4)
        plt.plot(data_filtered['Timestamp'], data_filtered['%MEM'], label='%MEM', color='red', linewidth=1.5)
        plt.xlabel('Time')
        plt.ylabel('%MEM')
        plt.title('%MEM vs Time')
        plt.xticks(rotation=30, ha='right')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()

        plt.tight_layout()
        plt.savefig(output_image, dpi=300)
        print(f"Graph generated and saved as '{output_image}'")
    except Exception as e:
        print(f"Error generating graph: {e}")

def monitor_top(ip, username, password, duration):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, 22, username, password)
        channel = ssh.invoke_shell()
        time.sleep(1)
        channel.send("top -b -d 1\n")
        time.sleep(2)

        ip_folder = f"./{ip}"
        os.makedirs(ip_folder, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(ip_folder, f"top_monitor_{ip}_{timestamp}.csv")
        
        with open(filename, mode='w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["Timestamp", "IP", "Load Avg (1m)", "Load Avg (5m)", "Load Avg (15m)", "User", "PID", "RES", "%CPU", "%MEM"])

            start_time = time.time()
            while time.time() - start_time < duration:
                if channel.recv_ready():
                    output = channel.recv(65536).decode("utf-8")
                    header_match = re.search(r"load average: ([0-9.]+), ([0-9.]+), ([0-9.]+)", output)
                    load_avg_1m, load_avg_5m, load_avg_15m = header_match.groups() if header_match else ("N/A", "N/A", "N/A")
                    
                    for line in output.splitlines():
                        if re.search(r"\btomcat\b", line) and re.search(r"\bjava\b", line):
                            columns = line.split()
                            if len(columns) > 9:
                                user = columns[0]
                                pid = columns[1]
                                res = columns[5]
                                cpu = columns[8]
                                mem = columns[9]
                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                csvwriter.writerow([timestamp, ip, load_avg_1m, load_avg_5m, load_avg_15m, user, pid, res, cpu, mem])
                time.sleep(1)

        print(f"Monitoring for {ip} completed. Output logged to {filename}.")
        generate_graph(filename)
        
    except Exception as e:
        print(f"An error occurred on {ip}: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    try:
        ips = input("Enter the IP addresses of the servers (comma-separated): ").strip().split(',')
        username = input("Enter the SSH username: ").strip()
        password = input("Enter the SSH password: ").strip()
        duration = int(input("Enter the duration to monitor (in seconds): "))

        print("\nStarting monitoring for all servers simultaneously...\n")
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(monitor_top, ip.strip(), username, password, duration) for ip in ips]
            for future in futures:
                future.result()
    except ValueError:
        print("Invalid input. Please enter a valid duration.")
    except KeyboardInterrupt:
        print("\nScript terminated by user.")
