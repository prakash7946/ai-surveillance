import cv2
import numpy as np
from ultralytics import YOLO

class WeaponDetector:
    def __init__(self, model_path="yolov8n.pt"):
        # We will use yolov8n.pt as a placeholder for a weapon-specific YOLO model
        # Normally you would load a weights file trained specifically on guns/knives
        print(f"Loading YOLO model from {model_path}...")
        self.model = YOLO(model_path)
        
        # Weapon classes (assuming COCO dataset for generic model testing, ID 43 might be knife, ID 76 might be scissors)
        # However, we will arbitrarily map any detected person or specific object to trigger confidence for the sake of demo
        # For a real system, you'd have custom classes like: 0: gun, 1: knife
        self.weapon_classes = [0] # Demo: We will use Person (0) or other ID to test bounding boxes if no weapon model available. 
        # Actually let's assume COCO: 43 is knife, 80 is tie etc. Let's just track everything and filter later or map to dummy "weapon" status.
        
    def detect(self, frame):
        # Run inference on the given frame
        results = self.model(frame, verbose=False)
        detections = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                
                # In a real model trained on weapons you would use specific weapon IDs: 
                # e.g., if cls == 0 (Gun), cls == 1 (Knife)
                label = self.model.names[cls]
                
                # For demo purposes using the default COCO model:
                # 1. COCO detects 'knife' and 'scissors' natively. Let's label them as KNIFE.
                # 2. COCO doesn't detect 'gun' natively. Let's map 'cell phone' and 'remote' to show up as a GUN for your presentation demo!
                
                is_weapon = False
                display_label = label
                
                if label in ['knife', 'scissors', 'baseball bat']:
                    is_weapon = True
                    display_label = "WEAPON: KNIFE / MELEE"
                elif label in ['cell phone', 'remote', 'hair drier', 'bottle']:
                    # We map these to GUN so you can easily point a phone or remote at the camera to trigger the GUN alert!
                    is_weapon = True
                    display_label = "WEAPON: GUN (Firearm)"
                
                detections.append({
                    'bbox': (x1, y1, x2, y2),
                    'conf': conf,
                    'class_id': cls,
                    'label': display_label,
                    'behavior_target_label': label,
                    'is_weapon': is_weapon
                })
                
        return detections

    def draw_detections(self, frame, detections):
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            label = f"{det['label']} {det['conf']:.2f}"
            color = (0, 0, 255) if det['is_weapon'] else (0, 255, 0)
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
        return frame
