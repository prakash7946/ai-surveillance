import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

def load_data(data_dir="data"):
    X = np.load(os.path.join(data_dir, "X.npy"))
    y = np.load(os.path.join(data_dir, "y.npy"))
    return X, y

def build_model(seq_length, num_features):
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(seq_length, num_features)),
        Dropout(0.3),
        LSTM(32),
        Dropout(0.3),
        Dense(16, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def plot_history(history, save_dir="static/eval"):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    plt.figure(figsize=(12, 4))
    
    # Plot training & validation accuracy
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Train Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.title('Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    
    # Plot training & validation loss
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "training_curves.png"))
    plt.close()

def plot_confusion_matrix(y_true, y_pred, save_dir="static/eval"):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Normal', 'Aggressive'], 
                yticklabels=['Normal', 'Aggressive'])
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "confusion_matrix.png"))
    plt.close()

def main():
    print("Loading data...")
    X, y = load_data()
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    seq_length = X.shape[1]
    num_features = X.shape[2]
    
    print("Building model...")
    model = build_model(seq_length, num_features)
    model.summary()
    
    print("Training model...")
    # Using small epochs just to guarantee it finishes somewhat quickly while achieving ~95-100% on synthetic easy data
    history = model.fit(
        X_train, y_train, 
        epochs=15, 
        batch_size=32, 
        validation_split=0.2,
        verbose=1
    )
    
    print("Evaluating model...")
    y_pred_probs = model.predict(X_test)
    y_pred = (y_pred_probs > 0.5).astype(int)
    
    acc = accuracy_score(y_test, y_pred)
    print(f"\nTest Accuracy: {acc*100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Normal', 'Aggressive']))
    
    print("Generating plots...")
    plot_history(history)
    plot_confusion_matrix(y_test, y_pred)
    
    model_dir = "models"
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    model.save(os.path.join(model_dir, "behavior_lstm.h5"))
    print("Model saved to models/behavior_lstm.h5")

if __name__ == "__main__":
    main()
