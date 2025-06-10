#!/usr/bin/env python3
"""
Enhanced Setup script for AI-Enhanced Secure Email Server
DCN Project Setup and Installation
"""

import os
import sys
import subprocess
import platform
import urllib.request
import json

def print_banner():
    """Print project banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║          🤖 AI-Enhanced Secure Email Server              ║
    ║                                                          ║
    ║  Data Communication and Networks (DCN) Project          ║
    ║  Complete Email System with AI Integration              ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

def run_command(command):
    """Run shell command and return success status"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {command}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {command}")
        print(f"Error: {e.stderr}")
        return False, e.stderr

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def check_internet_connection():
    """Check internet connectivity"""
    try:
        urllib.request.urlopen('https://google.com', timeout=5)
        print("✅ Internet connection available")
        return True
    except:
        print("⚠️  No internet connection detected")
        return False

def check_mongodb():
    """Check if MongoDB is available"""
    try:
        subprocess.run(["mongod", "--version"], capture_output=True, check=True)
        print("✅ MongoDB detected")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  MongoDB not found. Please install MongoDB Community Edition")
        print("   Download from: https://www.mongodb.com/try/download/community")
        print("   Or use MongoDB Atlas (cloud): https://cloud.mongodb.com")
        return False

def setup_virtual_environment():
    """Setup Python virtual environment"""
    print("\n🔧 Setting up virtual environment...")
    
    venv_name = "email_server_env"
    
    success, output = run_command(f"python -m venv {venv_name}")
    if not success:
        return None
    
    # Activation commands vary by OS
    if platform.system() == "Windows":
        activate_cmd = f"{venv_name}\\Scripts\\activate"
        pip_cmd = f"{venv_name}\\Scripts\\pip"
        python_cmd = f"{venv_name}\\Scripts\\python"
    else:
        activate_cmd = f"source {venv_name}/bin/activate"
        pip_cmd = f"{venv_name}/bin/pip"
        python_cmd = f"{venv_name}/bin/python"
    
    print(f"📝 To activate: {activate_cmd}")
    return pip_cmd, python_cmd

def install_dependencies(pip_cmd):
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Upgrade pip first
    run_command(f"{pip_cmd} install --upgrade pip")
    
    dependencies = [
        "Flask==2.3.3",
        "Flask-CORS==4.0.0", 
        "Flask-SocketIO==5.3.0",
        "pymongo==4.5.0",
        "requests==2.31.0",
        "cryptography==41.0.4",
        "PyJWT==2.8.0",
        "streamlit==1.26.0",
        "plotly==5.15.0",
        "pandas==2.1.1",
        "python-socketio==5.8.0",
        "python-dotenv==1.0.0"
    ]
    
    for dep in dependencies:
        success, output = run_command(f"{pip_cmd} install {dep}")
        if not success:
            print(f"⚠️  Failed to install {dep}, continuing...")
    
    return True

