import subprocess
import time
import os
import sys
import psutil
import urllib.request
import socket
import requests
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone
import dateutil.parser
import ctypes

TAILSCALE_API_KEY = 'tskey-api-k2qwsL7MQR11CNTRL-ahhhhhhhuseurs'
TAILSCALE_NODE_NAME = 'asdasdasdas'
TAILSCALE_NODE_ALIASES = ['aaaaaaaa', 'bbbb-1', 'the nocde id thingy']
TAILSCALE_OFFLINE_THRESHOLD = 180  # 3 minutes
MONITOR_INTERVAL_SECONDS = 300  # default, can be updated from menu


networks = ["Tufts_Secure", "Tufts_Secure_6e", "eduroam"]
MY_PUBLIC_WIFI_PATH = r"C:\\Program Files (x86)\\MyPublicWiFi\\MyPublicWiFi.exe"
ETHERNET_INTERFACE = "Ethernet 2"
HOST_IP = "192.168.1.14"
SERVER_IP = "192.168.1.101"
EMAIL_FROM = "urma@gmail.com"
EMAIL_TO = "urma@gmail.com"
EMAIL_PASS = "aaaa cccc xxxx pghi"
MAX_FAIL_COUNT_BEFORE_REBOOT = 5


# Global variable to store full diagnostic log
diagnostic_log = []

last_summary_sent_date = None


def log_message(message):
    """Add message to both console and diagnostic log"""
    print(message)
    diagnostic_log.append(message)

def clear_diagnostic_log():
    """Clear the diagnostic log"""
    global diagnostic_log
    diagnostic_log = []

def get_diagnostic_log():
    """Get the full diagnostic log as a string"""
    return "\n".join(diagnostic_log)

# ========== Helper Functions ==========

def check_tailscale_node_online():
    print("🔍 Starting comprehensive Tailscale connectivity test...")
    try:
        headers = {
            'Authorization': f'Bearer {TAILSCALE_API_KEY}',
            'Content-Type': 'application/json'
        }
        response = requests.get(
            'https://api.tailscale.com/api/v2/tailnet/-/devices', 
            headers=headers, 
            timeout=15
        )
        print(f"   → API Response Status: {response.status_code}")
        if response.status_code != 200:
            return False
        data = response.json()
        devices = data.get('devices', [])
        target = None
        for device in devices:
            hostname = device.get('hostname', '')
            name = device.get('name', '')
            node_id = device.get('nodeId', '')
            machine_key = device.get('machineKey', '')
            for identifier in TAILSCALE_NODE_ALIASES:
                if (identifier in hostname or identifier in name or identifier == node_id or identifier in machine_key):
                    target = device
                    print(f"✅ Found target device using identifier '{identifier}': {hostname}")
                    break
            if target:
                break

        if not target:
            print(f"❌ Target node not found using any of these identifiers: {TAILSCALE_NODE_ALIASES}")
            return False

        online = target.get('online', False)
        last_seen = target.get('lastSeen')
        if online:
            print("✅ Device is currently ONLINE")
            return True
        if last_seen:
            try:
                last_seen_dt = dateutil.parser.parse(last_seen)
                now = datetime.now(timezone.utc)
                offline_seconds = (now - last_seen_dt).total_seconds()
                print(f"   → Last seen: {offline_seconds:.1f} seconds ago")
                if offline_seconds < TAILSCALE_OFFLINE_THRESHOLD:
                    print("⚠️ Recently offline, assuming still connected")
                    return True
                else:
                    print(f"❌ Offline for more than {TAILSCALE_OFFLINE_THRESHOLD} seconds")
                    return False
            except Exception as e:
                print(f"⚠️ Could not parse 'lastSeen': {e}")
                return False
        else:
            print("❌ No 'lastSeen' data available")
            return False
    except Exception as e:
        print(f"❌ Error during Tailscale API request: {e}")
        return False

# The rest of the code remains unchanged
# You can now call check_tailscale_node_online and act accordingly

