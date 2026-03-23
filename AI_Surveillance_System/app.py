from flask import Flask, render_template, Response
from flask_socketio import SocketIO
from src.pipeline import VideoPipeline
import smtplib
from email.message import EmailMessage
import threading
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

pipeline = VideoPipeline()

# Email Configuration
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your_email@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your_app_password")
RECEIVER_EMAIL = "prakashsiva2004429@gmail.com"

last_email_time = 0
EMAIL_COOLDOWN = 60 # Don't send more than 1 email per 60 seconds

def send_email_alert(alert_type, behavior, timestamp):
    try:
        msg = EmailMessage()
        msg.set_content(f"CRITICAL ALERT: Threat detected by AI Surveillance System.\n\nType: {alert_type}\nBehavior: {behavior}\nTime: {time.ctime(timestamp)}\n\nPlease check the dashboard immediately.")
        msg['Subject'] = f"SECURITY ALERT: {alert_type} Detected!"
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL

        # Use Gmail SMTP server
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Alert email sent successfully to {RECEIVER_EMAIL}!")
    except Exception as e:
        print(f"Failed to send email alert. Please check .env credentials. Error: {e}")

def alert_callback(data):
    # Emit alert to frontend via socketio
    # data: {'weapon': bool, 'behavior': str, 'threat_level': str, 'timestamp': float}
    socketio.emit('new_alert', data)
    
    # Check if we should send an email for HIGH threat
    if data['threat_level'] == 'HIGH':
        global last_email_time
        current_time = time.time()
        if current_time - last_email_time > EMAIL_COOLDOWN:
            last_email_time = current_time
            alert_type = "Weapon + Aggression" if data['weapon'] else "Aggressive Behavior"
            
            # Send email in a separate thread so it doesn't block the video stream
            email_thread = threading.Thread(target=send_email_alert, args=(alert_type, data['behavior'], data['timestamp']))
            email_thread.daemon = True
            email_thread.start()

pipeline.set_alert_callback(alert_callback)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    # If already running, we might need to stop it first, but let's assume it reconnects cleanly.
    pipeline.stop() # Ensure old loop stops before starting a new one
    import time
    time.sleep(0.5) # Wait briefly for hardware to release
    return Response(pipeline.run(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_feed', methods=['POST'])
def stop_feed():
    pipeline.stop()
    return {"status": "stopped"}

if __name__ == '__main__':
    # Default Flask server with SocketIO
    print("Starting AI Surveillance System Dashboard...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