def create_env_file():
    """Create .env file from template"""
    print("\n⚙️  Creating environment configuration...")
    
    if not os.path.exists(".env"):
        env_content = """# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/email_server

# AI Configuration (Required)
GROQ_API_KEY=your_groq_api_key_here

# Security Configuration  
SECRET_KEY=dcn-email-server-secret-key-2025

# Server Configuration
HOST=0.0.0.0
PORT=5000
DEBUG=True

# Email Server Ports
SMTP_PORT=587
IMAP_PORT=993
POP3_PORT=995

# AI Model Configuration
GROQ_MODEL=mixtral-8x7b-32768
MAX_TOKENS=150

# Security Settings
SPAM_THRESHOLD=0.5
ENABLE_PHISHING_DETECTION=True
ENABLE_COMPOSITION_ASSISTANT=True
"""
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created")
        print("⚠️  Remember to add your GROQ_API_KEY to .env file")
    else:
        print("✅ .env file already exists")

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = ["certs", "logs", "data", "exports", "backups"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created {directory}/ directory")

def create_run_scripts():
    """Create convenient run scripts"""
    print("\n📝 Creating run scripts...")
    
    # Windows batch file
    if platform.system() == "Windows":
        with open("start_servers.bat", "w") as f:
            f.write("""@echo off
echo Starting AI-Enhanced Email Server...
echo.
echo Starting MongoDB (if not running)...
start "MongoDB" mongod

echo.
echo Waiting for MongoDB to start...
timeout /t 5

echo.
echo Starting Flask Backend...
start "Flask Backend" email_server_env\\Scripts\\python app.py

echo.
echo Waiting for Flask to start...
timeout /t 5

echo.
echo Starting Streamlit Interface...
start "Streamlit Interface" email_server_env\\Scripts\\streamlit run streamlit_app.py

echo.
echo All services started!
echo.
echo Access URLs:
echo Flask Dashboard: http://localhost:5000
echo Streamlit Interface: http://localhost:8501
echo.
pause
""")
        print("✅ Created start_servers.bat")
    
    # Unix shell script
    else:
        with open("start_servers.sh", "w") as f:
            f.write("""#!/bin/bash
echo "Starting AI-Enhanced Email Server..."
echo

echo "Starting MongoDB (if not running)..."
mongod --fork --logpath /var/log/mongod.log &

echo
echo "Waiting for MongoDB to start..."
sleep 5

echo
echo "Starting Flask Backend..."
source email_server_env/bin/activate
python app.py &

echo
echo "Waiting for Flask to start..."
sleep 5

echo
echo "Starting Streamlit Interface..."
streamlit run streamlit_app.py &

echo
echo "All services started!"
echo
echo "Access URLs:"
echo "Flask Dashboard: http://localhost:5000"
echo "Streamlit Interface: http://localhost:8501"
echo
""")
        # Make executable
        os.chmod("start_servers.sh", 0o755)
        print("✅ Created start_servers.sh")

def test_installation(python_cmd):
    """Test the installation"""
    print("\n🧪 Testing installation...")
    
    # Test imports
    test_code = '''
import flask
import streamlit
import pymongo
import requests
import cryptography
import pandas
import plotly
print("✅ All dependencies imported successfully")
'''
    
    success, output = run_command(f'{python_cmd} -c "{test_code}"')
    if success:
        print("✅ Installation test passed")
        return True
    else:
        print("❌ Installation test failed")
        return False

def main():
    """Main setup function"""
    print_banner()
    
    # Check requirements
    if not check_python_version():
        return False
    
    internet_available = check_internet_connection()
    mongodb_available = check_mongodb()
    
    # Setup environment
    venv_result = setup_virtual_environment()
    if not venv_result:
        return False
    
    pip_cmd, python_cmd = venv_result
    
    # Install dependencies
    if internet_available:
        if not install_dependencies(pip_cmd):
            return False
    else:
        print("⚠️  Skipping dependency installation (no internet)")
    
    # Create configuration
    create_env_file()
    create_directories()
    create_run_scripts()
    
    # Test installation
    if internet_available:
        test_installation(python_cmd)
    
    # Final instructions
    print("\n" + "="*60)
    print("🎉 Setup completed successfully!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Get a Groq API key from: https://console.groq.com")
    print("2. Add your API key to .env file (replace 'your_groq_api_key_here')")
    
    if not mongodb_available:
        print("3. Install and start MongoDB:")
        print("   - Download from: https://www.mongodb.com/try/download/community")
        print("   - Or use MongoDB Atlas: https://cloud.mongodb.com")
    else:
        print("3. Start MongoDB: mongod")
    
    print("\n🚀 Running the Application:")
    if platform.system() == "Windows":
        print("• Double-click: start_servers.bat")
        print("• Or manually:")
        print("  - Run: email_server_env\\Scripts\\python app.py")
        print("  - Run: email_server_env\\Scripts\\streamlit run streamlit_app.py")
    else:
        print("• Run: ./start_servers.sh")
        print("• Or manually:")
        print("  - Run: email_server_env/bin/python app.py")
        print("  - Run: email_server_env/bin/streamlit run streamlit_app.py")
    
    print("\n🌐 Access URLs:")
    print("• Flask Backend: http://localhost:5000")
    print("• Streamlit Interface: http://localhost:8501")
    
    print("\n📚 DCN Project Features:")
    print("• ✅ SMTP, IMAP, POP3 server implementation")
    print("• ✅ TLS/SSL encryption and security")
    print("• ✅ AI-powered spam and phishing detection")
    print("• ✅ Real-time protocol monitoring")
    print("• ✅ Comprehensive analytics dashboard")
    print("• ✅ Interactive testing interface")
    
    return True

if __name__ == "__main__":
    main()
