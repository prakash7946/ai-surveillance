import numpy as np
import os

def generate_synthetic_data(num_samples=1000, seq_length=30, num_features=8):
    """
    Generates synthetic sequence data for LSTM behavioral training.
    Normal behavior: slight movements, smooth trajectories.
    Aggression: erratic, rapid changes in key features.
    
    Features are imagined to be relative keypoint velocities or bounding box shifts.
    Classes: 0 -> Normal, 1 -> Aggressive/Suspicious
    """
    X = []
    y = []
    
    for _ in range(num_samples):
        label = np.random.choice([0, 1])
        if label == 0:
            # Normal behavior: small random walk, mean centered around 0
            seq = np.cumsum(np.random.normal(0, 0.05, (seq_length, num_features)), axis=0) 
        else:
            # Aggressive behavior: larger steps, more sudden changes
            seq = np.cumsum(np.random.normal(0, 0.3, (seq_length, num_features)), axis=0)
            # Add some sudden spikes to simulate abrupt strikes or sudden run
            spike_idx = np.random.randint(0, seq_length, size=3)
            seq[spike_idx] += np.random.normal(0, 1.5, (3, num_features))
            
        X.append(seq)
        y.append(label)
        
    X = np.array(X)
    y = np.array(y)
    return X, y

def save_data(data_dir="data"):
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    print("Generating synthetic behavioral data...")
    X, y = generate_synthetic_data(num_samples=2000)
    
    np.save(os.path.join(data_dir, "X.npy"), X)
    np.save(os.path.join(data_dir, "y.npy"), y)
    print(f"Saved synthetic dataset of shape {X.shape} to {data_dir}/")

if __name__ == "__main__":
    save_data()
