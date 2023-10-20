from collections import defaultdict
from tabulate import tabulate
from datetime import datetime, timedelta
import argparse
 
# Initialize a dictionary to store durations grouped by target
target_durations = defaultdict(list)
 
# Specify the file path
file_path = "ping_probe_data.txt"
 
# Define the time duration (e.g., "15m" for 15 minutes, "1hr" for 1 hour, "24hr" for 24 hours) as a command-line argument
parser = argparse.ArgumentParser(description="Calculate percentiles for ping durations within a specified time window.")
parser.add_argument("duration", type=str, help="Time duration (e.g., '15m', '1hr', '24hr')")
args = parser.parse_args()
 
# Calculate the cutoff time based on the specified duration
if args.duration.endswith("m"):
    minutes = int(args.duration[:-1])
    cutoff_time = datetime.now() - timedelta(minutes=minutes)
elif args.duration.endswith("hr"):
    hours = int(args.duration[:-2])
    cutoff_time = datetime.now() - timedelta(hours=hours)
else:
    print("Invalid duration format. Use '15m' for minutes, '1hr' for hours, or '24hr' for 24 hours.")
    exit(1)
 
# Open and read the file
with open(file_path, "r") as file:
    data = file.readlines()
 
# Extract duration_seconds values and group by target within the specified duration
for line in data:
    if "duration_seconds=" in line:
        timestamp_str = line.split("ts=")[1].split(" ")[0]
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        if timestamp >= cutoff_time:
            target = line.split("target=")[1].split(" ")[0]
            duration_str = line.split("duration_seconds=")[1]
            try:
                duration = float(duration_str)
                duration_ms = duration * 1000  # Convert to milliseconds
                target_durations[target].append(duration_ms)
            except ValueError:
                print(f"Skipping invalid duration value: {duration_str}")
 
# Prepare data for tabulation
table_data = []
for target, durations_ms in target_durations.items():
    if durations_ms:
        # Sort the durations in ascending order
        sorted_durations_ms = sorted(durations_ms)
 
        # Calculate the indices for P50, P90, and P99
        p50_index = int(0.5 * len(sorted_durations_ms))
        p90_index = int(0.9 * len(sorted_durations_ms))
        p99_index = int(0.99 * len(sorted_durations_ms))
 
        # Retrieve the values at the specified percentiles
        p50_value_ms = sorted_durations_ms[p50_index]
        p90_value_ms = sorted_durations_ms[p90_index]
        p99_value_ms = sorted_durations_ms[p99_index]
 
        table_data.append([target, f"{p50_value_ms:.2f}ms", f"{p90_value_ms:.2f}ms", f"{p99_value_ms:.2f}ms"])
    else:
        table_data.append([target, "N/A", "N/A", "N/A"])
 
# Define the table headers
headers = ["Target", "P50", "P90", "P99"]
 
# Print the ASCII table
table = tabulate(table_data, headers, tablefmt="grid")
print(table)
