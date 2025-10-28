import psutil
import ping3
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set a timeout for ping3
ping3.EXCEPTIONS = True 

def get_system_metrics():
    """
    Fetches live CPU, Memory, and Disk usage percentages.
    
    Returns:
        dict: A dictionary with 'cpu', 'memory', and 'disk' keys.
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        return {
            "cpu": cpu_percent,
            "memory": memory_percent,
            "disk": disk_percent
        }
    except Exception as e:
        print(f"Error getting system metrics: {e}")
        return {"cpu": 0, "memory": 0, "disk": 0}

def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    """
    Checks for a live internet connection by connecting to Google's DNS.
    
    Returns:
        bool: True if connection is successful, False otherwise.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def ping_target(host):
    """
    Pings a target host and returns its status and latency.
    
    Args:
        host (str): The IP address or hostname to ping.
    
    Returns:
        tuple: (status, latency_ms)
               ('Online', float) or ('Offline', None) or ('Error', None)
    """
    try:
        latency = ping3.ping(host, unit='ms')
        if latency is not None:
            return "Online", round(latency, 2)
        else:
            return "Offline", None
    except ping3.errors.HostUnknown:
        return "Host Unknown", None
    except Exception as e:
        # Catch other errors like Permission Denied (common on some OS for non-root)
        print(f"Ping error for {host}: {e}")
        return "Error", None

def scan_port(host, port):
    """
    Scans a single port on a target host.
    
    Returns:
        tuple: (port, is_open)
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)  # Set a short timeout
            if s.connect_ex((host, port)) == 0:
                return port, True
            else:
                return port, False
    except (socket.timeout, socket.error):
        return port, False

def scan_ports(host, ports_to_scan):
    """
    Scans a list of ports on a target host using multi-threading.
    
    Args:
        host (str): The IP address or hostname to scan.
        ports_to_scan (list): A list of integers (ports).
    
    Returns:
        list: A list of open port numbers.
    """
    open_ports = []
    # Use ThreadPoolExecutor for concurrent port scanning
    with ThreadPoolExecutor(max_workers=50) as executor:
        # Create a future for each port scan
        futures = {executor.submit(scan_port, host, port): port for port in ports_to_scan}
        
        for future in as_completed(futures):
            port, is_open = future.result()
            if is_open:
                open_ports.append(port)
                
    return sorted(open_ports)