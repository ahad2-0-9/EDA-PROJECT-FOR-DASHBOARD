"""
Public access wrapper for Streamlit app using ngrok
Run this to expose the dashboard to the internet with a public URL
"""

import subprocess
import time
import sys
from pyngrok import ngrok, conf
import webbrowser

# Get ngrok auth token (free tier doesn't require it but recommended)
print("=" * 60)
print("Starting Food Price Dashboard - Public Access Mode")
print("=" * 60)

# Kill any existing ngrok processes
try:
    subprocess.run(["taskkill", "/IM", "ngrok.exe", "/F"], 
                  stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    time.sleep(1)
except:
    pass

# Start ngrok tunnel
print("\nStarting ngrok tunnel...")
try:
    # Set ngrok config
    ngrok.set_auth_token("")  # Leave empty for free tier
    
    # Connect to port 8501 (Streamlit default)
    public_url = ngrok.connect(8501)
    print(f"\n✓ Public URL: {public_url}")
    print(f"\n✓ Anyone can now access your dashboard at: {public_url}")
    
    print("\n" + "=" * 60)
    print("Dashboard URLs:")
    print("=" * 60)
    print(f"  Local Access:  http://localhost:8501")
    print(f"  Network Access: http://192.168.1.103:8501")
    print(f"  Public Access: {public_url}")
    print("=" * 60)
    
    print("\nThe public URL will remain active as long as this script is running.")
    print("Press Ctrl+C to stop and close the public access.\n")
    
    # Keep the tunnel alive
    ngrok_process = ngrok.get_ngrok_process()
    ngrok_process.proc.wait()
    
except Exception as e:
    print(f"Error starting ngrok tunnel: {e}")
    print("\nMake sure Streamlit is running on port 8501")
    print("Start the dashboard separately with: streamlit run app.py")
    sys.exit(1)
