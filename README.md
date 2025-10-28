# Network & System Monitoring Dashboard

This is a Python-based monitoring dashboard built with Streamlit. It's designed for IT enthusiasts or support trainees to monitor a local system and network in real-time. It provides live metrics, network tools (ping, port scan), an automatic uptime monitor, and logs all data to a local SQLite database for historical analysis.

## Features

* **Live System Monitoring**: Real-time charts and metrics for local CPU, Memory, and Disk (storage) usage.
* **Persistent Uptime Monitor**: Automatically pings a user-defined list of hosts (e.g., `8.8.8.8`, `192.168.1.1`) every 60 seconds to display their live 'Up'/'Down' status.
* **Network Tools**:
    * **Ping Utility**: Send ICMP requests to any host or IP to check latency and reachability.
    * **Port Scanner**: Scan specified ports on a target host to see which are open.
* **Database Logging**: All monitoring results (system, ping, ports, uptime) are automatically logged to a local `network_monitor.db` SQLite database.
* **Historical Analysis**: View and filter all logged data directly in the dashboard.
* **Report Exporting**: Export any log table to **CSV** or **DOCX** format for reporting.

## Tech Stack

* **Python**: 3.10+
* **Web Framework**: `streamlit`
* **System Metrics**: `psutil`
* **Network Ping**: `ping3`
* **Network Port Scan**: `socket` (Python standard library)
* **Database**: `sqlite3` (Python standard library)
* **Data Handling**: `pandas`
* **DOCX Export**: `python-docx`

## Setup & Installation

Follow these steps to get the project running on your local machine.

**1. Clone the Repository:**
Navigate to the directory where you want to store the project and clone the repository:

```bash
git clone [https://github.com/Ashishpal0219/network-monitoring-dashboard.git](https://github.com/Ashishpal0219/network-monitoring-dashboard.git)
cd network-monitoring-dashboard
2. Create a Virtual Environment: It's highly recommended to use a virtual environment.

Bash

# Create a virtual environment
python -m venv venv

# Activate the environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
3. Install Required Libraries: With your virtual environment active, install all dependencies from the requirements.txt file.

Bash

pip install -r requirements.txt
Usage
Once everything is installed, you can run the Streamlit application.

1. Run the App: In your terminal (from the network-monitoring-dashboard folder), run:

Bash

streamlit run app.py
2. View the Dashboard: Streamlit will automatically open a new tab in your web browser (usually http://localhost:8501).

Deployment on Streamlit Community Cloud
To deploy this app for free:

Push your code to your GitHub repository (which you have already done).

Sign up or log in to Streamlit Community Cloud.

Click "New app" and select your repository (network-monitoring-dashboard).

Ensure the "Main file path" is set to app.py.

Click "Deploy!".