import streamlit as st
import pandas as pd
import time
import re
from datetime import datetime

# Import modular functions
import monitoring
import database
import reporting

# --- Page Configuration ---
st.set_page_config(
    page_title="Network Monitoring Dashboard",
    page_icon="🖥️",
    layout="wide"
)

# --- Database Initialization ---
# This runs once at the start of the script.
database.init_db()

# --- Helper Functions ---
def validate_ip(ip):
    """Rudimentary validation for IP or hostname."""
    if not ip:
        return False
    # Simple regex for hostnames/IPs. Not perfect, but good enough.
    pattern = re.compile(r"^[a-zA-Z0-9.-]+$")
    return pattern.match(ip)

def parse_ports(port_string):
    """Parses a comma-separated string of ports/port-ranges."""
    ports = set()
    if not port_string:
        st.error("Port string is empty.")
        return []
        
    parts = port_string.split(',')
    for part in parts:
        part = part.strip()
        try:
            if '-' in part:
                # Handle range
                start, end = part.split('-')
                start_port = int(start)
                end_port = int(end)
                if 0 < start_port <= end_port <= 65535:
                    ports.update(range(start_port, end_port + 1))
                else:
                    st.error(f"Invalid port range: {part}")
            else:
                # Handle single port
                port = int(part)
                if 0 < port <= 65535:
                    ports.add(port)
                else:
                    st.error(f"Invalid port number: {port}")
        except ValueError:
            st.error(f"Invalid port format: {part}")
    
    return sorted(list(ports))

# --- Application State ---
# Use session_state to store values that persist across reruns
if 'last_log_time' not in st.session_state:
    st.session_state.last_log_time = time.time()
if 'chart_data' not in st.session_state:
    st.session_state.chart_data = pd.DataFrame(columns=['timestamp', 'cpu', 'memory', 'disk']).set_index('timestamp')

