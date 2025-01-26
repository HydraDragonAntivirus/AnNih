from cx_Freeze import setup, Executable

# Define the script and executable options
executables = [
    Executable(
        "UTKUDORUKBAYRAKTARUGABUGA.py",  # Your script file
        target_name="UTKUDORUKBAYRAKTARUGABUGA.exe",  # Output executable name
        base="console",  # Use "Console" if you don't need a GUI window, otherwise "Win32GUI"
        uac_admin=True  # Request admin privileges (optional)
    )
]

# Setup the cx_Freeze build process
setup(
    name="UTKUDORUKBAYRAKTARUGABUGA",
    version="1.0",
    description="My Python Script to Executable",
    options={
        "build_exe": {
            "packages": ["pyttsx3"],  # List required packages
        }
    },
    executables=executables
)
