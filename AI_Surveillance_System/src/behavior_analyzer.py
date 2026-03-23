import numpy as np
import tensorflow as tf
from collections import deque
import cv2

class BehaviorAnalyzer:
    def __init__(self, model_path="models/behavior_lstm.h5", seq_length=30, num_features=8):
        self.model_path = model_path
        self.seq_length = seq_length
        self.num_features = num_features
        self.sequence_buffer = deque(maxlen=self.seq_length)
        print("Loading LSTM model...")
        try:
            self.model = tf.keras.models.load_model(self.model_path)
            self.model_loaded = True
        except Exception as e:
            print(f"Failed to load LSTM model: {e}")
            self.model_loaded = False
            
        self.consecutive_threats = 0

    def extract_features(self, frame, detections):
        # In a full system, you would extract pose keypoints (MediaPipe/YOLO-Pose)
        # or optical flow. Here we simulate features based on the average movement of bounded boxes.
        
        features = np.zeros(self.num_features)
        
        if detections:
            # Simple heuristic: sizes, positions of bounding boxes
            for i, det in enumerate(detections[:4]): # up to 4 objects
                x1, y1, x2, y2 = det['bbox']
                cx, cy = (x1+x2)/2, (y1+y2)/2
                w, h = x2-x1, y2-y1
                
                if i*2+1 < self.num_features:
                    features[i*2] = cx / frame.shape[1] # normalized x
                    features[i*2+1] = cy / frame.shape[0] # normalized y
                    
        # Add random noise if nothing detected to simulate background baseline
        if not detections:
            features = np.random.normal(0, 0.05, self.num_features)
            
        return features

    def analyze(self, frame, detections):
        features = self.extract_features(frame, detections)
        self.sequence_buffer.append(features)
        
        status = "Normal"
        confidence = 0.0
        
        if len(self.sequence_buffer) == self.seq_length and self.model_loaded:
            # Prepare input for LSTM: (1, seq_length, num_features)
            input_seq = np.array(self.sequence_buffer).reshape(1, self.seq_length, self.num_features)
            
            # Predict
            pred = self.model.predict(input_seq, verbose=0)[0][0]
            confidence = float(pred)
            
            if confidence > 0.5:
                status = "Aggressive/Suspicious"
                self.consecutive_threats += 1
            else:
                self.consecutive_threats = max(0, self.consecutive_threats - 1)
                
        return {
            'status': status,
            'confidence': confidence,
            'is_threat': self.consecutive_threats > 3 # Require 3 consecutive threat frames to avoid flicker
        }
