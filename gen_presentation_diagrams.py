#!/usr/bin/env python
"""Generate presentation-style architecture diagrams for BCI Interface."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import os

def create_presentation_overview():
    """Create a high-level presentation overview of ML + WebApp integration."""
    
    fig = plt.figure(figsize=(20, 12))
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(10, 11.5, 'BCI Interface - Complete ML + WebApp Integration', 
            fontsize=22, fontweight='bold', ha='center')
    ax.text(10, 11, 'Brain-Computer Interface System with Real-Time Inference', 
            fontsize=14, ha='center', style='italic', color='#666')
    
    # ====================== LEFT SIDE: ML PIPELINE ======================
    
    # ML Pipeline Title
    ax.text(1, 10.2, 'MACHINE LEARNING PIPELINE', fontsize=13, fontweight='bold', 
            bbox=dict(boxstyle='round', facecolor='#7B1FA2', alpha=0.8, edgecolor='none'),
            color='white')
    
    # ---- Stage 1: Data Collection ----
    rect1 = FancyBboxPatch((0.2, 8.5), 2.2, 1.3, boxstyle="round,pad=0.1", 
                           edgecolor='#1976D2', facecolor='#E3F2FD', linewidth=3)
    ax.add_patch(rect1)
    ax.text(1.3, 9.5, 'DATA COLLECTION', fontsize=11, ha='center', fontweight='bold', color='#1565C0')
    ax.text(1.3, 9.1, 'PhysioNet Database', fontsize=9, ha='center')
    ax.text(1.3, 8.8, '(109 Subjects)', fontsize=9, ha='center')
    
    # Arrow down
    arrow = FancyArrowPatch((1.3, 8.4), (1.3, 7.8), arrowstyle='->', mutation_scale=30, 
                           linewidth=3, color='#1976D2')
    ax.add_patch(arrow)
    
    # ---- Stage 2: Data Preprocessing ----
    rect2 = FancyBboxPatch((0.2, 6.3), 2.2, 1.3, boxstyle="round,pad=0.1", 
                           edgecolor='#F57F17', facecolor='#FFF9C4', linewidth=3)
    ax.add_patch(rect2)
    ax.text(1.3, 7.3, 'DATA PREPROCESSING', fontsize=11, ha='center', fontweight='bold', color='#F57F17')
    ax.text(1.3, 6.9, 'Filter, Normalize', fontsize=9, ha='center')
    ax.text(1.3, 6.6, 'Augmentation', fontsize=9, ha='center')
    
    # Arrow down
    arrow = FancyArrowPatch((1.3, 6.2), (1.3, 5.6), arrowstyle='->', mutation_scale=30, 
                           linewidth=3, color='#F57F17')
    ax.add_patch(arrow)
    
    # ---- Stage 3: Model Training ----
    rect3 = FancyBboxPatch((0.2, 4.1), 2.2, 1.3, boxstyle="round,pad=0.1", 
                           edgecolor='#7B1FA2', facecolor='#F3E5F5', linewidth=3)
    ax.add_patch(rect3)
    ax.text(1.3, 5.1, 'MODEL TRAINING', fontsize=11, ha='center', fontweight='bold', color='#7B1FA2')
    ax.text(1.3, 4.7, 'CNN-LSTM Network', fontsize=9, ha='center')
    ax.text(1.3, 4.4, '50 Epochs', fontsize=9, ha='center')
    
    # Arrow down
    arrow = FancyArrowPatch((1.3, 4), (1.3, 3.4), arrowstyle='->', mutation_scale=30, 
                           linewidth=3, color='#7B1FA2')
    ax.add_patch(arrow)
    
    # ---- Stage 4: Model Evaluation ----
    rect4 = FancyBboxPatch((0.2, 1.9), 2.2, 1.3, boxstyle="round,pad=0.1", 
                           edgecolor='#D32F2F', facecolor='#FFEBEE', linewidth=3)
    ax.add_patch(rect4)
    ax.text(1.3, 2.9, 'MODEL EVALUATION', fontsize=11, ha='center', fontweight='bold', color='#D32F2F')
    ax.text(1.3, 2.5, 'Accuracy: 76.43%', fontsize=10, ha='center', fontweight='bold')
    ax.text(1.3, 2.2, '5-Class Classification', fontsize=9, ha='center')
    
    # ====================== MIDDLE: REAL-TIME INFERENCE ======================
    
    ax.text(4.8, 10.2, 'REAL-TIME INFERENCE ENGINE', fontsize=13, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#00695C', alpha=0.8, edgecolor='none'),
            color='white')
    
    # EEG Input
    rect5 = FancyBboxPatch((3.8, 8.5), 2, 1.3, boxstyle="round,pad=0.1", 
                           edgecolor='#1976D2', facecolor='#E3F2FD', linewidth=3)
    ax.add_patch(rect5)
    ax.text(4.8, 9.4, 'EEG INPUT STREAM', fontsize=10, ha='center', fontweight='bold')
    ax.text(4.8, 9, '64 Channels', fontsize=9, ha='center')
    ax.text(4.8, 8.7, '160 Hz Sampling', fontsize=9, ha='center')
    
    # Arrow right and down
    arrow = FancyArrowPatch((5.8, 9.1), (6.2, 9.1), arrowstyle='->', mutation_scale=30, 
                           linewidth=3, color='#1976D2')
    ax.add_patch(arrow)
    
    # Real-time preprocessing
    rect6 = FancyBboxPatch((6.2, 8.5), 2, 1.3, boxstyle="round,pad=0.1", 
                           edgecolor='#F57F17', facecolor='#FFF9C4', linewidth=3)
    ax.add_patch(rect6)
    ax.text(7.2, 9.4, 'PREPROCESSING', fontsize=10, ha='center', fontweight='bold')
    ax.text(7.2, 9, 'Sliding Window', fontsize=9, ha='center')
    ax.text(7.2, 8.7, 'Buffer Management', fontsize=9, ha='center')
    
    # Arrow down
    arrow = FancyArrowPatch((7.2, 8.4), (7.2, 7.8), arrowstyle='->', mutation_scale=30, 
                           linewidth=3, color='#F57F17')
    ax.add_patch(arrow)
    
    # Model Loading
    rect7 = FancyBboxPatch((6.2, 6.3), 2, 1.3, boxstyle="round,pad=0.1", 
                           edgecolor='#7B1FA2', facecolor='#F3E5F5', linewidth=3)
    ax.add_patch(rect7)
    ax.text(7.2, 7.3, 'TRAINED MODEL', fontsize=10, ha='center', fontweight='bold')
    ax.text(7.2, 6.9, 'Loaded from Disk', fontsize=9, ha='center')
    ax.text(7.2, 6.6, 'TensorFlow .h5', fontsize=9, ha='center')
    
    # Arrow down
    arrow = FancyArrowPatch((7.2, 6.2), (7.2, 5.6), arrowstyle='->', mutation_scale=30, 
                           linewidth=3, color='#7B1FA2')
    ax.add_patch(arrow)
    
    # Inference
    rect8 = FancyBboxPatch((6.2, 4.1), 2, 1.3, boxstyle="round,pad=0.1", 
                           edgecolor='#00695C', facecolor='#C8E6C9', linewidth=3)
    ax.add_patch(rect8)
    ax.text(7.2, 5.1, 'INFERENCE', fontsize=10, ha='center', fontweight='bold')
    ax.text(7.2, 4.7, '< 500ms Latency', fontsize=9, ha='center', fontweight='bold', color='#D32F2F')
    ax.text(7.2, 4.4, 'Get Predictions', fontsize=9, ha='center')
    
    # Arrow down
    arrow = FancyArrowPatch((7.2, 4), (7.2, 3.4), arrowstyle='->', mutation_scale=30, 
                           linewidth=3, color='#00695C')
    ax.add_patch(arrow)
    
    # Cursor Smoothing
    rect9 = FancyBboxPatch((6.2, 1.9), 2, 1.3, boxstyle="round,pad=0.1", 
                           edgecolor='#E91E63', facecolor='#FCE4EC', linewidth=3)
    ax.add_patch(rect9)
    ax.text(7.2, 2.9, 'ACTION GENERATION', fontsize=10, ha='center', fontweight='bold')
    ax.text(7.2, 2.5, 'Cursor Movement', fontsize=9, ha='center')
    ax.text(7.2, 2.2, 'Click Actions', fontsize=9, ha='center')
    
    # Connection from ML to Inference
    arrow = FancyArrowPatch((2.4, 2.5), (6.2, 2.5), arrowstyle='->', mutation_scale=35, 
                           linewidth=4, color='#7B1FA2', linestyle='--')
    ax.add_patch(arrow)
    ax.text(4.3, 2.8, 'Trained Model', fontsize=9, ha='center', 
            bbox=dict(boxstyle='round', facecolor='#F3E5F5', alpha=0.9))
    
    # ====================== RIGHT SIDE: WEBAPP & DASHBOARD ======================
    
    ax.text(11.5, 10.2, 'WEBAPP & DASHBOARD', fontsize=13, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#1565C0', alpha=0.8, edgecolor='none'),
            color='white')
    
    # ---- Backend (Flask API) ----
    rect10 = FancyBboxPatch((10.2, 7.8), 2.6, 1.8, boxstyle="round,pad=0.1", 
                            edgecolor='#00897B', facecolor='#E0F2F1', linewidth=3)
    ax.add_patch(rect10)
    ax.text(11.5, 9.2, 'BACKEND API', fontsize=11, ha='center', fontweight='bold', color='#00695C')
    ax.text(11.5, 8.85, 'Flask Server', fontsize=9, ha='center')
    ax.text(11.5, 8.55, '• Model Loading', fontsize=8, ha='center')
    ax.text(11.5, 8.25, '• Prediction Service', fontsize=8, ha='center')
    ax.text(11.5, 7.95, '• WebSocket Handler', fontsize=8, ha='center')
    
    # Arrow from Inference to API
    arrow = FancyArrowPatch((8.2, 2.5), (10.2, 8.7), arrowstyle='->', mutation_scale=35, 
                           linewidth=3.5, color='#00695C')
    ax.add_patch(arrow)
    ax.text(9, 5, 'Real-Time Data', fontsize=9, ha='center', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#E0F2F1', alpha=0.9))
    
    # ---- Frontend Dashboard ----
    rect11 = FancyBboxPatch((13.2, 7.8), 2.6, 1.8, boxstyle="round,pad=0.1", 
                            edgecolor='#0277BD', facecolor='#B3E5FC', linewidth=3)
    ax.add_patch(rect11)
    ax.text(14.5, 9.2, 'FRONTEND DASHBOARD', fontsize=11, ha='center', fontweight='bold', color='#01579B')
    ax.text(14.5, 8.85, 'Web Interface', fontsize=9, ha='center')
    ax.text(14.5, 8.55, '• Real-Time Visualization', fontsize=8, ha='center')
    ax.text(14.5, 8.25, '• Live EEG Signal', fontsize=8, ha='center')
    ax.text(14.5, 7.95, '• Prediction Display', fontsize=8, ha='center')
    
    # Socket.IO Connection
    arrow1 = FancyArrowPatch((12.8, 8.7), (13.2, 8.7), arrowstyle='->', mutation_scale=25, 
                            linewidth=3, color='#1565C0')
    ax.add_patch(arrow1)
    arrow2 = FancyArrowPatch((13.2, 8.5), (12.8, 8.5), arrowstyle='->', mutation_scale=25, 
                            linewidth=3, color='#1565C0')
    ax.add_patch(arrow2)
    ax.text(13, 9.05, 'WebSocket', fontsize=8, ha='center', fontweight='bold', color='#1565C0')
    
    # ---- Database/Storage ----
    rect12 = FancyBboxPatch((10.2, 5.8), 2.6, 1.5, boxstyle="round,pad=0.1", 
                            edgecolor='#F57F17', facecolor='#FFECB3', linewidth=3)
    ax.add_patch(rect12)
    ax.text(11.5, 6.95, 'DATA STORAGE', fontsize=11, ha='center', fontweight='bold', color='#F57F17')
    ax.text(11.5, 6.55, '• Training History', fontsize=8, ha='center')
    ax.text(11.5, 6.25, '• Model Metadata', fontsize=8, ha='center')
    ax.text(11.5, 5.95, '• Session Logs', fontsize=8, ha='center')
    
    # Arrows
    arrow = FancyArrowPatch((11.5, 7.8), (11.5, 7.3), arrowstyle='->', mutation_scale=25, 
                           linewidth=2.5, color='#F57F17')
    ax.add_patch(arrow)
    
    # ---- Analytics & Monitoring ----
    rect13 = FancyBboxPatch((13.2, 5.8), 2.6, 1.5, boxstyle="round,pad=0.1", 
                            edgecolor='#C2185B', facecolor='#FCE4EC', linewidth=3)
    ax.add_patch(rect13)
    ax.text(14.5, 6.95, 'ANALYTICS', fontsize=11, ha='center', fontweight='bold', color='#C2185B')
    ax.text(14.5, 6.55, '• Performance Metrics', fontsize=8, ha='center')
    ax.text(14.5, 6.25, '• Model Accuracy', fontsize=8, ha='center')
    ax.text(14.5, 5.95, '• System Health', fontsize=8, ha='center')
    
    # Arrow
    arrow = FancyArrowPatch((14.5, 7.8), (14.5, 7.3), arrowstyle='->', mutation_scale=25, 
                           linewidth=2.5, color='#C2185B')
    ax.add_patch(arrow)
    
    # ====================== BOTTOM: USER INTERACTION ======================
    
    # Mouse/User Control
    rect14 = FancyBboxPatch((4.8, 0.2), 2, 1.2, boxstyle="round,pad=0.1", 
                            edgecolor='#D32F2F', facecolor='#FFCDD2', linewidth=3)
    ax.add_patch(rect14)
    ax.text(5.8, 0.95, 'SYSTEM OUTPUT', fontsize=10, ha='center', fontweight='bold', color='#B71C1C')
    ax.text(5.8, 0.55, 'Mouse Control & Clicks', fontsize=8, ha='center')
    
    # Arrow from action generation to mouse
    arrow = FancyArrowPatch((7.2, 1.9), (6.5, 1.4), arrowstyle='->', mutation_scale=30, 
                           linewidth=3, color='#D32F2F')
    ax.add_patch(arrow)
    
    # ====================== KEY INFORMATION BOXES ======================
    
    # Left info box
    info_text1 = """WORKFLOW:
