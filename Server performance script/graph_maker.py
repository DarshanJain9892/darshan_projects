import pandas as pd
import matplotlib.pyplot as plt
import os
import warnings

# Ignore specific warnings
warnings.filterwarnings("ignore", message="invalid escape sequence '\\s'")
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)

# File path (update if necessary)
file_path = 'top_monitor_10.151.110.84_20241209_172309.csv'  # Replace with the actual file path if different

# Generate image file name dynamically
output_image = os.path.splitext(file_path)[0] + '.png'

# Read the CSV file
try:
    data = pd.read_csv(file_path)
except Exception as e:
    print(f"Error reading the file: {e}")
    exit()

# Copy the relevant columns
data_filtered = data[['Timestamp', 'Load Avg (15m)', 'RES', '%CPU', '%MEM']]

# Convert 'Timestamp' to a datetime object
try:
    data_filtered.loc[:, 'Timestamp'] = pd.to_datetime(data_filtered['Timestamp'])
except Exception as e:
    print(f"Error converting 'Timestamp' column to datetime: {e}")
    exit()

# Convert 'RES' to numeric (handle units like 'g', 'm', 'k', etc.)
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

# Apply the conversion to the 'RES' column
data_filtered.loc[:, 'RES'] = data_filtered['RES'].apply(convert_res_to_mb)

# Drop rows with missing or invalid data
data_filtered.dropna(inplace=True)

# Plot each parameter
plt.figure(figsize=(14, 10))  # Increased figure size for better visualization

# Plot 1: Load Avg (15m)
plt.subplot(2, 2, 1)
plt.plot(data_filtered['Timestamp'], data_filtered['Load Avg (15m)'], label='Load Avg (15m)', color='blue', linewidth=1.5)
plt.xlabel('Time')
plt.ylabel('Load Avg (15m)')
plt.title('Load Avg (15m) vs Time')
plt.xticks(rotation=30, ha='right')  # Rotate for better readability
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()

# Plot 2: RES (in MB)
plt.subplot(2, 2, 2)
plt.plot(data_filtered['Timestamp'], data_filtered['RES'], label='RES (MB)', color='orange', linewidth=1.5)
plt.xlabel('Time')
plt.ylabel('RES (MB)')
plt.title('RES (MB) vs Time')
plt.xticks(rotation=30, ha='right')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()

# Plot 3: %CPU
plt.subplot(2, 2, 3)
plt.plot(data_filtered['Timestamp'], data_filtered['%CPU'], label='%CPU', color='green', linewidth=1.5)
plt.xlabel('Time')
plt.ylabel('%CPU')
plt.title('%CPU vs Time')
plt.xticks(rotation=30, ha='right')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()

# Plot 4: %MEM
plt.subplot(2, 2, 4)
plt.plot(data_filtered['Timestamp'], data_filtered['%MEM'], label='%MEM', color='red', linewidth=1.5)
plt.xlabel('Time')
plt.ylabel('%MEM')
plt.title('%MEM vs Time')
plt.xticks(rotation=30, ha='right')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()

# Adjust layout to prevent overlap
plt.tight_layout()

# Save the plot instead of showing it
plt.savefig(output_image, dpi=300)  # Save the plot as a high-resolution image
print(f"Plot saved as '{output_image}'")
