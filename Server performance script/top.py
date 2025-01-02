import paramiko
import time
import csv
import os  # Import os module to handle directories
from datetime import datetime
import re
from concurrent.futures import ThreadPoolExecutor

def monitor_top(ip, username, password, duration):
    try:
        # Establish SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, 22, username, password)

        # Open an interactive shell session
        channel = ssh.invoke_shell()
        time.sleep(1)  # Allow time for the shell to initialize
        
        # Start the 'top' command
        channel.send("top -b -d 1\n")  # Run top in batch mode with 1-second intervals
        time.sleep(2)  # Allow time for initial output

        # Create a directory named after the IP if it doesn't exist
        ip_folder = f"./{ip}"
        os.makedirs(ip_folder, exist_ok=True)  # Create the folder if it doesn't exist

        # Create a unique CSV file with a timestamp in the name, inside the IP folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(ip_folder, f"top_monitor_{ip}_{timestamp}.csv")
        
        with open(filename, mode='w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["Timestamp", "IP", "Load Avg (1m)", "Load Avg (5m)", "Load Avg (15m)", "User", "PID", "RES", "%CPU", "%MEM"])  # Write header row
            
            print(f"Logging output for {ip} to {filename}")
            print(f"Monitoring 'java' processes owned by 'tomcat' on {ip}...")

            start_time = time.time()
            
            while time.time() - start_time < duration:
                # Read a chunk of the output
                if channel.recv_ready():
                    output = channel.recv(65536).decode("utf-8")
                    
                    # Extract load average from the header line
                    header_match = re.search(r"load average: ([0-9.]+), ([0-9.]+), ([0-9.]+)", output)
                    load_avg_1m, load_avg_5m, load_avg_15m = header_match.groups() if header_match else ("N/A", "N/A", "N/A")
                    
                    # Parse lines containing the 'java' command and user 'tomcat'
                    for line in output.splitlines():
                        if re.search(r"\btomcat\b", line) and re.search(r"\bjava\b", line):
                            columns = line.split()
                            if len(columns) > 9:  # Ensure line is complete
                                user = columns[0]
                                pid = columns[1]
                                res = columns[5]  # RES
                                cpu = columns[8]  # %CPU
                                mem = columns[9]  # %MEM
                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                
                                # Log to CSV
                                csvwriter.writerow([timestamp, ip, load_avg_1m, load_avg_5m, load_avg_15m, user, pid, res, cpu, mem])
                                
                                # Print to console (optional)
                                print(f"Timestamp: {timestamp}, IP: {ip}, Load Avg: {load_avg_1m}, {load_avg_5m}, {load_avg_15m}, User: {user}, PID: {pid}, RES: {res}, %CPU: {cpu}, %MEM: {mem}")
                
                time.sleep(1)

        print(f"Monitoring for {ip} completed. Output logged to {filename}.")
        
    except Exception as e:
        print(f"An error occurred on {ip}: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    try:
        # Take input for multiple IPs, username, password, and duration
        ips = input("Enter the IP addresses of the servers (comma-separated): ").strip().split(',')
        username = input("Enter the SSH username: ").strip()
        password = input("Enter the SSH password: ").strip()
        duration = int(input("Enter the duration to monitor (in seconds): "))

        # Remove whitespace from IPs and start monitoring each server concurrently
        print("\nStarting monitoring for all servers simultaneously...\n")
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(monitor_top, ip.strip(), username, password, duration) for ip in ips]
            for future in futures:
                future.result()  # Wait for all tasks to complete

    except ValueError:
        print("Invalid input. Please enter a valid duration.")
    except KeyboardInterrupt:
        print("\nScript terminated by user.")