1. Collect EEG Data (PhysioNet)
2. Preprocess & Augment
3. Train CNN-LSTM Model
4. Achieve 76.43% Accuracy
5. Save Trained Model"""
    
    rect_info1 = FancyBboxPatch((10.2, 3.8), 2.6, 1.8, boxstyle="round,pad=0.1", 
                                edgecolor='#7B1FA2', facecolor='#F3E5F5', linewidth=2, alpha=0.9)
    ax.add_patch(rect_info1)
    ax.text(11.5, 5.4, 'ML WORKFLOW', fontsize=9, ha='center', fontweight='bold', color='#7B1FA2')
    ax.text(11.5, 5.05, '1. Load EEG Data', fontsize=7, ha='center')
    ax.text(11.5, 4.75, '2. Preprocess Signals', fontsize=7, ha='center')
    ax.text(11.5, 4.45, '3. Train CNN-LSTM', fontsize=7, ha='center')
    ax.text(11.5, 4.15, '4. Evaluate Model', fontsize=7, ha='center')
    ax.text(11.5, 3.85, '5. Save & Deploy', fontsize=7, ha='center')
    
    # Right info box
    rect_info2 = FancyBboxPatch((13.2, 3.8), 2.6, 1.8, boxstyle="round,pad=0.1", 
                                edgecolor='#1565C0', facecolor='#E3F2FD', linewidth=2, alpha=0.9)
    ax.add_patch(rect_info2)
    ax.text(14.5, 5.4, 'REAL-TIME FLOW', fontsize=9, ha='center', fontweight='bold', color='#1565C0')
    ax.text(14.5, 5.05, '1. EEG Stream In', fontsize=7, ha='center')
    ax.text(14.5, 4.75, '2. Buffer & Process', fontsize=7, ha='center')
    ax.text(14.5, 4.45, '3. Predict Class', fontsize=7, ha='center')
    ax.text(14.5, 4.15, '4. Generate Action', fontsize=7, ha='center')
    ax.text(14.5, 3.85, '5. Display Results', fontsize=7, ha='center')
    
    # ====================== LEGEND ======================
    
    # Legend box
    ax.text(0.2, 0.9, 'TECHNOLOGY STACK', fontsize=10, fontweight='bold')
    ax.text(0.2, 0.5, '• ML: TensorFlow, Keras, Scikit-learn', fontsize=8)
    ax.text(0.2, 0.15, '• Backend: Flask, Socket.IO, Python', fontsize=8)
    
    ax.text(0.2, -0.3, '• Frontend: HTML5, JavaScript, Matplotlib', fontsize=8)
    ax.text(0.2, -0.65, '• Deployment: Docker, Docker-Compose', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(r'outputs\presentation_architecture_complete.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("✓ Presentation architecture saved: outputs\\presentation_architecture_complete.png")
    plt.close()

def create_ml_webapp_interaction_diagram():
    """Create a detailed interaction diagram between ML and WebApp."""
    
    fig = plt.figure(figsize=(18, 11))
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 11)
    ax.axis('off')
    
    # Title
    ax.text(9, 10.5, 'ML Model & WebApp Integration Flow', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(9, 10, 'How Machine Learning Powers Real-Time Brain-Computer Interface', 
            fontsize=12, ha='center', style='italic', color='#666')
    
    # ==================== LEFT: MODEL TRAINING PHASE ====================
    
    ax.text(1.5, 9.5, 'PHASE 1: TRAINING & DEPLOYMENT', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#7B1FA2', alpha=0.8, edgecolor='none'),
            color='white')
    
    # Training data
    rect = FancyBboxPatch((0.2, 8.2), 2.8, 0.9, boxstyle="round,pad=0.08", 
                          edgecolor='#1976D2', facecolor='#E3F2FD', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(1.6, 8.8, 'Load Training Data', fontsize=9, ha='center', fontweight='bold')
    ax.text(1.6, 8.45, 'PhysioNet: 109 subjects', fontsize=8, ha='center')
    
    # Arrow
    ax.annotate('', xy=(1.6, 7.95), xytext=(1.6, 8.2), 
                arrowprops=dict(arrowstyle='->', lw=2.5, color='#1976D2'))
    
    # Training
    rect = FancyBboxPatch((0.2, 6.5), 2.8, 1.3, boxstyle="round,pad=0.08", 
                          edgecolor='#F57F17', facecolor='#FFF9C4', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(1.6, 7.5, 'Train Model', fontsize=9, ha='center', fontweight='bold')
    ax.text(1.6, 7.1, 'CNN-LSTM Network', fontsize=8, ha='center')
    ax.text(1.6, 6.75, '50 epochs | Adam optimizer', fontsize=7, ha='center')
    
    # Arrow
    ax.annotate('', xy=(1.6, 6.25), xytext=(1.6, 6.5), 
                arrowprops=dict(arrowstyle='->', lw=2.5, color='#F57F17'))
    
    # Evaluation
    rect = FancyBboxPatch((0.2, 4.7), 2.8, 1.3, boxstyle="round,pad=0.08", 
                          edgecolor='#D32F2F', facecolor='#FFEBEE', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(1.6, 5.7, 'Evaluate & Validate', fontsize=9, ha='center', fontweight='bold')
    ax.text(1.6, 5.3, 'Accuracy: 76.43%', fontsize=8, ha='center', fontweight='bold')
    ax.text(1.6, 4.95, 'Generate Confusion Matrix', fontsize=7, ha='center')
    
    # Arrow
    ax.annotate('', xy=(1.6, 4.45), xytext=(1.6, 4.7), 
                arrowprops=dict(arrowstyle='->', lw=2.5, color='#D32F2F'))
    
    # Save Model
    rect = FancyBboxPatch((0.2, 2.8), 2.8, 1.3, boxstyle="round,pad=0.08", 
                          edgecolor='#00695C', facecolor='#C8E6C9', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(1.6, 3.8, 'Save Trained Model', fontsize=9, ha='center', fontweight='bold')
    ax.text(1.6, 3.4, 'TensorFlow .h5 Format', fontsize=8, ha='center')
    ax.text(1.6, 3.05, 'models/best_eeg_model.h5', fontsize=7, ha='center', family='monospace')
    
    # ==================== MIDDLE: MODEL DEPLOYMENT TO WEBAPP ====================
    
    ax.text(6, 9.5, 'PHASE 2: REAL-TIME INFERENCE', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#00695C', alpha=0.8, edgecolor='none'),
            color='white')
    
    # Deploy to API
    rect = FancyBboxPatch((4.5, 8.2), 3, 0.9, boxstyle="round,pad=0.08", 
                          edgecolor='#00897B', facecolor='#E0F2F1', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(6, 8.8, 'Deploy Model to Backend API', fontsize=9, ha='center', fontweight='bold')
    ax.text(6, 8.45, 'Flask loads .h5 on startup', fontsize=8, ha='center')
    
    # Connection from training to deployment
    arrow = FancyArrowPatch((3, 3.5), (4.5, 8.65), arrowstyle='->', mutation_scale=30, 
                           linewidth=3, color='#7B1FA2', linestyle='--')
    ax.add_patch(arrow)
    ax.text(3.7, 6, 'Trained Model', fontsize=8, ha='center', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#F3E5F5', alpha=0.9))
    
    # Arrow
    ax.annotate('', xy=(6, 7.95), xytext=(6, 8.2), 
                arrowprops=dict(arrowstyle='->', lw=2.5, color='#00897B'))
    
    # EEG Input from user
    rect = FancyBboxPatch((4.5, 6.5), 3, 1, boxstyle="round,pad=0.08", 
                          edgecolor='#1976D2', facecolor='#E3F2FD', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(6, 7.2, 'User with EEG Device', fontsize=9, ha='center', fontweight='bold')
    ax.text(6, 6.85, 'Real-time 64-channel EEG stream', fontsize=8, ha='center')
    
    # Arrow
    ax.annotate('', xy=(6, 6.25), xytext=(6, 6.5), 
                arrowprops=dict(arrowstyle='->', lw=2.5, color='#1976D2'))
    
    # Process & Predict
    rect = FancyBboxPatch((4.5, 4.5), 3, 1.5, boxstyle="round,pad=0.08", 
                          edgecolor='#7B1FA2', facecolor='#F3E5F5', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(6, 5.7, 'Process & Predict', fontsize=9, ha='center', fontweight='bold')
    ax.text(6, 5.3, '1. Preprocess EEG signal', fontsize=8, ha='center')
    ax.text(6, 5, '2. Run through model', fontsize=8, ha='center')
    ax.text(6, 4.7, '3. Get class prediction', fontsize=8, ha='center')
    
    # Arrow
    ax.annotate('', xy=(6, 4.25), xytext=(6, 4.5), 
                arrowprops=dict(arrowstyle='->', lw=2.5, color='#7B1FA2'))
    
    # Output Action
    rect = FancyBboxPatch((4.5, 2.8), 3, 1.3, boxstyle="round,pad=0.08", 
                          edgecolor='#E91E63', facecolor='#FCE4EC', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(6, 3.8, 'Generate Output Action', fontsize=9, ha='center', fontweight='bold')
    ax.text(6, 3.4, 'Map prediction to action:', fontsize=8, ha='center')
    ax.text(6, 3.05, 'Left/Right/Hands/Feet/Click', fontsize=7, ha='center')
    
    # ==================== RIGHT: WEBAPP DASHBOARD ====================
    
    ax.text(11.5, 9.5, 'PHASE 3: WEBAPP & VISUALIZATION', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#1565C0', alpha=0.8, edgecolor='none'),
            color='white')
    
    # Connection from API to Dashboard
    arrow = FancyArrowPatch((7.5, 3.5), (10.5, 8.2), arrowstyle='->', mutation_scale=30, 
                           linewidth=3, color='#00695C')
    ax.add_patch(arrow)
    ax.text(9, 5.5, 'WebSocket\nReal-Time', fontsize=8, ha='center', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#E0F2F1', alpha=0.9))
    
    # Backend API Server
    rect = FancyBboxPatch((10.5, 8.2), 3, 0.9, boxstyle="round,pad=0.08", 
                          edgecolor='#00897B', facecolor='#E0F2F1', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(12, 8.8, 'Flask Backend Server', fontsize=9, ha='center', fontweight='bold')
    ax.text(12, 8.45, 'Port 5000 | Socket.IO enabled', fontsize=8, ha='center')
    
    # Arrow
    ax.annotate('', xy=(12, 7.95), xytext=(12, 8.2), 
                arrowprops=dict(arrowstyle='->', lw=2.5, color='#00897B'))
    
    # Frontend Dashboard
    rect = FancyBboxPatch((10.5, 6.5), 3, 1.3, boxstyle="round,pad=0.08", 
                          edgecolor='#0277BD', facecolor='#B3E5FC', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(12, 7.5, 'Web Dashboard', fontsize=9, ha='center', fontweight='bold')
    ax.text(12, 7.1, 'Real-time EEG visualization', fontsize=8, ha='center')
    ax.text(12, 6.75, 'Live prediction display', fontsize=8, ha='center')
    
    # Arrow
    ax.annotate('', xy=(12, 6.25), xytext=(12, 6.5), 
                arrowprops=dict(arrowstyle='->', lw=2.5, color='#0277BD'))
    
    # System Output
    rect = FancyBboxPatch((10.5, 4.5), 3, 1.5, boxstyle="round,pad=0.08", 
                          edgecolor='#F57F17', facecolor='#FFF9C4', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(12, 5.7, 'System Output', fontsize=9, ha='center', fontweight='bold')
    ax.text(12, 5.3, '• Mouse cursor movement', fontsize=8, ha='center')
    ax.text(12, 5, '• Click commands', fontsize=8, ha='center')
    ax.text(12, 4.7, '• Visual feedback', fontsize=8, ha='center')
    
    # Arrow
    ax.annotate('', xy=(12, 4.25), xytext=(12, 4.5), 
                arrowprops=dict(arrowstyle='->', lw=2.5, color='#F57F17'))
    
    # Feedback Loop
    rect = FancyBboxPatch((10.5, 2.8), 3, 1.3, boxstyle="round,pad=0.08", 
                          edgecolor='#D32F2F', facecolor='#FFCDD2', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(12, 3.8, 'User Sees Result', fontsize=9, ha='center', fontweight='bold')
    ax.text(12, 3.4, 'Dashboard updates with:', fontsize=8, ha='center')
    ax.text(12, 3.05, 'action, confidence, metrics', fontsize=7, ha='center')
    
    # Feedback arrow back to input
    arrow = FancyArrowPatch((13.5, 7), (8, 6.8), arrowstyle='->', mutation_scale=25, 
                           linewidth=2.5, color='#666', linestyle=':', alpha=0.6)
    ax.add_patch(arrow)
    ax.text(10.7, 6.5, 'User Feedback Loop', fontsize=7, ha='center', style='italic', color='#666')
    
    # ==================== BOTTOM: KEY METRICS & STATS ====================
    
    # Performance Metrics
    rect = FancyBboxPatch((0.2, 0.2), 4.3, 2.3, boxstyle="round,pad=0.08", 
                          edgecolor='#D32F2F', facecolor='#FFEBEE', linewidth=2)
    ax.add_patch(rect)
    ax.text(2.35, 2.35, 'MODEL PERFORMANCE', fontsize=10, ha='center', fontweight='bold', color='#D32F2F')
    ax.text(0.5, 2, 'Accuracy: 76.43%', fontsize=9, ha='left', fontweight='bold')
    ax.text(0.5, 1.6, '• Precision: 75.9%', fontsize=8, ha='left')
    ax.text(0.5, 1.25, '• Recall: 76%', fontsize=8, ha='left')
    ax.text(0.5, 0.9, '• 5-class classification', fontsize=8, ha='left')
    ax.text(0.5, 0.55, '• 64 EEG channels, 320 samples', fontsize=8, ha='left')
    
    # Real-time Performance
    rect = FancyBboxPatch((4.8, 0.2), 4.3, 2.3, boxstyle="round,pad=0.08", 
                          edgecolor='#00695C', facecolor='#C8E6C9', linewidth=2)
    ax.add_patch(rect)
    ax.text(6.95, 2.35, 'REAL-TIME PERFORMANCE', fontsize=10, ha='center', fontweight='bold', color='#00695C')
    ax.text(5.1, 2, 'Latency: < 500ms', fontsize=9, ha='left', fontweight='bold')
    ax.text(5.1, 1.6, '• Buffer size: 64 samples', fontsize=8, ha='left')
    ax.text(5.1, 1.25, '• Update rate: 25 FPS', fontsize=8, ha='left')
    ax.text(5.1, 0.9, '• Sliding window processing', fontsize=8, ha='left')
    ax.text(5.1, 0.55, '• Exponential smoothing enabled', fontsize=8, ha='left')
    
    # System Architecture
    rect = FancyBboxPatch((9.4, 0.2), 4.3, 2.3, boxstyle="round,pad=0.08", 
                          edgecolor='#1565C0', facecolor='#E3F2FD', linewidth=2)
    ax.add_patch(rect)
    ax.text(11.55, 2.35, 'SYSTEM ARCHITECTURE', fontsize=10, ha='center', fontweight='bold', color='#1565C0')
    ax.text(9.6, 2, 'Framework: Flask + Socket.IO', fontsize=9, ha='left', fontweight='bold')
    ax.text(9.6, 1.6, '• Backend: Python 3.8+', fontsize=8, ha='left')
    ax.text(9.6, 1.25, '• ML: TensorFlow/Keras', fontsize=8, ha='left')
    ax.text(9.6, 0.9, '• Frontend: HTML5/JavaScript', fontsize=8, ha='left')
    ax.text(9.6, 0.55, '• Deployment: Docker', fontsize=8, ha='left')
    
    # Tech Stack
    rect = FancyBboxPatch((13.9, 0.2), 4.3, 2.3, boxstyle="round,pad=0.08", 
                          edgecolor='#7B1FA2', facecolor='#F3E5F5', linewidth=2)
    ax.add_patch(rect)
    ax.text(16.05, 2.35, 'TECH STACK', fontsize=10, ha='center', fontweight='bold', color='#7B1FA2')
    ax.text(14.1, 2, 'Core Libraries:', fontsize=9, ha='left', fontweight='bold')
    ax.text(14.1, 1.6, '• NumPy, Pandas, Scikit-learn', fontsize=8, ha='left')
    ax.text(14.1, 1.25, '• Matplotlib, SciPy', fontsize=8, ha='left')
    ax.text(14.1, 0.9, '• MNE-Python (EEG processing)', fontsize=8, ha='left')
    ax.text(14.1, 0.55, '• PyAutoGUI (mouse control)', fontsize=8, ha='left')
    
    plt.tight_layout()
    plt.savefig(r'outputs\ml_webapp_integration_flow.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("✓ ML-WebApp integration flow saved: outputs\\ml_webapp_integration_flow.png")
    plt.close()

def create_system_components_diagram():
    """Create a detailed system components interaction diagram."""
    
    fig = plt.figure(figsize=(18, 12))
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(9, 11.5, 'Complete System Components & Data Flow', 
            fontsize=20, fontweight='bold', ha='center')
    
    # ==================== TOP: DATA SOURCES ====================
    
    ax.text(1.5, 10.8, 'DATA SOURCES', fontsize=10, fontweight='bold', color='#1976D2')
    
    # PhysioNet
    circle = Circle((1.5, 10.2), 0.3, color='#BBDEFB', ec='#1976D2', linewidth=2)
    ax.add_patch(circle)
    ax.text(1.5, 10.2, '1', fontsize=12, ha='center', va='center', fontweight='bold')
    ax.text(1.5, 9.7, 'PhysioNet\nDatabase', fontsize=8, ha='center')
    
    # Real-time EEG
    circle = Circle((4, 10.2), 0.3, color='#BBDEFB', ec='#1976D2', linewidth=2)
    ax.add_patch(circle)
    ax.text(4, 10.2, '2', fontsize=12, ha='center', va='center', fontweight='bold')
    ax.text(4, 9.7, 'Real-Time\nEEG Sensors', fontsize=8, ha='center')
    
    # Synthetic Data
    circle = Circle((6.5, 10.2), 0.3, color='#BBDEFB', ec='#1976D2', linewidth=2)
    ax.add_patch(circle)
    ax.text(6.5, 10.2, '3', fontsize=12, ha='center', va='center', fontweight='bold')
    ax.text(6.5, 9.7, 'Synthetic\nData', fontsize=8, ha='center')
    
    # ==================== MIDDLE-TOP: PROCESSING LAYER ====================
    
    ax.text(1.5, 8.8, 'DATA PROCESSING & ML LAYER', fontsize=10, fontweight='bold', color='#F57F17')
    
    # Data Loader
    rect = FancyBboxPatch((0.5, 7.5), 1.8, 1, boxstyle="round,pad=0.08", 
                          edgecolor='#F57F17', facecolor='#FFF9C4', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(1.4, 8.2, 'Data Loader', fontsize=9, ha='center', fontweight='bold')
    ax.text(1.4, 7.8, 'src/data_loader.py', fontsize=7, ha='center', family='monospace')
    
    # Preprocessing
    rect = FancyBboxPatch((2.6, 7.5), 1.8, 1, boxstyle="round,pad=0.08", 
                          edgecolor='#F57F17', facecolor='#FFF9C4', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(3.5, 8.2, 'Preprocessing', fontsize=9, ha='center', fontweight='bold')
    ax.text(3.5, 7.8, 'src/preprocessing.py', fontsize=7, ha='center', family='monospace')
    
    # Data Preparation
    rect = FancyBboxPatch((4.7, 7.5), 1.8, 1, boxstyle="round,pad=0.08", 
                          edgecolor='#F57F17', facecolor='#FFF9C4', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(5.6, 8.2, 'Preparation', fontsize=9, ha='center', fontweight='bold')
    ax.text(5.6, 7.8, 'src/data_preparation.py', fontsize=7, ha='center', family='monospace')
    
    # Model
    rect = FancyBboxPatch((6.8, 7.5), 1.8, 1, boxstyle="round,pad=0.08", 
                          edgecolor='#7B1FA2', facecolor='#F3E5F5', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(7.7, 8.2, 'CNN-LSTM Model', fontsize=9, ha='center', fontweight='bold')
    ax.text(7.7, 7.8, 'src/model.py', fontsize=7, ha='center', family='monospace')
    
    # Training
    rect = FancyBboxPatch((8.9, 7.5), 1.8, 1, boxstyle="round,pad=0.08", 
                          edgecolor='#7B1FA2', facecolor='#F3E5F5', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(9.8, 8.2, 'Training Module', fontsize=9, ha='center', fontweight='bold')
    ax.text(9.8, 7.8, 'src/train.py', fontsize=7, ha='center', family='monospace')
    
    # Evaluation
    rect = FancyBboxPatch((11, 7.5), 1.8, 1, boxstyle="round,pad=0.08", 
                          edgecolor='#D32F2F', facecolor='#FFEBEE', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(11.9, 8.2, 'Evaluation', fontsize=9, ha='center', fontweight='bold')
    ax.text(11.9, 7.8, 'src/evaluate.py', fontsize=7, ha='center', family='monospace')
    
    # Model Manager
    rect = FancyBboxPatch((12.1, 7.5), 1.8, 1, boxstyle="round,pad=0.08", 
                          edgecolor='#00695C', facecolor='#C8E6C9', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(13, 8.2, 'Model Manager', fontsize=9, ha='center', fontweight='bold')
    ax.text(13, 7.8, 'src/model_manager.py', fontsize=7, ha='center', family='monospace')
    
    # Config
    rect = FancyBboxPatch((14.2, 7.5), 1.8, 1, boxstyle="round,pad=0.08", 
                          edgecolor='#1565C0', facecolor='#E3F2FD', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(15.1, 8.2, 'Config Manager', fontsize=9, ha='center', fontweight='bold')
    ax.text(15.1, 7.8, 'src/config.py', fontsize=7, ha='center', family='monospace')
    
    # Arrows from data sources to processing
    for x_start in [1.5, 4, 6.5]:
        ax.annotate('', xy=(1.4, 8.5), xytext=(x_start, 9.9), 
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='#999', alpha=0.5))
    
    # ==================== MIDDLE: INFERENCE LAYER ====================
    
    ax.text(1.5, 6.8, 'REAL-TIME INFERENCE ENGINE', fontsize=10, fontweight='bold', color='#00695C')
    
    # Realtime Engine
    rect = FancyBboxPatch((0.5, 5.2), 2.2, 1.3, boxstyle="round,pad=0.08", 
                          edgecolor='#00695C', facecolor='#C8E6C9', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(1.6, 6.2, 'Realtime\nInference Engine', fontsize=9, ha='center', fontweight='bold')
    ax.text(1.6, 5.6, 'src/realtime_inference.py', fontsize=7, ha='center', family='monospace')
    
    # Click Detection
    rect = FancyBboxPatch((3, 5.2), 2.2, 1.3, boxstyle="round,pad=0.08", 
                          edgecolor='#E91E63', facecolor='#FCE4EC', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(4.1, 6.2, 'Click\nDetection', fontsize=9, ha='center', fontweight='bold')
    ax.text(4.1, 5.6, 'src/click_detection.py', fontsize=7, ha='center', family='monospace')
    
    # Backend API
    rect = FancyBboxPatch((5.5, 5.2), 2.2, 1.3, boxstyle="round,pad=0.08", 
                          edgecolor='#00897B', facecolor='#E0F2F1', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(6.6, 6.2, 'Flask Backend\nAPI Server', fontsize=9, ha='center', fontweight='bold')
    ax.text(6.6, 5.6, 'Port 5000', fontsize=7, ha='center')
    
    # Frontend Dashboard
    rect = FancyBboxPatch((8, 5.2), 2.2, 1.3, boxstyle="round,pad=0.08", 
                          edgecolor='#0277BD', facecolor='#B3E5FC', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(9.1, 6.2, 'Web Dashboard\nFrontend', fontsize=9, ha='center', fontweight='bold')
    ax.text(9.1, 5.6, 'HTML5 + JavaScript', fontsize=7, ha='center')
    
    # Mouse Controller
    rect = FancyBboxPatch((10.5, 5.2), 2.2, 1.3, boxstyle="round,pad=0.08", 
                          edgecolor='#D32F2F', facecolor='#FFCDD2', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(11.6, 6.2, 'Mouse\nController', fontsize=9, ha='center', fontweight='bold')
    ax.text(11.6, 5.6, 'PyAutoGUI', fontsize=7, ha='center')
    
    # Utils
    rect = FancyBboxPatch((13, 5.2), 2.2, 1.3, boxstyle="round,pad=0.08", 
                          edgecolor='#666', facecolor='#E8E8E8', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(14.1, 6.2, 'Utilities &\nLogging', fontsize=9, ha='center', fontweight='bold')
    ax.text(14.1, 5.6, 'src/utils.py', fontsize=7, ha='center', family='monospace')
    
    # Arrows connecting inference components
    connections = [
        (2.7, 5.85),  # Engine to Click
        (4, 5.85),    # Click to Backend
        (7.7, 5.85),  # Backend to Frontend
        (10.2, 5.85), # Frontend to Mouse
    ]
    for i in range(len(connections)-1):
        ax.annotate('', xy=connections[i+1], xytext=(connections[i][0]+1.1, connections[i][1]), 
                    arrowprops=dict(arrowstyle='->', lw=2, color='#00695C'))
    
    # Arrow from Model Manager to Inference
    ax.annotate('', xy=(1.6, 6.5), xytext=(13, 7.5), 
                arrowprops=dict(arrowstyle='->', lw=2.5, color='#7B1FA2', linestyle='--'))
    ax.text(8.5, 7.1, 'Load Trained Model', fontsize=8, ha='center', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#F3E5F5', alpha=0.8))
    
    # ==================== BOTTOM: STORAGE & OUTPUT ====================
    
    ax.text(1.5, 4.5, 'STORAGE & OUTPUT', fontsize=10, fontweight='bold', color='#F57F17')
    
    # Model Storage
    rect = FancyBboxPatch((0.5, 2.8), 2.2, 1.3, boxstyle="round,pad=0.08", 
                          edgecolor='#F57F17', facecolor='#FFE0B2', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(1.6, 3.8, 'Model Storage', fontsize=9, ha='center', fontweight='bold')
    ax.text(1.6, 3.35, 'models/', fontsize=8, ha='center', family='monospace')
    ax.text(1.6, 3.05, '.h5 format', fontsize=7, ha='center')
    
    # Results & Outputs
    rect = FancyBboxPatch((3, 2.8), 2.2, 1.3, boxstyle="round,pad=0.08", 
                          edgecolor='#D32F2F', facecolor='#FFEBEE', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(4.1, 3.8, 'Results & Outputs', fontsize=9, ha='center', fontweight='bold')
    ax.text(4.1, 3.35, 'outputs/', fontsize=8, ha='center', family='monospace')
    ax.text(4.1, 3.05, 'Metrics, Curves', fontsize=7, ha='center')
    
    # Database
    rect = FancyBboxPatch((5.5, 2.8), 2.2, 1.3, boxstyle="round,pad=0.08", 
                          edgecolor='#00796B', facecolor='#E0F2F1', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(6.6, 3.8, 'Database', fontsize=9, ha='center', fontweight='bold')
    ax.text(6.6, 3.35, 'Training History', fontsize=8, ha='center')
    ax.text(6.6, 3.05, 'Metadata', fontsize=7, ha='center')
    
    # Logs
    rect = FancyBboxPatch((8, 2.8), 2.2, 1.3, boxstyle="round,pad=0.08", 
                          edgecolor='#1565C0', facecolor='#E3F2FD', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(9.1, 3.8, 'Application Logs', fontsize=9, ha='center', fontweight='bold')
    ax.text(9.1, 3.35, 'logs/', fontsize=8, ha='center', family='monospace')
    ax.text(9.1, 3.05, '.log files', fontsize=7, ha='center')
    
    # Deployment
    rect = FancyBboxPatch((10.5, 2.8), 2.2, 1.3, boxstyle="round,pad=0.08", 
                          edgecolor='#558B2F', facecolor='#F1F8E9', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(11.6, 3.8, 'Deployment', fontsize=9, ha='center', fontweight='bold')
    ax.text(11.6, 3.35, 'Docker', fontsize=8, ha='center')
    ax.text(11.6, 3.05, 'docker-compose.yml', fontsize=7, ha='center')
    
    # User Output
    rect = FancyBboxPatch((13, 2.8), 2.2, 1.3, boxstyle="round,pad=0.08", 
                          edgecolor='#D32F2F', facecolor='#FFCDD2', linewidth=2.5)
    ax.add_patch(rect)
    ax.text(14.1, 3.8, 'System Output', fontsize=9, ha='center', fontweight='bold')
    ax.text(14.1, 3.35, 'Mouse Commands', fontsize=8, ha='center')
    ax.text(14.1, 3.05, 'Clicks, Movement', fontsize=7, ha='center')
    
    # Arrows from Inference to Storage
    ax.annotate('', xy=(1.6, 4.1), xytext=(1.6, 5.2), 
                arrowprops=dict(arrowstyle='->', lw=2, color='#F57F17'))
    ax.annotate('', xy=(4.1, 4.1), xytext=(9.1, 5.2), 
                arrowprops=dict(arrowstyle='->', lw=2, color='#D32F2F'))
    ax.annotate('', xy=(14.1, 4.1), xytext=(11.6, 5.2), 
                arrowprops=dict(arrowstyle='->', lw=2, color='#D32F2F'))
    
    # ==================== FOOTER: STATS ====================
    
    stats_text = """
    PERFORMANCE METRICS                    REAL-TIME SPECS                        DEPLOYMENT OPTIONS
    ✓ Accuracy: 76.43%                     ✓ Latency: <500ms                      ✓ Docker Container
    ✓ 5-Class Classification              ✓ Buffer: 64 samples                   ✓ Docker Compose
    ✓ 64 EEG Channels                      ✓ Update Rate: 25 FPS                  ✓ Local Machine
    ✓ 320 Sample Window                    ✓ Smoothing: Exponential               ✓ Cloud Deployment
    """
    
    ax.text(9, 1.3, stats_text, fontsize=7, ha='center', va='center', family='monospace',
            bbox=dict(boxstyle='round', facecolor='#F5F5F5', alpha=0.9, edgecolor='#999', linewidth=1))
    
    plt.tight_layout()
    plt.savefig(r'outputs\system_components_detailed.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("✓ System components diagram saved: outputs\\system_components_detailed.png")
    plt.close()

if __name__ == '__main__':
    print("Generating Presentation-Style Architecture Diagrams...\n")
    
    create_presentation_overview()
    create_ml_webapp_interaction_diagram()
    create_system_components_diagram()
    
    print("\n" + "="*80)
    print("PRESENTATION DIAGRAMS GENERATED SUCCESSFULLY")
    print("="*80)
    print("\nGenerated Files:")
    print("  ✓ outputs\\presentation_architecture_complete.png")
    print("  ✓ outputs\\ml_webapp_integration_flow.png")
    print("  ✓ outputs\\system_components_detailed.png")
    print("\n" + "="*80)
    print("\nThese diagrams are perfect for:")
    print("  • Presentations and stakeholder meetings")
    print("  • Documentation and GitHub README")
    print("  • Project proposals and reports")
    print("  • Team training and onboarding")
    print("="*80)
