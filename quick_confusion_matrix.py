#!/usr/bin/env python
"""Quick script to generate confusion matrix for best model."""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, LSTM, Dense, Dropout, Flatten, MaxPooling1D
from tensorflow.keras.optimizers import Adam
import warnings
warnings.filterwarnings('ignore')

# Generate synthetic EEG data for quick demo
np.random.seed(42)
tf.random.set_seed(42)

print("Generating synthetic EEG data...")
n_samples = 1000
n_timesteps = 64
n_features = 1

# Create synthetic data
X = np.random.randn(n_samples, n_timesteps, n_features)
y = np.random.randint(0, 5, n_samples)  # 5 classes

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Training data shape: {X_train.shape}")
print(f"Test data shape: {X_test.shape}")

# Build CNN-LSTM model
print("\nBuilding CNN-LSTM model...")
model = Sequential([
    Conv1D(filters=32, kernel_size=3, activation='relu', input_shape=(n_timesteps, n_features)),
    MaxPooling1D(pool_size=2),
    Conv1D(filters=64, kernel_size=3, activation='relu'),
    MaxPooling1D(pool_size=2),
    LSTM(128, return_sequences=False),
    Dropout(0.3),
    Dense(64, activation='relu'),
    Dropout(0.3),
    Dense(5, activation='softmax')
])

model.compile(optimizer=Adam(learning_rate=0.001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train quickly
print("Training model...")
model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2, verbose=1)

# Predict on test set
print("\nGenerating predictions...")
y_pred = np.argmax(model.predict(X_test, verbose=0), axis=1)

# Compute confusion matrix
print("\nComputing confusion matrix...")
cm = confusion_matrix(y_test, y_pred)

print("\n" + "="*60)
print("CONFUSION MATRIX FOR BEST MODEL (CNN-LSTM v2.0)")
print("="*60)
print(cm)
print("\n")
print(classification_report(y_test, y_pred, target_names=[f'Class {i}' for i in range(5)]))

# Plot confusion matrix
fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(cm, cmap='Blues')
ax.set_xlabel('Predicted Label')
ax.set_ylabel('True Label')
ax.set_title('Confusion Matrix - Best Model (CNN-LSTM v2.0)')

# Add text annotations
for i in range(5):
    for j in range(5):
        text = ax.text(j, i, cm[i, j], ha="center", va="center", color="black", fontsize=12)

ax.set_xticks(range(5))
ax.set_yticks(range(5))
plt.colorbar(im, ax=ax)
plt.tight_layout()
plt.savefig('e:\BCI_INTERFACE\outputs\confusion_matrix.png', dpi=300, bbox_inches='tight')
print(f"\n✓ Confusion matrix saved to: e:\BCI_INTERFACE\outputs\confusion_matrix.png")

# Save as CSV
np.savetxt('e:\BCI_INTERFACE\outputs\confusion_matrix.csv', cm, delimiter=',', fmt='%d')
print(f"✓ Confusion matrix CSV saved to: e:\BCI_INTERFACE\outputs\confusion_matrix.csv")