# --- Main Application ---
st.title("🖥️ Network & System Monitoring Dashboard")
st.caption(f"A real-time monitoring tool. Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# ==============================================================================
# --- LIVE SYSTEM METRICS (as a self-updating fragment) ---
# ==============================================================================
@st.fragment(run_every=1)
def live_metrics_fragment():
    """
    This function creates the live metrics tab.
    The @st.fragment decorator tells Streamlit this section can
    update itself on a loop without reloading the whole page.
    """
    
    # We create the UI elements *inside* the fragment
    st.header("Live Local System Metrics")
    
    # Check for internet connection once (on first run)
    @st.cache_data
    def check_connection():
        return monitoring.check_internet_connection()

    if check_connection():
        st.success("✅ Internet Connection: **Online**")
    else:
        st.error("❌ Internet Connection: **Offline**")

    st.subheader("Real-time Usage")
    
    # Create placeholders for live metrics and chart
    kpi_cols = st.columns(3)
    cpu_kpi = kpi_cols[0].empty()
    mem_kpi = kpi_cols[1].empty()
    disk_kpi = kpi_cols[2].empty()
    
    chart_placeholder = st.empty()
    
    # 1. Get Metrics
    metrics = monitoring.get_system_metrics()
    
    # 2. Log to Database (every 10 seconds)
    current_time = time.time()
    if (current_time - st.session_state.last_log_time) > 10:
        database.log_system_metrics(metrics["cpu"], metrics["memory"], metrics["disk"])
        st.session_state.last_log_time = current_time

    # 3. Update Chart Data
    new_data = pd.DataFrame({
        'timestamp': [datetime.now()],
        'cpu': [metrics["cpu"]],
        'memory': [metrics["memory"]],
        'disk': [metrics["disk"]]
    }).set_index('timestamp')
    
    st.session_state.chart_data = pd.concat([st.session_state.chart_data, new_data])
    st.session_state.chart_data = st.session_state.chart_data.tail(50)

    # 4. Update UI Elements
    cpu_kpi.metric("CPU Usage", f"{metrics['cpu']:.1f} %")
    mem_kpi.metric("Memory Usage", f"{metrics['memory']:.1f} %")
    disk_kpi.metric("Disk Usage", f"{metrics['disk']:.1f} %")
    
    chart_placeholder.line_chart(st.session_state.chart_data)

# ==============================================================================
# --- CREATE TABS ---
# ==============================================================================

tab_live, tab_tools, tab_history, tab_uptime = st.tabs([
    "📊 Live System Metrics", 
    "🛠️ Network Tools", 
    "📈 Log History & Reports",
    "📡 Uptime Monitor"
])

# Call the fragment function in the first tab
with tab_live:
    live_metrics_fragment()


# ==============================================================================
# --- NETWORK TOOLS TAB --- 
# ==============================================================================
with tab_tools:
    st.header("Network Diagnostic Tools")
    
    tool_col1, tool_col2 = st.columns(2)
    
    # --- Ping Utility ---
    with tool_col1:
        st.subheader("Ping Utility")
        ping_target_host = st.text_input("Enter IP or Hostname to Ping", "8.8.8.8", key="ping_host")
        
        if st.button("Ping Target", use_container_width=True):
            if validate_ip(ping_target_host):
                with st.spinner(f"Pinging {ping_target_host}..."):
                    status, latency = monitoring.ping_target(ping_target_host)
                    
                    # Log the result
                    database.log_ping_result(ping_target_host, status, latency)
                    
                    # Display the result
                    if status == "Online":
                        st.success(f"**{ping_target_host}** is **{status}** (Latency: {latency} ms)")
                    elif status == "Host Unknown":
                        st.error(f"**{ping_target_host}**: **{status}**. Check the hostname.")
                    else:
                        st.warning(f"**{ping_target_host}** is **{status}** (Latency: N/A)")
            else:
                st.error("Invalid hostname or IP address.")

    # --- Port Scanner ---
    with tool_col2:
        st.subheader("Port Scanner")
        scan_target_host = st.text_input("Enter IP or Hostname to Scan", "127.0.0.1", key="scan_host")
        port_string = st.text_input("Ports (e.g., 22, 80, 443, 8000-8010)", "80, 443, 8080")
        
        if st.button("Scan Ports", use_container_width=True):
            if validate_ip(scan_target_host):
                ports_to_scan = parse_ports(port_string)
                if ports_to_scan:
                    with st.spinner(f"Scanning {len(ports_to_scan)} ports on {scan_target_host}..."):
                        open_ports = monitoring.scan_ports(scan_target_host, ports_to_scan)
                        
                        # Log the results
                        database.log_port_scan_results(scan_target_host, open_ports, ports_to_scan)
                        
                        # Display results
                        if open_ports:
                            st.success(f"Scan complete. Open ports: **{', '.join(map(str, open_ports))}**")
                        else:
                            st.info("Scan complete. No open ports found in the specified range.")
                        
                        # Show a small dataframe of results
                        scan_df = pd.DataFrame({
                            'Port': ports_to_scan,
                            'Status': ['Open' if p in open_ports else 'Closed' for p in ports_to_scan]
                        }).set_index('Port')
                        
                        # --- FIX for use_container_width ---
                        st.dataframe(scan_df, width='stretch')
            else:
                st.error("Invalid hostname or IP address.")


# ==============================================================================
# --- LOG HISTORY & REPORTS TAB ---
# ==============================================================================
with tab_history:
    st.header("Log History & Reporting")
    
    log_type = st.selectbox(
        "Select Log Type to View:",
        ("System Metrics", "Ping Results", "Port Scan Results"),
        key="log_select"
    )
    
    log_type_key = log_type.lower().replace(' ', '_')
    
    st.subheader(f"{log_type} Logs")
    
    df_logs = pd.DataFrame() # Initialize empty dataframe
    
    # 1. Fetch data from database
    if log_type == "System Metrics":
        df_logs = database.fetch_logs("system_logs", limit=200)
        if not df_logs.empty:
            st.line_chart(df_logs[['cpu_percent', 'memory_percent', 'disk_percent']])
            
    elif log_type == "Ping Results":
        df_logs = database.fetch_logs("network_logs", limit=100)
        
    elif log_type == "Port Scan Results":
        df_logs = database.fetch_logs("port_logs", limit=200)

    # 2. Display data in a table
    if not df_logs.empty:
        # --- FIX for use_container_width ---
        st.dataframe(df_logs, width='stretch')

        # 3. Exporting Section
        st.subheader("Export Current View")
        export_cols = st.columns(2)
        
        # --- CSV Export ---
        with export_cols[0]:
            csv_data = reporting.export_to_csv(df_logs)
            st.download_button(
                label="📥 Download as CSV",
                data=csv_data,
                file_name=f"{log_type.lower().replace(' ', '_')}_report.csv",
                mime="text/csv",
                use_container_width=True, 
                key=f"csv_download_{log_type_key}"  
            )
        
        # --- DOCX Export ---
        with export_cols[1]:
            docx_data = reporting.export_to_docx(df_logs, f"{log_type} Report")
            st.download_button(
                label="📄 Download as DOCX",
                data=docx_data,
                file_name=f"{log_type.lower().replace(' ', '_')}_report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                key=f"docx_download_{log_type_key}" 
            )
    else:
        st.info("No logs found for this category. Try running some tests in the 'Network Tools' tab.")

# ==============================================================================
# --- UPTIME MONITOR TAB ---
# ==============================================================================
@st.fragment(run_every=60)
def uptime_monitor_fragment():
    """
    This fragment pings a list of hosts every 60 seconds
    and displays their status.
    """
    
    # Use session state to store the list of hosts between runs
    if "hosts_to_monitor" not in st.session_state:
        # Set a default list to get the user started
        st.session_state.hosts_to_monitor = "8.8.8.8\n1.1.1.1\n192.168.1.1"

    # Create the UI for entering hosts
    st.session_state.hosts_to_monitor = st.text_area(
        "Hosts to Monitor (one per line)",
        value=st.session_state.hosts_to_monitor,
        height=150,
        help="Enter IP addresses or hostnames you want to ping automatically every 60 seconds."
    )
    
    # Create a placeholder for the status table
    status_placeholder = st.empty()
    
    # Process the list of hosts
    hosts = [h.strip() for h in st.session_state.hosts_to_monitor.split('\n') if h.strip()]
    
    results = []
    
    if not hosts:
        st.info("Please enter at least one host or IP address to monitor.")
        return

    # Ping each host and log the results
    for host in hosts:
        if validate_ip(host): # We reuse the validation function
            status, latency = monitoring.ping_target(host) # We reuse the ping function
            
            # We also log this to our database!
            database.log_ping_result(host, status, latency)
            
            results.append({
                "Device": host,
                "Status": status,
                "Latency (ms)": latency if latency is not None else "N/A",
                "Last Checked": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            results.append({
                "Device": host,
                "Status": "Invalid Host",
                "Latency (ms)": "N/A",
                "Last Checked": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

    # Display the results in a table
    df_results = pd.DataFrame(results)
    
    # --- FIX for ArrowInvalid ---
    # Convert 'Latency (ms)' to object type so it can hold 'N/A' and numbers
    if "Latency (ms)" in df_results.columns:
        df_results["Latency (ms)"] = df_results["Latency (ms)"].astype(object)
    
    # --- FIX for use_container_width ---
    status_placeholder.dataframe(df_results, width='stretch')

# ---
# This is the code that *runs* the fragment in the tab
# ---
with tab_uptime:
    st.header("Persistent Uptime Monitor")
    st.caption("This dashboard automatically pings all devices in the list every 60 seconds and logs the results.")
    uptime_monitor_fragment()