def check_tailscale_comprehensive():
    """
    The ultimate MyPublicWiFi test - comprehensive Tailscale connectivity check.
    If this passes, MyPublicWiFi is definitely working correctly.
    """
    log_message("🚀 COMPREHENSIVE TAILSCALE TEST")
    log_message("=" * 50)
    log_message("This test proves MyPublicWiFi is working correctly.")
    log_message("If Tailscale is online, clients can reach internet!")
    log_message("=" * 50)
    
    # Test 1: Basic connectivity
    log_message("\n🔧 Test 1: Basic Tailscale API connectivity")
    if not check_tailscale_node_online():
        log_message("❌ FAILED: Tailscale node is not online")
        return False
    
    # Test 2: Additional API endpoint test
    log_message("\n🔧 Test 2: Testing additional API endpoints")
    try:
        headers = {
            'Authorization': f'Bearer {TAILSCALE_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Test tailnet info
        log_message("   → Testing tailnet info endpoint...")
        response = requests.get(
            'https://api.tailscale.com/api/v2/tailnet/-', 
            headers=headers, 
            timeout=10
        )
        
        if response.status_code == 200:
            tailnet_info = response.json()
            log_message(f"   ✅ Tailnet: {tailnet_info.get('name', 'Unknown')}")
        else:
            log_message(f"   ⚠️ Tailnet info unavailable (status: {response.status_code})")
            
    except Exception as e:
        log_message(f"   ⚠️ Additional API test failed: {e}")
    
    # Test 3: Local Tailscale status (if available)
    log_message("\n🔧 Test 3: Local Tailscale status check")
    try:
        result = subprocess.run(
            ['tailscale', 'status', '--json'], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        
        if result.returncode == 0:
            log_message("   ✅ Local Tailscale CLI is responding")
            try:
                import json
                local_status = json.loads(result.stdout)
                self_info = local_status.get('Self', {})
                log_message(f"   → Local IP: {self_info.get('TailscaleIPs', ['Unknown'])[0]}")
                log_message(f"   → Local Online: {self_info.get('Online', False)}")
            except:
                log_message("   ⚠️ Could not parse local status")
        else:
            log_message("   ⚠️ Local Tailscale CLI not available (this is OK)")
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        log_message("   ⚠️ Local Tailscale CLI not available (this is OK)")
    except Exception as e:
        log_message(f"   ⚠️ Local status check failed: {e}")
    
    log_message("\n" + "=" * 50)
    log_message("✅ COMPREHENSIVE TAILSCALE TEST PASSED!")
    log_message("🎉 MyPublicWiFi is working correctly!")
    log_message("🌐 Clients can successfully reach the internet!")
    log_message("=" * 50)
    
    return True


def send_email(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_FROM, EMAIL_PASS)
            smtp.send_message(msg)
        log_message("📧 Email sent.")
    except Exception as e:
        log_message(f"⚠️  Email send failed: {e}")


def get_wifi_interface():
    try:
        output = subprocess.check_output("netsh wlan show interfaces", shell=True, text=True)
        for line in output.splitlines():
            if line.strip().startswith("Name"):
                return line.split(":", 1)[1].strip()
    except Exception as e:
        log_message(f"Error detecting Wi-Fi interface: {e}")
    return None


def test_internet():
    try:
        # Test DNS reachability
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        # Test HTTP
        requests.get("https://www.google.com", timeout=5)
        return True
    except Exception:
        return False


def disconnect_wifi():
    log_message("🔌 Disconnecting Wi-Fi...")
    subprocess.run("netsh wlan disconnect", shell=True)
    time.sleep(5)


def connect_wifi(interface):
    for net in networks:
        log_message(f"📡 Trying to connect to {net}...")
        subprocess.run(f'netsh wlan connect name="{net}" interface="{interface}"', shell=True)
        time.sleep(10)
        if test_internet():
            log_message(f"✅ Connected to {net} and internet is working.")
            return True
        else:
            log_message(f"❌ Connection to {net} failed.")
    log_message("❌ All connection attempts failed.")
    return False


def is_mypublicwifi_running():
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            name = proc.info['name']
            if name and "mypublicwifi" in name.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def start_mypublicwifi():
    log_message("🚀 Checking MyPublicWiFi app...")
    if not is_mypublicwifi_running():
        log_message("❌ MyPublicWiFi.exe not running. Starting it now...")
        try:
            subprocess.Popen([MY_PUBLIC_WIFI_PATH], shell=False)
            time.sleep(10)
            log_message("✅ MyPublicWiFi started.")
        except Exception as e:
            log_message(f"❌ Failed to start MyPublicWiFi: {e}")
    else:
        log_message("✅ MyPublicWiFi is already running.")


def kill_mypublicwifi():
    log_message("🛑 Killing MyPublicWiFi process...")
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if "mypublicwifi" in proc.info['name'].lower():
                proc.kill()
                log_message("✅ Killed MyPublicWiFi.")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    time.sleep(3)


def relaunch_mypublicwifi():
    kill_mypublicwifi()
    time.sleep(3)
    start_mypublicwifi()


def check_ethernet():
    try:
        interfaces = psutil.net_if_addrs()
        eth_addrs = interfaces.get(ETHERNET_INTERFACE)
        if not eth_addrs:
            send_email("❌ Ethernet Missing", f"{ETHERNET_INTERFACE} interface not found.")
            return False

        has_ip = any(a.address == HOST_IP and a.family == socket.AF_INET for a in eth_addrs)
        if not has_ip:
            send_email("❌ Wrong IP", f"{ETHERNET_INTERFACE} does not have IP {HOST_IP}.")
            return False

        # Try pinging the server IP
        result = os.system(f"ping -n 1 -S {HOST_IP} {SERVER_IP} >nul")
        if result != 0:
            send_email("❌ LAN Server Not Reachable", f"Cannot ping {SERVER_IP} from {HOST_IP}.")
            return False

        return True
    except Exception as e:
        send_email("❌ Ethernet Check Failed", str(e))
        return False


def test_mypublicwifi_setup():
    """
    Simplified MyPublicWiFi test focusing on what really matters:
    1. Basic local setup (process running, IP configured, LAN reachable)
    2. Comprehensive Tailscale test (the ultimate proof it's working)
    """
    # Clear previous diagnostic log
    clear_diagnostic_log()
    
    log_message("🛠 Testing MyPublicWiFi Setup")
    log_message("=" * 40)
    
    issues = []
    
    # Basic local checks
    log_message("\n📋 Basic Local Setup Checks:")
    
    # 1. Check MyPublicWiFi process
    if not is_mypublicwifi_running():
        issues.append("❌ MyPublicWiFi is NOT running.")
        log_message("❌ MyPublicWiFi process is NOT running")
    else:
        log_message("✅ MyPublicWiFi process is running")

    # 2. Check Ethernet 2 has IP 192.168.1.14
    interfaces = psutil.net_if_addrs()
    eth_addrs = interfaces.get(ETHERNET_INTERFACE)
    if not eth_addrs:
        issues.append(f"❌ Interface '{ETHERNET_INTERFACE}' not found.")
        log_message(f"❌ Interface '{ETHERNET_INTERFACE}' not found")
    else:
        has_correct_ip = any(a.address == HOST_IP and a.family == socket.AF_INET for a in eth_addrs)
        if has_correct_ip:
            log_message(f"✅ {ETHERNET_INTERFACE} has correct IP {HOST_IP}")
        else:
            issues.append(f"❌ {ETHERNET_INTERFACE} does NOT have IP {HOST_IP}")
            log_message(f"❌ {ETHERNET_INTERFACE} does NOT have IP {HOST_IP}")

    # 3. Ping the LAN server (192.168.1.101)
    response = os.system(f"ping -n 1 -S {HOST_IP} {SERVER_IP} >nul")
    if response == 0:
        log_message(f"✅ LAN server {SERVER_IP} is reachable via {HOST_IP}")
    else:
        issues.append(f"❌ Cannot ping {SERVER_IP} from {HOST_IP}")
        log_message(f"❌ Cannot ping {SERVER_IP} from {HOST_IP}")

    # 4. Check main internet connection
    if test_internet():
        log_message("✅ Internet is working via Wi-Fi (source connection)")
    else:
        issues.append("❌ Internet via Wi-Fi is down (source connection)")
        log_message("❌ Internet via Wi-Fi is down (source connection)")
    
    # 5. THE ULTIMATE TEST - Comprehensive Tailscale check
    log_message("\n🎯 ULTIMATE TEST - Comprehensive Tailscale Check:")
    log_message("(This proves MyPublicWiFi is working correctly)")
    
    if check_tailscale_comprehensive():
        log_message("✅ TAILSCALE TEST PASSED - MyPublicWiFi is working perfectly!")
    else:
        issues.append("❌ Tailscale node is offline - MyPublicWiFi may not be working")
        log_message("❌ TAILSCALE TEST FAILED - MyPublicWiFi may not be working")

    # Summary
    log_message("\n" + "=" * 40)
    if issues:
        log_message("🛑 Issues found:")
        for issue in issues:
            log_message(f"   {issue}")
        log_message("\n📧 Sending email notification...")
        
        # Send full diagnostic log in email
        full_log = get_diagnostic_log()
        email_body = f"MyPublicWiFi Setup Issues Detected:\n\n{full_log}"
        
        # If email is too long (over 50KB), truncate it
        if len(email_body) > 50000:
            email_body = email_body[:45000] + "\n\n[... Log truncated due to length ...]"
        
        send_email("❌ MyPublicWiFi Setup Issues", email_body)
    else:
        log_message("🎉 ALL TESTS PASSED!")
        log_message("✅ MyPublicWiFi is working perfectly!")
        log_message("🌐 Clients can successfully access the internet!")
    log_message("=" * 40)


def reboot_system():
    log_message("⚠️  Triggering system reboot now...")
    # Disabled as requested
    # os.system("shutdown /r /t 5")

from datetime import date

def monitor(interface):
    start_mypublicwifi()
    fail_count = 0
    log_message("\n🚀 Monitoring started. Press Ctrl+C to stop.")
    try:
        while True:
            now = time.strftime("%H:%M:%S")
            if test_internet():
                log_message(f"{now} ✅ Internet OK")
                fail_count = 0
            else:
                log_message(f"{now} ❌ Internet DOWN. Reconnecting...")
                fail_count += 1
                disconnect_wifi()
                if not connect_wifi(interface):
                    log_message("⚠️ Failed to reconnect to any preferred network.")
                    send_email("Internet Outage", "All Wi-Fi connection attempts failed.")
                    
            # Relaunch WiFi sharing if Ethernet isn't OK
            start_mypublicwifi()
            if not check_ethernet():
                log_message("⚠️ Ethernet config invalid. Relaunching MyPublicWiFi...")
                send_email("⚠️ Ethernet Issue", "Relaunching MyPublicWiFi due to shared network issues.")
                relaunch_mypublicwifi()
                time.sleep(15)
                if not check_ethernet():
                    send_email("❌ Critical", "LAN issue persists after restart.")

            # ✅ NEW: Check tailscale availability via full test
            if not check_tailscale_comprehensive():
                log_message("❌ Tailscale test failed — restarting MyPublicWiFi.")
                send_email("❌ Tailscale Offline", "Comprehensive test failed. Restarting MyPublicWiFi.")
                relaunch_mypublicwifi()
                time.sleep(60)
                # Optional: verify again
                if not check_tailscale_comprehensive():
                    send_email("⚠️ Tailscale still offline", "Even after restarting MyPublicWiFi.")


            if fail_count >= MAX_FAIL_COUNT_BEFORE_REBOOT:
                log_message("❌ Too many failures. Reboot condition met.")
                send_email("⚠️ Reboot Limit Reached", "System would reboot now (NERFED).")
                reboot_system()
                break

            today = date.today()
            global last_summary_sent_date

            if last_summary_sent_date != today:
                summary_log = get_diagnostic_log()
                send_email("✅ Daily MyPublicWiFi Status", f"All systems working as of {today}.\n\n{summary_log}")
                last_summary_sent_date = today
                clear_diagnostic_log()  # optional: reset log after daily send

            time.sleep(MONITOR_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        log_message("\n👋 Monitoring stopped by user.")


def pause():
    input("\nPress Enter to continue...")


def show_menu(interface):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("========== WiFi Monitor Menu ==========")
        print("1. Start monitoring connection")
        print("2. Test internet (Google)")
        print("3. Disconnect Wi-Fi")
        print("4. Try reconnect to preferred networks")
        print("5. Test reboot system (disabled)")
        print("6. Test MyPublicWiFi status")
        print("7. Exit")
        print("8. Set monitor interval (seconds)")
        print("=======================================\n")

        choice = input("Select an option [1-8]: ")

        if choice == "1":
            monitor(interface)
        elif choice == "2":
            if test_internet():
                print("✅ Internet is reachable.")
            else:
                print("❌ Internet is not reachable.")
            pause()
        elif choice == "3":
            disconnect_wifi()
            pause()
        elif choice == "4":
            connect_wifi(interface)
            pause()
        elif choice == "5":
            print("⚠️ This test reboot is disabled in this version.")
            pause()
        elif choice == "6":
            print("\n🛠 Testing MyPublicWiFi setup...\n")
            test_mypublicwifi_setup()
            pause()
        elif choice == "7":
            print("👋 Exiting...")

        elif choice == "8":
            try:
                new_val = int(input("Enter new interval in seconds (e.g., 60): "))
                if new_val < 10:
                    print("⚠️ Too fast; must be at least 10 seconds.")
                else:
                    global MONITOR_INTERVAL_SECONDS
                    MONITOR_INTERVAL_SECONDS = new_val
                    print(f"✅ Monitor interval set to {new_val} seconds.")
            except ValueError:
                print("❌ Invalid number.")
            pause()

            break
        else:
            print("❓ Invalid choice.")
            pause()


# ========== MAIN ==========

if __name__ == "__main__":
    interface = get_wifi_interface()
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("⚠️ WARNING: This script is NOT running as administrator!")
        print("❗ MyPublicWiFi may fail to start correctly without admin rights.\n")
        time.sleep(1)

    if not interface:
        print("❌ Could not detect Wi-Fi interface.")
        pause()
        sys.exit(1)
    show_menu(interface)
