import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from collections import defaultdict
import os
import argparse
import json

parser = argparse.ArgumentParser(description='Generate monitoring report for client servers.')
parser.add_argument('--client_ips', type=str, help='Comma-separated list of client server IPs')
args = parser.parse_args()

# Configuration
LOKI_URL = "http://localhost:3100"
PROMETHEUS_URL = "http://localhost:9090"
#CLIENT_SERVERS = args.client_ips.split(',') if args.client_ips else [] #CLIENT_SERVERS = ["209.97.134.226:9100", "142.93.38.159:9100"]
REPORT_DURATION = timedelta(days=7) 
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ServerReports")

CLIENT_IPS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_ips.json')

def load_client_ips():
    if os.path.exists(CLIENT_IPS_FILE):
        with open(CLIENT_IPS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_client_ips(ips):
    with open(CLIENT_IPS_FILE, 'w') as f:
        json.dump(ips, f)

parser = argparse.ArgumentParser(description='Generate monitoring report for client servers.')
parser.add_argument('--client_ips', type=str, help='Comma-separated list of client server IPs')
args = parser.parse_args()

if args.client_ips:
    CLIENT_SERVERS = args.client_ips.split(',')
    # Ensure each IP ends with :9100
    CLIENT_SERVERS = [ip if ip.endswith(':9100') else f"{ip}:9100" for ip in CLIENT_SERVERS]
    save_client_ips(CLIENT_SERVERS)
else:
    CLIENT_SERVERS = load_client_ips()


# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Metrics configuration
METRICS = {
    "cpu_usage": {
        "query": '100 - (avg by(instance) (rate(node_cpu_seconds_total{{instance="{}",mode="idle"}}[5m])) * 100)',
        "unit": "%",
        "title": "CPU Usage"
    },
    "memory_usage": {
        "query": '(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100',
        "unit": "%",
        "title": "Memory Usage"
    },
    "disk_space_usage": {
        "query": '100 - ((node_filesystem_avail_bytes{{mountpoint="/"}} * 100) / node_filesystem_size_bytes{{mountpoint="/"}})',
        "unit": "%",
        "title": "Disk Space Usage"
    },
    "disk_io": {
        "query": 'rate(node_disk_io_time_seconds_total[5m])',
        "unit": "ops/sec",
        "title": "Disk I/O"
    },
    # new
    #"network_throughput_percentage": {
    #"query": '100 * (sum by(instance) (rate(node_network_transmit_bytes_total[5m]) + rate(node_network_receive_bytes_total[5m]))) / sum(node_network_speed_bytes)',
    #"unit": "%",
    #"title": "Network Throughput Percentage"
    #},
    # new
    "network_throughput_percentage": {
        "query": """
    100 * 
    sum(rate(node_network_transmit_bytes_total[5m]) + rate(node_network_receive_bytes_total[5m])) 
    / 
    scalar(sum(node_network_speed_bytes))
    """,
        "unit": "%",
        "title": "Network Throughput Percentage"
    },
    #new
    "network_throughput": {
        "query": '(sum by(instance) (rate(node_network_transmit_bytes_total[5m]) + rate(node_network_receive_bytes_total[5m]))) / 1024 / 1024',
        "unit": "MB/s",
        "title": "Network Throughput"
    },
    "network_error_rate": {
        "query": '(sum by(instance) (rate(node_network_transmit_errs_total[5m]) + rate(node_network_receive_errs_total[5m]))) / (sum by(instance) (rate(node_network_transmit_packets_total[5m]) + rate(node_network_receive_packets_total[5m]))) * 100',
        "unit": "%",
        "title": "Network Error Rate"
    },
    "service_availability": {
        "query": '100 - 100 * avg(up{{instance="{}"}})',
        "unit": "%",
        "title": "Service Availability (All Jobs)"
    },
    "response_time": {
        "query": 'avg(avg_over_time(scrape_duration_seconds{{instance="{}"}}[5m]))',
        "unit": "seconds",
        "title": "Average Response Time (All Jobs)"
    }
}

def query_prometheus(query, start_time, end_time):
    url = f"{PROMETHEUS_URL}/api/v1/query_range"
    params = {
        'query': query,
        'start': start_time.isoformat("T") + "Z",
        'end': end_time.isoformat("T") + "Z",
        'step': '5m'  # 5-minute resolution for longer periods
    }
    response = requests.get(url, params=params)
    return response.json()

def query_loki(query, start_time, end_time):
    url = f"{LOKI_URL}/loki/api/v1/query_range"
    params = {
        'query': query,
        'start': start_time.isoformat("T") + "Z",
        'end': end_time.isoformat("T") + "Z",
        'limit': 1000  # Increased limit
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error querying Loki: {response.status_code} - {response.text}")
    return response.json()

def plot_metric(df, metric_name, server, unit):
    plt.figure(figsize=(16, 8))
    df['value'].plot(linewidth=0.5)
    plt.title(f"{METRICS[metric_name]['title']} for {server} over {REPORT_DURATION}")
    plt.ylabel(f"{METRICS[metric_name]['title']} ({unit})")
    plt.xlabel("Time")
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Highlight max points
    max_points = get_spaced_max_values(df, 5, timedelta(hours=24))
    plt.scatter(max_points.index, max_points['value'], color='red', zorder=5, label='Top 5 Max Values (24h apart)')
    
    for idx, row in max_points.iterrows():
        plt.annotate(f"{row['value']:.3f}", (idx, row['value']), textcoords="offset points", xytext=(0,10), ha='center')

    plt.legend()
    plt.tight_layout()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{server.replace(':', '_')}_{metric_name}_{timestamp}.png"
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300)
    plt.close()

def get_spaced_max_values(df, n=5, min_interval=timedelta(hours=24)):
    max_values = []
    last_timestamp = df.index.min() - min_interval
    sorted_df = df.sort_values('value', ascending=False)
    
    for idx, row in sorted_df.iterrows():
        if idx - last_timestamp >= min_interval:
            max_values.append(row)
            last_timestamp = idx
        if len(max_values) == n:
            break
    
    return pd.DataFrame(max_values)

def get_alert_periods(df, alert_threshold):
    df['alert'] = df['value'] > alert_threshold
    alert_periods = []
    alert_start = None
    for index, row in df.iterrows():
        if row['alert'] and alert_start is None:
            alert_start = index
        elif not row['alert'] and alert_start is not None:
            alert_periods.append((alert_start, index, df.loc[alert_start:index, 'value'].max()))
            alert_start = None
    if alert_start is not None:
        alert_periods.append((alert_start, df.index[-1], df.loc[alert_start:, 'value'].max()))
    return alert_periods

#def query_alerts(start_time, end_time):
#    query = 'ALERTS{alertstate="firing"}'
#    return query_prometheus(query, start_time, end_time)

def query_alerts(start_time, end_time):
    query = 'ALERTS{alertstate="firing"}'
    # Use a step size that matches the alert evaluation interval
    step = '15s'  # Assuming the alert evaluation interval is 15 seconds
    url = f"{PROMETHEUS_URL}/api/v1/query_range"
    params = {
        'query': query,
        'start': start_time.isoformat("T") + "Z",
        'end': end_time.isoformat("T") + "Z",
        'step': step
    }
    response = requests.get(url, params=params)
    return response.json()

def format_timestamp(timestamp):
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')

def process_alerts(alert_data):
    alert_occurrences = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for result in alert_data['data']['result']:
        alert_name = result['metric']['alertname']
        severity = result['metric'].get('severity', 'unknown')
        
        for timestamp, value in result['values']:
            if float(value) == 1:  # Alert is firing
                date = datetime.fromtimestamp(timestamp).date()
                alert_occurrences[alert_name][date][severity] += 1
    
    return alert_occurrences

from datetime import datetime, timedelta

def test_full_network_query(server, start_time, end_time):
    # Test individual components
    transmit_query = f'sum(rate(node_network_transmit_bytes_total{{instance="{server}"}}[5m]))'
    receive_query = f'sum(rate(node_network_receive_bytes_total{{instance="{server}"}}[5m]))'
    speed_query = f'sum(node_network_speed_bytes{{instance="{server}"}})'

    transmit_data = query_prometheus(transmit_query, start_time, end_time)
    receive_data = query_prometheus(receive_query, start_time, end_time)
    speed_data = query_prometheus(speed_query, start_time, end_time)

    print(f"Detailed network query diagnosis for {server}:")

    speed_value = None
    if speed_data['data']['result']:
        try:
            # Extract the most recent speed value
            speed_value = float(speed_data['data']['result'][0]['values'][-1][1])
            print(f"  - node_network_speed_bytes value: {speed_value}")
            if speed_value == 0:
                print("    Warning: Speed is zero, this will cause division by zero in the full query.")
        except (IndexError, KeyError, ValueError) as e:
            print(f"  - Error extracting node_network_speed_bytes value: {str(e)}")
    else:
        print("  - node_network_speed_bytes data is missing.")

    if transmit_data['data']['result'] and receive_data['data']['result'] and speed_data['data']['result']:
        print("  All required metrics are present. Testing full query...")
        
        full_query = f'100 * (sum by(instance) (rate(node_network_transmit_bytes_total{{instance="{server}"}}[5m]) + rate(node_network_receive_bytes_total{{instance="{server}"}}[5m]))) / sum(node_network_speed_bytes{{instance="{server}"}})'
        full_data = query_prometheus(full_query, start_time, end_time)
        
        if full_data['data']['result']:
            print("  Full query returned data successfully.")
            print(f"  Result: {full_data['data']['result']}")
        else:
            print("  Full query returned no data despite all metrics being present.")
            print("  This could be due to:")
            if speed_value == 0:
                print("    - Division by zero (node_network_speed_bytes is zero)")
            elif speed_value is None:
                print("    - Unable to determine node_network_speed_bytes value")
            else:
                print("    - No data points within the specified time range")
            print(f"  Time range: {start_time} to {end_time}")
    else:
        print("  Full query was not tested due to missing metrics.")

    print("\nRaw data from Prometheus:")
    print(f"Transmit data: {transmit_data}")
    print(f"Receive data: {receive_data}")
    print(f"Speed data: {speed_data}")

    print("\nCalculated network usage:")
    try:
        latest_transmit = float(transmit_data['data']['result'][0]['values'][-1][1])
        latest_receive = float(receive_data['data']['result'][0]['values'][-1][1])
        total_usage = latest_transmit + latest_receive
        if speed_value and speed_value > 0:
            usage_percentage = (total_usage / speed_value) * 100
            print(f"  Current network usage: {usage_percentage:.2f}%")
            print(f"  Total usage: {total_usage:.2f} bytes/s")
            print(f"  Network speed: {speed_value:.2f} bytes/s")
        else:
            print(f"  Total usage: {total_usage:.2f} bytes/s")
            print("  Unable to calculate usage percentage due to missing or invalid speed data")
    except Exception as e:
        print(f"  Error calculating network usage: {str(e)}")

    print("\nTime range check:")
    current_time = datetime.now()
    if start_time > current_time or end_time > current_time:
        print("  Warning: The specified time range includes future dates.")
        print(f"  Current time: {current_time}")
        print(f"  Query start time: {start_time}")
        print(f"  Query end time: {end_time}")
    else:
        print("  Time range appears to be valid.")


def generate_report(server):
    end_time = datetime.now()
    start_time = end_time - REPORT_DURATION
    timestamp = end_time.strftime("%Y%m%d_%H%M%S")

    print(f"Generating report for {server}")

    report_filename = f"{server.replace(':', '_')}_report_{timestamp}.txt"
    with open(os.path.join(OUTPUT_DIR, report_filename), "w") as f:
        f.write(f"Report for {server}\n")
        f.write(f"Duration: {REPORT_DURATION}\n")
        f.write(f"From: {start_time} To: {end_time}\n\n")

        for metric_name, metric_info in METRICS.items():
            query = metric_info['query'].format(server) # this was changed because of network speed metric
            #query = metric_info['query'].replace('$instance', server)
            data = query_prometheus(query, start_time, end_time)

            if not data['data']['result']:
                f.write(f"No {metric_info['title']} data available. Check if the server is reachable and exporting metrics.\n\n")
                continue

            # Call this function to check if the network throughput speed is up to par
            #test_full_network_query(server, start_time, end_time)

            df = pd.DataFrame(data['data']['result'][0]['values'], columns=['timestamp', 'value'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df.set_index('timestamp', inplace=True)
            df['value'] = df['value'].astype(float)

            avg_value = df['value'].mean()
            max_value = df['value'].max()

            f.write(f"{metric_info['title']}:\n")
            f.write(f"Average: {avg_value:.3f} {metric_info['unit']}\n")
            f.write(f"Maximum: {max_value:.3f} {metric_info['unit']}\n")

            spaced_max_values = get_spaced_max_values(df, 5, timedelta(hours=24))
            f.write("Top 5 Maximum Values (at least 24 hours apart):\n")
            for idx, row in spaced_max_values.iterrows():
                f.write(f"  {format_timestamp(idx)}: {row['value']:.3f} {metric_info['unit']}\n")

            alert_threshold = 70 if metric_name == 'network_throughput_percentage' else 0.01 if metric_name == 'network_error_rate' else 1 if metric_name == 'service_availability' else 2 if metric_name == 'response_time' else 80 
            alert_periods = get_alert_periods(df, alert_threshold)
            if alert_periods:
                f.write(f"Alert Periods (threshold: {alert_threshold} {metric_info['unit']}):\n")
                for start, end, max_val in alert_periods:
                    f.write(f"  {format_timestamp(start)} to {format_timestamp(end)}: Max value {max_val:.3f} {metric_info['unit']}\n")
            else:
                f.write(f"No alerts triggered (threshold: {alert_threshold} {metric_info['unit']})\n")

            f.write("\n")

            plot_metric(df, metric_name, server, metric_info['unit'])

        # Query and process alerts
        alert_data = query_alerts(start_time, end_time)
        alert_occurrences = process_alerts(alert_data)
        
        f.write("Alert Summary:\n")
        for alert_name, dates in alert_occurrences.items():
            total_occurrences = sum(sum(severities.values()) for severities in dates.values())
            total_critical = sum(severities.get('critical', 0) for severities in dates.values())
            total_warning = sum(severities.get('warning', 0) for severities in dates.values())
            
            f.write(f"  {alert_name}:\n")
            f.write(f"    Total Occurrences: {total_occurrences}")
            if total_critical > 0:
                f.write(f", {total_critical} critical")
            if total_warning > 0:
                f.write(f", {total_warning} warning")
            f.write("\n")
            
            f.write("    Triggered on: ")
            triggered_days = []
            for date, severities in sorted(dates.items()):
                day_total = sum(severities.values())
                severity = 'critical' if severities.get('critical', 0) > 0 else 'warning'
                triggered_days.append(f"{date} ({severity}, {day_total})")
            f.write(", ".join(triggered_days))
            f.write("\n\n")
        """
        # Add specific reporting for ServiceAvailabilityAlert and ResponseTimeAlert
        if 'ServiceAvailabilityAlert' in alert_occurrences:
            f.write("  Service Availability Alerts:\n")
            for date, severities in sorted(alert_occurrences['ServiceAvailabilityAlert'].items()):
                for severity, count in severities.items():
                    f.write(f"    {date} - {severity.capitalize()}: {count} occurrences\n")
            f.write("\n")

        if 'ResponseTimeAlert' in alert_occurrences:
            f.write("  Response Time Alerts:\n")
            for date, severities in sorted(alert_occurrences['ResponseTimeAlert'].items()):
                for severity, count in severities.items():
                    f.write(f"    {date} - {severity.capitalize()}: {count} occurrences\n")
            f.write("\n")
        """

        # Query logs
        log_query = '{job =~".+"}'
        log_data = query_loki(log_query, start_time, end_time)

        f.write("Logs:\n")
        if 'result' in log_data['data'] and log_data['data']['result']:
            for stream in log_data['data']['result']:
                for value in stream['values']:
                    timestamp = datetime.fromtimestamp(float(value[0]) / 1e9).isoformat()
                    log_entry = value[1]
                    f.write(f"{timestamp} - {log_entry}\n")
        else:
            f.write("No logs found for this period.\n")

    print(f"Report generated for {server}")

if __name__ == "__main__":
    if not CLIENT_SERVERS:
        print("No client IPs found. Please run the script with --client_ips argument to set the IPs.")
    else:
        for server in CLIENT_SERVERS:
            generate_report(server)
        print("All reports generated.")
        
"""
# Generate reports for each server
for server in CLIENT_SERVERS:
    generate_report(server)

print("All reports generated.")
"""
