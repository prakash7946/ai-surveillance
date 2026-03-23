document.addEventListener("DOMContentLoaded", () => {
    const socket = io();
    
    const logContainer = document.getElementById("log-container");
    const threatCounter = document.getElementById("threat-counter");
    const bigAlertOverlay = document.getElementById("big-alert-overlay");
    const cameraToggle = document.getElementById("camera-toggle");
    const cameraStatusText = document.getElementById("camera-status-text");
    const videoStream = document.getElementById("video-stream");
    
    let totalThreats = 0;
    let alertTimeout = null;
    
    // Camera Toggle Logic
    cameraToggle.addEventListener("change", (e) => {
        if (e.target.checked) {
            // Turn ON
            cameraStatusText.innerText = "ON";
            cameraStatusText.className = "status-on";
            videoStream.style.display = "block";
            videoStream.src = "/video_feed?" + new Date().getTime(); // Anti-cache
            addLogEntry("Camera stream activated.", "system-msg");
        } else {
            // Turn OFF
            cameraStatusText.innerText = "OFF";
            cameraStatusText.className = "status-off";
            videoStream.style.display = "none";
            videoStream.src = "";
            addLogEntry("Camera stream deactivated.", "system-msg");
            
            // Notify server to release hardware
            fetch('/stop_feed', { method: 'POST' });
        }
    });

    // Add initial log
    addLogEntry("System active. Camera is ON.", "system-msg");

    socket.on('new_alert', (data) => {
        // data: {weapon: bool, behavior: str, threat_level: str, timestamp: float}
        
        const timeStr = new Date(data.timestamp * 1000).toLocaleTimeString();
        let message = "";
        let logClass = "threat-high";
        
        if (data.weapon && data.threat_level === "HIGH") {
            message = `Weapon Detected! Behavior: ${data.behavior}`;
        } else if (data.weapon) {
            message = `Weapon Object Detected. Monitoring.`;
            logClass = "threat-med";
        } else if (data.threat_level === "HIGH") {
            message = `Aggressive Behavior Detected! No weapon visible.`;
        } else {
            message = `Suspicious Activity: ${data.behavior}`;
            logClass = "threat-med";
        }
        
        addLogEntry(`${message}`, logClass, timeStr);
        
        // Show Big Alert in video feed
        showBigAlert();
        
        // Update Counter
        if (data.threat_level === "HIGH") {
            totalThreats++;
            threatCounter.innerText = `${totalThreats} Threats`;
        }
    });

    function addLogEntry(text, className, timeStr = null) {
        if (!timeStr) {
            timeStr = new Date().toLocaleTimeString();
        }
        
        const entry = document.createElement("div");
        entry.className = `log-entry ${className}`;
        
        const timeSpan = document.createElement("span");
        timeSpan.className = "time";
        timeSpan.innerText = timeStr;
        
        const msgSpan = document.createElement("span");
        msgSpan.className = "msg";
        msgSpan.innerText = text;
        
        entry.appendChild(timeSpan);
        entry.appendChild(msgSpan);
        
        logContainer.prepend(entry);
        
        // Keep logs slightly tidy
        if (logContainer.children.length > 50) {
            logContainer.removeChild(logContainer.lastChild);
        }
    }

    function showBigAlert() {
        bigAlertOverlay.classList.remove("hidden");
        
        // Hide after 3 seconds of no new alerts
        if (alertTimeout) {
            clearTimeout(alertTimeout);
        }
        
        alertTimeout = setTimeout(() => {
            bigAlertOverlay.classList.add("hidden");
        }, 3000);
    }
});
