import paramiko
import csv
import configparser
import re
import os
from datetime import datetime

# SSH credentials
USERNAME = 'darshan.jain'
PASSWORD = 'kuBlynk7'

# Output directory
OUTPUT_DIR = 'output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_sha_id(ssh, tomcat_name, application_folder):
    try:
        command = f"cat /opt/{tomcat_name}/webapps/{application_folder}/WEB-INF/classes/git-revision"
        stdin, stdout, stderr = ssh.exec_command(command)
        sha_id_output = stdout.read().decode().strip()
        sha_id = sha_id_output.split(':')[-1].strip() if ':' in sha_id_output else 'Not-Found'
    except Exception as e:
        sha_id = f"Error: {e}"
    return sha_id

def get_config_url(ssh):
    try:
        command = "cat /sms/config.properties | grep config.url"
        stdin, stdout, stderr = ssh.exec_command(command)
        config_output = stdout.read().decode().strip()
        match = re.search(r"config.url=.*?//(.*)", config_output)
        config_url = match.group(1) if match else 'Not-Found'
    except Exception as e:
        config_url = f"Error: {e}"
    return config_url

def get_top_info(ssh):
    try:
        # Get number of CPU cores
        stdin, stdout, stderr = ssh.exec_command("nproc")
        cores = stdout.read().decode().strip()

        # Get memory details
        stdin, stdout, stderr = ssh.exec_command("free -m")
        free_output = stdout.read().decode().strip()
        mem_info = re.search(r"Mem:\s+(\d+)\s+(\d+)\s+(\d+)", free_output)

        if mem_info:
            total_mem, used_mem, free_mem = mem_info.groups()
        else:
            total_mem, used_mem, free_mem = 'N/A', 'N/A', 'N/A'

    except Exception as e:
        cores = 'Error'
        total_mem, used_mem, free_mem = 'Error', 'Error', 'Error'

    return cores, total_mem, used_mem, free_mem

def check_tomcats(ip):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ip, username=USERNAME, password=PASSWORD)
        ssh_status = 'ssh passed'

        # Get config URL
        config_url = get_config_url(ssh)

        # Get top info
        cores, total_mem, used_mem, free_mem = get_top_info(ssh)

        # List Tomcats under /opt
        stdin, stdout, stderr = ssh.exec_command("ls /opt | grep -v '^tomcat\*$' | grep tomcat")
        tomcat_dirs = stdout.read().decode().strip().splitlines()

        tomcat_info = []
        if tomcat_dirs:
            for tomcat_name in tomcat_dirs:
                # Check if Tomcat is running
                stdin, stdout, stderr = ssh.exec_command(f"ps -ef | grep {tomcat_name} | grep -v grep")
                output = stdout.read().decode().strip()
                status = 'UP' if output else 'DOWN'

                # Get list of .war files in webapps
                stdin, stdout, stderr = ssh.exec_command(f"ls /opt/{tomcat_name}/webapps/*.war 2>/dev/null")
                war_files = stdout.read().decode().strip().splitlines()
                application_names = [file.split('/')[-1].replace('.war', '') for file in war_files]

                for app in application_names:
                    sha_id = get_sha_id(ssh, tomcat_name, app)
                    tomcat_info.append((tomcat_name, status, app, sha_id, cores, total_mem, used_mem, free_mem, config_url))
        else:
            tomcat_info = [('No-Tomcats-found', 'N/A', 'N/A', 'N/A', cores, total_mem, used_mem, free_mem, config_url)]

        ssh.close()
    except Exception as e:
        ssh_status = 'ssh failed'
        tomcat_info = [('N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A')]

    return ssh_status, tomcat_info

def main():
    # Prompt user for input method
    print("Choose an option to input IPs:")
    print("a) Config file")
    print("b) CSV file upload")
    print("c) Enter IPs manually")
    choice = input("Enter your choice (a/b/c): ").strip().lower()

    ips = []

    if choice == 'a':
        # Read IPs from config file
        CONFIG_FILE = 'config.ini'
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        ips = config['DEFAULT']['ips'].split(',')
    elif choice == 'b':
        # Upload CSV file and read IPs
        csv_file = input("Enter the path to the CSV file: ").strip()
        try:
            with open(csv_file, mode='r') as file:
                reader = csv.reader(file)
                ips = [row[0].strip() for row in reader if row]
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return
    elif choice == 'c':
        # Manually enter IPs
        ip_input = input("Enter the IPs, comma-separated: ").strip()
        ips = [ip.strip() for ip in ip_input.split(',')]
    else:
        print("Invalid choice. Exiting.")
        return

    # Generate unique output file name
    date_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"config_report_{date_time}.csv")

    print(f"Creating output file: {output_file}")

    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Server_No', 'IP', 'ssh', 'SSH_Status', 'Tomcat_Name', 'Tomcat_Status', 'Application_Name', 'SHA_ID', 'CPU_Cores', 'Mem_Total_MiB', 'Mem_Used_MiB', 'Mem_Free_MiB', 'Default_Config_URL'])

        server_no = 1
        for ip in ips:
            ip = ip.strip()
            print(f"Processing IP: {ip} (Server {server_no})")
            ssh_status, tomcat_info = check_tomcats(ip)
            print(f"Status for IP {ip}: {ssh_status}")
            for tomcat_name, tomcat_status, application_name, sha_id, cores, total_mem, used_mem, free_mem, config_url in tomcat_info:
                writer.writerow([server_no, ip, ssh_status, tomcat_name, tomcat_status, application_name, sha_id, cores, total_mem, used_mem, free_mem, config_url])
            server_no += 1

    print(f"Results written to {output_file}")

if __name__ == "__main__":
    main()
