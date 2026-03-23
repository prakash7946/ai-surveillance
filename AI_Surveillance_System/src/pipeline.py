import cv2
import time
from src.detector import WeaponDetector
from src.behavior_analyzer import BehaviorAnalyzer

class VideoPipeline:
    def __init__(self):
        self.detector = WeaponDetector(model_path="yolov8n.pt")
        self.behavior_analyzer = BehaviorAnalyzer()
        self.alert_callback = None
        self.is_running = False

    def set_alert_callback(self, callback):
        self.alert_callback = callback

    def run(self, source=0):
        # source can be 0 for webcam or a video file path
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            print(f"Error: Could not open video source {source}")
            return

        self.is_running = True
        frame_count = 0
        start_time = time.time()

        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 1. Weapon Detection (YOLO)
            detections = self.detector.detect(frame)
            frame = self.detector.draw_detections(frame, detections)
            
            weapon_detected = any(d['is_weapon'] for d in detections)
            
            # 2. Behavior Analysis (LSTM)
            behavior_info = self.behavior_analyzer.analyze(frame, detections)
            
            # 3. Threat Assessment
            is_threat = weapon_detected or behavior_info['is_threat']
            
            # Trigger alert
            if is_threat and self.alert_callback:
                self.alert_callback({
                    'weapon': weapon_detected,
                    'behavior': behavior_info['status'],
                    'threat_level': 'HIGH' if weapon_detected and behavior_info['is_threat'] else 'MEDIUM',
                    'timestamp': time.time()
                })

            # Overlay info
            fps = frame_count / (time.time() - start_time)
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            status_color = (0, 0, 255) if is_threat else (0, 255, 0)
            status_text = f"Threat: {'YES' if is_threat else 'NO'} | Behavior: {behavior_info['status']} ({behavior_info['confidence']:.2f})"
            cv2.putText(frame, status_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

            # Yield frame for web stream
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                   
            frame_count += 1
            time.sleep(0.01) # Manage FPS slightly for demo
            
        cap.release()

    def stop(self):
        self.is_running = False
