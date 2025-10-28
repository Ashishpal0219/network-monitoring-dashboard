import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_NAME = "network_monitor.db"

def init_db():
    """Initializes the SQLite database and creates tables if they don't exist."""
    if os.path.exists(DB_NAME):
        return  # Database already exists

    print(f"Creating new database: {DB_NAME}")
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Table for system metrics
        cursor.execute('''
        CREATE TABLE system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            cpu_percent REAL NOT NULL,
            memory_percent REAL NOT NULL,
            disk_percent REAL NOT NULL
        )
        ''')

        # Table for ping results
        cursor.execute('''
        CREATE TABLE network_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            target TEXT NOT NULL,
            status TEXT NOT NULL,
            latency_ms REAL
        )
        ''')

        # Table for port scan results
        cursor.execute('''
        CREATE TABLE port_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            target TEXT NOT NULL,
            port INTEGER NOT NULL,
            status TEXT NOT NULL
        )
        ''')

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error during initialization: {e}")
    finally:
        if conn:
            conn.close()

def log_system_metrics(cpu, memory, disk):
    """Logs system metrics to the database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO system_logs (timestamp, cpu_percent, memory_percent, disk_percent) VALUES (?, ?, ?, ?)",
            (datetime.now(), cpu, memory, disk)
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error logging system metrics: {e}")
    finally:
        if conn:
            conn.close()

def log_ping_result(target, status, latency_ms):
    """Logs the result of a ping test."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO network_logs (timestamp, target, status, latency_ms) VALUES (?, ?, ?, ?)",
            (datetime.now(), target, status, latency_ms)
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error logging ping result: {e}")
    finally:
        if conn:
            conn.close()

def log_port_scan_results(target, open_ports, scanned_ports):
    """Logs the results of a port scan, one entry per port."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        timestamp = datetime.now()
        
        for port in scanned_ports:
            status = "Open" if port in open_ports else "Closed"
            cursor.execute(
                "INSERT INTO port_logs (timestamp, target, port, status) VALUES (?, ?, ?, ?)",
                (timestamp, target, port, status)
            )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error logging port scan: {e}")
    finally:
        if conn:
            conn.close()

def fetch_logs(table_name, limit=100):
    """Fetches the most recent logs from a specified table."""
    if table_name not in ["system_logs", "network_logs", "port_logs"]:
        return pd.DataFrame() # Return empty dataframe for invalid table

    try:
        conn = sqlite3.connect(DB_NAME)
        # Order by id DESC to get the *most recent* logs
        query = f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT {limit}"
        df = pd.read_sql_query(query, conn)
        
        # Reverse the dataframe so that charts plot time correctly (oldest to newest)
        df = df.iloc[::-1]

        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
        
        return df
    except sqlite3.Error as e:
        print(f"Database error fetching logs: {e}")
        return pd.DataFrame() # Return empty on error
    finally:
        if conn:
            conn.close()