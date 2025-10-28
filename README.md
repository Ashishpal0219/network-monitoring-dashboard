# Network & System Monitoring Dashboard

This is a Python-based monitoring dashboard built with Streamlit. It's designed for technical support trainees or IT enthusiasts to monitor a local system and network in real-time. It provides live metrics, network tools (ping, port scan), and logs all data to a local SQLite database for historical analysis.

## Features

* **Live System Monitoring**: Real-time charts and metrics for CPU, Memory, and Disk usage.
* **Network Tools**:
    * **Ping Utility**: Send ICMP requests to any host or IP to check latency and reachability.
    * **Port Scanner**: Scan specified ports on a target host to see which are open.
* **Database Logging**: All monitoring results (system, ping, ports) are automatically logged to a local `network_monitor.db` SQLite database.
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

**1. Clone the Repository (or create the files):**
If this were on GitHub, you'd clone it. For now, create a folder named `network_monitor` and add all the files from this project (`app.py`, `monitoring.py`, etc.) into it.

**2. Create a Virtual Environment:**
It's highly recommended to use a virtual environment.

```bash
# Navigate into your project folder
cd network_monitor

# Create a virtual environment
python -m venv venv

# Activate the environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate