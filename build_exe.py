import os
import subprocess
import sys

def main():
    """
    Builds the standalone executable using PyInstaller.
    Requires pyinstaller to be installed (`pip install pyinstaller`).
    """
    print("Building ANOVA Calculator Executable...")
    
    # Ensure we are in the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check if PyInstaller is available
    try:
        import PyInstaller.__main__
    except ImportError:
        print("PyInstaller is not installed. Please run `pip install -r requirements.txt`.")
        sys.exit(1)
        
    # Build command configuration
    build_args = [
        'anova_gui.py',            # Main entry point
        '--name=ANOVACalculator',  # Name of the executable
        '--windowed',              # No console window (GUI mode)
        '--onefile',               # Bundle everything into a single .exe
        '--clean',                 # Clean PyInstaller cache
        '--noconfirm',             # Replace output directory without asking
    ]
    
    # Add icon if it exists
    icon_path = os.path.join(script_dir, 'app_icon.ico')
    if os.path.exists(icon_path):
        build_args.append(f'--icon={icon_path}')
        print(f"Using icon: {icon_path}")
    else:
        print("Warning: app_icon.ico not found. Using default PyInstaller icon.")
        
    # Execute PyInstaller
    PyInstaller.__main__.run(build_args)
    
    # Check output
    exe_path = os.path.join(script_dir, 'dist', 'ANOVACalculator.exe')
    if os.path.exists(exe_path):
        print(f"\nSuccess! Executable built at: {exe_path}")
    else:
        print("\nBuild failed or executable not found.")

if __name__ == "__main__":
    main()
