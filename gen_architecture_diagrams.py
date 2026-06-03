#!/usr/bin/env python
"""Generate comprehensive project architecture diagram."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

def create_architecture_diagram():
    """Create a comprehensive architecture diagram for the BCI Interface project."""
    
    fig = plt.figure(figsize=(18, 14))
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(5, 11.5, 'BCI Interface - Complete System Architecture', 
            fontsize=18, fontweight='bold', ha='center')
    
    # Color scheme
    color_data = '#E3F2FD'
    color_core = '#FFF3E0'
    color_ml = '#F3E5F5'
    color_inference = '#E8F5E9'
    color_output = '#FCE4EC'
    color_infra = '#F1F8E9'
    
    # ================= DATA INPUT LAYER =================
    ax.text(0.5, 10.8, '📊 DATA INPUT LAYER', fontsize=11, fontweight='bold')
    
    # PhysioNet
    rect1 = FancyBboxPatch((0.1, 10.2), 1.8, 0.5, boxstyle="round,pad=0.05", 
                           edgecolor='#1976D2', facecolor=color_data, linewidth=2)
    ax.add_patch(rect1)
    ax.text(1, 10.45, 'PhysioNet\nEEG Database\n(109 Subjects)', 
            fontsize=9, ha='center', va='center', fontweight='bold')
    
    # Synthetic Data
    rect2 = FancyBboxPatch((2.3, 10.2), 1.8, 0.5, boxstyle="round,pad=0.05", 
                           edgecolor='#1976D2', facecolor=color_data, linewidth=2)
    ax.add_patch(rect2)
    ax.text(3.2, 10.45, 'Synthetic\nEEG Data\nGeneration', 
            fontsize=9, ha='center', va='center', fontweight='bold')
    
    # Real-Time EEG
    rect3 = FancyBboxPatch((4.5, 10.2), 1.8, 0.5, boxstyle="round,pad=0.05", 
                           edgecolor='#1976D2', facecolor=color_data, linewidth=2)
    ax.add_patch(rect3)
    ax.text(5.4, 10.45, 'Real-Time\nEEG Sensors\n(64 Channels)', 
            fontsize=9, ha='center', va='center', fontweight='bold')
    
    # ================= DATA PROCESSING LAYER =================
    ax.text(0.5, 9.5, '⚙️ DATA PROCESSING LAYER', fontsize=11, fontweight='bold')
    
    # Data Loader
    rect4 = FancyBboxPatch((0.1, 8.5), 1.5, 0.8, boxstyle="round,pad=0.05", 
                           edgecolor='#F57F17', facecolor=color_core, linewidth=2)
    ax.add_patch(rect4)
    ax.text(0.85, 8.9, 'Data Loader\nsrc/data_loader.py\n(Load & Validate)', 
            fontsize=8, ha='center', va='center')
    
    # Preprocessing
    rect5 = FancyBboxPatch((1.8, 8.5), 1.5, 0.8, boxstyle="round,pad=0.05", 
                           edgecolor='#F57F17', facecolor=color_core, linewidth=2)
    ax.add_patch(rect5)
    ax.text(2.55, 8.9, 'Preprocessing\nsrc/preprocessing.py\n(Filter, Normalize)', 
            fontsize=8, ha='center', va='center')
    
    # Data Preparation
    rect6 = FancyBboxPatch((3.5, 8.5), 1.5, 0.8, boxstyle="round,pad=0.05", 
                           edgecolor='#F57F17', facecolor=color_core, linewidth=2)
    ax.add_patch(rect6)
    ax.text(4.25, 8.9, 'Data Preparation\nsrc/data_preparation.py\n(Window, Split)', 
            fontsize=8, ha='center', va='center')
    
    # Data Augmentation
    rect7 = FancyBboxPatch((5.2, 8.5), 1.5, 0.8, boxstyle="round,pad=0.05", 
                           edgecolor='#F57F17', facecolor=color_core, linewidth=2)
    ax.add_patch(rect7)
    ax.text(5.95, 8.9, 'Data Augmentation\n(Time Shift, Scale)\n(Improve Robustness)', 
            fontsize=8, ha='center', va='center')
    
    # ================= CORE ML LAYER =================
    ax.text(0.5, 7.8, '🧠 CORE ML LAYER', fontsize=11, fontweight='bold')
    
    # CNN-LSTM Model
    rect8 = FancyBboxPatch((0.5, 6.2), 2.5, 1.4, boxstyle="round,pad=0.08", 
                           edgecolor='#7B1FA2', facecolor=color_ml, linewidth=2.5)
    ax.add_patch(rect8)
    ax.text(1.75, 7.3, 'CNN-LSTM Model', fontsize=10, ha='center', fontweight='bold')
    ax.text(1.75, 6.95, '5-Class Architecture', fontsize=8, ha='center')
    ax.text(1.75, 6.65, '• Conv1D (3 blocks)', fontsize=7, ha='center')
    ax.text(1.75, 6.4, '• Bidirectional LSTM', fontsize=7, ha='center')
    
    # Training Pipeline
    rect9 = FancyBboxPatch((3.3, 6.2), 2.5, 1.4, boxstyle="round,pad=0.08", 
                           edgecolor='#7B1FA2', facecolor=color_ml, linewidth=2.5)
    ax.add_patch(rect9)
    ax.text(4.55, 7.3, 'Training Pipeline', fontsize=10, ha='center', fontweight='bold')
    ax.text(4.55, 6.95, 'src/train.py', fontsize=8, ha='center')
    ax.text(4.55, 6.65, '• Early Stopping', fontsize=7, ha='center')
    ax.text(4.55, 6.4, '• Learning Rate Decay', fontsize=7, ha='center')
    
    # Evaluation & Metrics
    rect10 = FancyBboxPatch((6.1, 6.2), 2.5, 1.4, boxstyle="round,pad=0.08", 
                            edgecolor='#7B1FA2', facecolor=color_ml, linewidth=2.5)
    ax.add_patch(rect10)
    ax.text(7.35, 7.3, 'Evaluation Module', fontsize=10, ha='center', fontweight='bold')
    ax.text(7.35, 6.95, 'src/evaluate.py', fontsize=8, ha='center')
    ax.text(7.35, 6.65, '• Confusion Matrix', fontsize=7, ha='center')
    ax.text(7.35, 6.4, '• Accuracy: 76.43%', fontsize=7, ha='center', color='#D32F2F')
    
    # ================= MODEL MANAGEMENT =================
    ax.text(0.5, 5.7, '💾 MODEL MANAGEMENT', fontsize=11, fontweight='bold')
    
    # Model Manager
    rect11 = FancyBboxPatch((0.5, 4.7), 2.5, 0.9, boxstyle="round,pad=0.05", 
                            edgecolor='#00796B', facecolor='#E0F2F1', linewidth=2)
    ax.add_patch(rect11)
    ax.text(1.75, 5.25, 'Model Manager', fontsize=9, ha='center', fontweight='bold')
    ax.text(1.75, 4.95, 'src/model_manager.py\n(Save, Load, Version)', 
            fontsize=7, ha='center', va='center')
    
    # Config Manager
    rect12 = FancyBboxPatch((3.3, 4.7), 2.5, 0.9, boxstyle="round,pad=0.05", 
                            edgecolor='#00796B', facecolor='#E0F2F1', linewidth=2)
    ax.add_patch(rect12)
    ax.text(4.55, 5.25, 'Config Management', fontsize=9, ha='center', fontweight='bold')
    ax.text(4.55, 4.95, 'src/config.py\n(YAML + Environment)', 
            fontsize=7, ha='center', va='center')
    
    # ================= INFERENCE LAYER =================
    ax.text(0.5, 4.1, '⚡ INFERENCE LAYER', fontsize=11, fontweight='bold')
    
    # Real-Time Inference
    rect13 = FancyBboxPatch((0.5, 2.5), 2.8, 1.4, boxstyle="round,pad=0.08", 
                            edgecolor='#00695C', facecolor=color_inference, linewidth=2.5)
    ax.add_patch(rect13)
    ax.text(1.9, 3.65, 'Real-Time Inference', fontsize=9, ha='center', fontweight='bold')
    ax.text(1.9, 3.35, 'src/realtime_inference.py', fontsize=7, ha='center')
    ax.text(1.9, 3.05, '• <500ms latency', fontsize=7, ha='center')
    ax.text(1.9, 2.8, '• Buffer management', fontsize=7, ha='center')
    
    # Cursor Smoother
    rect14 = FancyBboxPatch((3.6, 2.5), 2.8, 1.4, boxstyle="round,pad=0.08", 
                            edgecolor='#00695C', facecolor=color_inference, linewidth=2.5)
    ax.add_patch(rect14)
    ax.text(5, 3.65, 'Cursor Smoother', fontsize=9, ha='center', fontweight='bold')
    ax.text(5, 3.35, 'Exponential Smoothing', fontsize=7, ha='center')
    ax.text(5, 3.05, '• Natural movement', fontsize=7, ha='center')
    ax.text(5, 2.8, '• Position history', fontsize=7, ha='center')
    
    # BCI Controller
    rect15 = FancyBboxPatch((6.7, 2.5), 2.8, 1.4, boxstyle="round,pad=0.08", 
                            edgecolor='#00695C', facecolor=color_inference, linewidth=2.5)
    ax.add_patch(rect15)
    ax.text(8.1, 3.65, 'BCI Mouse Controller', fontsize=9, ha='center', fontweight='bold')
    ax.text(8.1, 3.35, 'Mouse Action Mapping', fontsize=7, ha='center')
    ax.text(8.1, 3.05, '• 5-class to actions', fontsize=7, ha='center')
    ax.text(8.1, 2.8, '• Confidence based', fontsize=7, ha='center')
    
    # ================= OUTPUT & APPLICATIONS =================
    ax.text(0.5, 2, '📲 OUTPUT & APPLICATIONS', fontsize=11, fontweight='bold')
    
    # Mouse Control
    rect16 = FancyBboxPatch((0.5, 0.8), 1.8, 1, boxstyle="round,pad=0.05", 
                            edgecolor='#C2185B', facecolor=color_output, linewidth=2)
    ax.add_patch(rect16)
    ax.text(1.4, 1.5, 'Mouse Control', fontsize=9, ha='center', fontweight='bold')
    ax.text(1.4, 1.1, 'Cursor Movement\nClick Actions', fontsize=7, ha='center')
    
    # Live Dashboard
    rect17 = FancyBboxPatch((2.6, 0.8), 1.8, 1, boxstyle="round,pad=0.05", 
                            edgecolor='#C2185B', facecolor=color_output, linewidth=2)
    ax.add_patch(rect17)
    ax.text(3.5, 1.5, 'Web Dashboard', fontsize=9, ha='center', fontweight='bold')
    ax.text(3.5, 1.1, 'Flask + Socket.IO\nReal-time Viz', fontsize=7, ha='center')
    
    # Data Visualization
    rect18 = FancyBboxPatch((4.7, 0.8), 1.8, 1, boxstyle="round,pad=0.05", 
                            edgecolor='#C2185B', facecolor=color_output, linewidth=2)
    ax.add_patch(rect18)
    ax.text(5.6, 1.5, 'Visualization', fontsize=9, ha='center', fontweight='bold')
    ax.text(5.6, 1.1, 'Training Curves\nConfusion Matrix', fontsize=7, ha='center')
    
    # Logs & Records
    rect19 = FancyBboxPatch((6.8, 0.8), 1.8, 1, boxstyle="round,pad=0.05", 
                            edgecolor='#C2185B', facecolor=color_output, linewidth=2)
    ax.add_patch(rect19)
    ax.text(7.7, 1.5, 'Logs & Storage', fontsize=9, ha='center', fontweight='bold')
    ax.text(7.7, 1.1, 'Training History\nMetadata', fontsize=7, ha='center')
    
    # ================= ARROWS - Data Flow =================
    arrow_props = dict(arrowstyle='->', lw=2.5, color='#1976D2')
    
    # Input to Processing
    ax.annotate('', xy=(0.85, 9.3), xytext=(0.85, 10.2), 
                arrowprops=dict(arrowstyle='->', lw=2, color='#1976D2'))
    ax.annotate('', xy=(3.2, 9.3), xytext=(3.2, 10.2), 
                arrowprops=dict(arrowstyle='->', lw=2, color='#1976D2'))
    ax.annotate('', xy=(5.4, 9.3), xytext=(5.4, 10.2), 
                arrowprops=dict(arrowstyle='->', lw=2, color='#1976D2'))
    
    # Processing to ML
    ax.annotate('', xy=(1.75, 7.6), xytext=(2.55, 9.3), 
                arrowprops=dict(arrowstyle='->', lw=2.5, color='#F57C00'))
    ax.annotate('', xy=(4.55, 7.6), xytext=(4.25, 9.3), 
                arrowprops=dict(arrowstyle='->', lw=2.5, color='#F57C00'))
    
    # ML to Inference
    ax.annotate('', xy=(1.9, 3.9), xytext=(2, 6.2), 
                arrowprops=dict(arrowstyle='->', lw=2.5, color='#7B1FA2'))
    ax.annotate('', xy=(5, 3.9), xytext=(6.5, 6.2), 
                arrowprops=dict(arrowstyle='->', lw=2.5, color='#7B1FA2'))
    
    # Inference to Output
    ax.annotate('', xy=(1.4, 1.8), xytext=(1.9, 2.5), 
                arrowprops=dict(arrowstyle='->', lw=2, color='#00695C'))
    ax.annotate('', xy=(3.5, 1.8), xytext=(5, 2.5), 
                arrowprops=dict(arrowstyle='->', lw=2, color='#00695C'))
    ax.annotate('', xy=(5.6, 1.8), xytext=(7.35, 6.2), 
                arrowprops=dict(arrowstyle='->', lw=2, color='#9C27B0'))
    
    # ================= KEY STATISTICS BOX =================
    rect_stats = FancyBboxPatch((7.8, 3.5), 2, 1.8, boxstyle="round,pad=0.08", 
                                edgecolor='#D32F2F', facecolor='#FFEBEE', linewidth=2)
    ax.add_patch(rect_stats)
    ax.text(8.8, 5.1, 'KEY METRICS', fontsize=10, ha='center', fontweight='bold', color='#D32F2F')
    ax.text(8.8, 4.75, '✓ Accuracy: 76.43%', fontsize=8, ha='center')
    ax.text(8.8, 4.45, '✓ Latency: <500ms', fontsize=8, ha='center')
    ax.text(8.8, 4.15, '✓ Classes: 5', fontsize=8, ha='center')
    ax.text(8.8, 3.85, '✓ Channels: 64', fontsize=8, ha='center')
    
    # ================= TECH STACK BOX =================
    rect_tech = FancyBboxPatch((7.8, 0.8), 2, 2.5, boxstyle="round,pad=0.08", 
                               edgecolor='#1565C0', facecolor='#E3F2FD', linewidth=2)
    ax.add_patch(rect_tech)
    ax.text(8.8, 3.1, 'TECH STACK', fontsize=10, ha='center', fontweight='bold', color='#1565C0')
    ax.text(8.8, 2.8, 'Backend:', fontsize=7, ha='center', fontweight='bold')
    ax.text(8.8, 2.55, 'Python, TensorFlow', fontsize=7, ha='center')
    ax.text(8.8, 2.3, 'Keras, NumPy, Pandas', fontsize=7, ha='center')
    ax.text(8.8, 2.05, 'MNE-Python', fontsize=7, ha='center')
    ax.text(8.8, 1.75, 'Frontend:', fontsize=7, ha='center', fontweight='bold')
    ax.text(8.8, 1.5, 'Flask, Socket.IO', fontsize=7, ha='center')
    ax.text(8.8, 1.25, 'PyAutoGUI', fontsize=7, ha='center')
    ax.text(8.8, 1, 'Docker, Docker-Compose', fontsize=7, ha='center')
    
    # Save figure
    os.makedirs('outputs', exist_ok=True)
    plt.tight_layout()
    plt.savefig(r'outputs\project_architecture_diagram.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print("✓ Architecture diagram saved: outputs\\project_architecture_diagram.png")
    plt.close()

def create_data_flow_diagram():
    """Create a detailed data flow diagram."""
    
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(5, 9.7, 'BCI Interface - Complete Data Flow Pipeline', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Color scheme
    colors = {
        'input': '#BBDEFB',
        'process': '#FFF9C4',
        'ml': '#F3E5F5',
        'output': '#C8E6C9',
        'storage': '#FFCCBC'
    }
    
    # =========== STAGE 1: DATA ACQUISITION ===========
    ax.text(0.3, 9, 'STAGE 1: Data Acquisition', fontsize=10, fontweight='bold')
    
    rect = FancyBboxPatch((0.2, 8), 1.5, 0.7, boxstyle="round,pad=0.05", 
                          edgecolor='#1976D2', facecolor=colors['input'], linewidth=2)
    ax.add_patch(rect)
    ax.text(0.95, 8.35, 'EEG Sensors\n64 Channels\n160 Hz', 
            fontsize=7, ha='center', va='center')
    
    rect = FancyBboxPatch((2, 8), 1.5, 0.7, boxstyle="round,pad=0.05", 
                          edgecolor='#1976D2', facecolor=colors['input'], linewidth=2)
    ax.add_patch(rect)
    ax.text(2.75, 8.35, 'PhysioNet DB\n109 Subjects\n64 Channels', 
            fontsize=7, ha='center', va='center')
    
    # Arrow down
    ax.annotate('', xy=(1.5, 7.5), xytext=(1.5, 7.95), 
                arrowprops=dict(arrowstyle='->', lw=2, color='#1976D2'))
    
    # =========== STAGE 2: PREPROCESSING ===========
    ax.text(0.3, 7.3, 'STAGE 2: Signal Preprocessing', fontsize=10, fontweight='bold')
    
    rect = FancyBboxPatch((0.2, 6), 2.3, 1, boxstyle="round,pad=0.05", 
                          edgecolor='#F57F17', facecolor=colors['process'], linewidth=2)
    ax.add_patch(rect)
    ax.text(1.35, 6.75, 'Preprocessing Pipeline', fontsize=8, ha='center', fontweight='bold')
    ax.text(1.35, 6.45, '• Bandpass Filter (8-30 Hz)', fontsize=6, ha='center')
    ax.text(1.35, 6.2, '• Artifact Removal', fontsize=6, ha='center')
    ax.text(1.35, 5.95, '• Normalization', fontsize=6, ha='center')
    
    # Arrow down
    ax.annotate('', xy=(1.35, 5.8), xytext=(1.35, 5.95), 
                arrowprops=dict(arrowstyle='->', lw=2, color='#F57F17'))
    
    # =========== STAGE 3: DATA PREPARATION ===========
    ax.text(0.3, 5.6, 'STAGE 3: Data Preparation', fontsize=10, fontweight='bold')
    
    rect = FancyBboxPatch((0.2, 4.2), 2.3, 1.2, boxstyle="round,pad=0.05", 
                          edgecolor='#F57F17', facecolor=colors['process'], linewidth=2)
    ax.add_patch(rect)
    ax.text(1.35, 5.15, 'Data Windowing & Splitting', fontsize=8, ha='center', fontweight='bold')
    ax.text(1.35, 4.85, '• Epoch Extraction (0.5-3.5s)', fontsize=6, ha='center')
    ax.text(1.35, 4.6, '• Train/Val/Test Split (70/15/15)', fontsize=6, ha='center')
    ax.text(1.35, 4.35, '• Shape: (n_epochs, 64, 320)', fontsize=6, ha='center')
    
    # Arrow down
    ax.annotate('', xy=(1.35, 4), xytext=(1.35, 4.2), 
                arrowprops=dict(arrowstyle='->', lw=2, color='#F57F17'))
    
    # =========== STAGE 4: MODEL TRAINING ===========
    ax.text(0.3, 3.8, 'STAGE 4: Model Training', fontsize=10, fontweight='bold')
    
    rect = FancyBboxPatch((0.2, 1.8), 2.3, 1.8, boxstyle="round,pad=0.05", 
                          edgecolor='#7B1FA2', facecolor=colors['ml'], linewidth=2)
    ax.add_patch(rect)
    ax.text(1.35, 3.4, 'CNN-LSTM Training', fontsize=8, ha='center', fontweight='bold')
    ax.text(1.35, 3.1, '• Conv1D Blocks (32→64→128)', fontsize=6, ha='center')
    ax.text(1.35, 2.85, '• Bidirectional LSTM (128→64)', fontsize=6, ha='center')
    ax.text(1.35, 2.6, '• Dense Layers (64→32→5)', fontsize=6, ha='center')
    ax.text(1.35, 2.35, '• Epochs: 50', fontsize=6, ha='center')
    ax.text(1.35, 2.1, '• Callbacks: EarlyStopping, LR Decay', fontsize=6, ha='center')
    
    # Arrow down
    ax.annotate('', xy=(1.35, 1.6), xytext=(1.35, 1.8), 
                arrowprops=dict(arrowstyle='->', lw=2, color='#7B1FA2'))
    
    # =========== STAGE 5: EVALUATION ===========
    ax.text(0.3, 1.4, 'STAGE 5: Evaluation', fontsize=10, fontweight='bold')
    
    rect = FancyBboxPatch((0.2, 0.2), 2.3, 1, boxstyle="round,pad=0.05", 
                          edgecolor='#D32F2F', facecolor='#FFEBEE', linewidth=2)
    ax.add_patch(rect)
    ax.text(1.35, 0.95, 'Model Evaluation', fontsize=8, ha='center', fontweight='bold')
    ax.text(1.35, 0.65, '✓ Accuracy: 76.43%', fontsize=7, ha='center', color='#D32F2F')
    ax.text(1.35, 0.4, 'Confusion Matrix | Metrics', fontsize=6, ha='center')
    
    # =========== RIGHT SIDE: INFERENCE PIPELINE ===========
    ax.text(3.7, 9, 'INFERENCE PIPELINE', fontsize=10, fontweight='bold')
    
    # Real-time input
    rect = FancyBboxPatch((3.5, 8), 1.5, 0.7, boxstyle="round,pad=0.05", 
                          edgecolor='#00695C', facecolor=colors['input'], linewidth=2)
    ax.add_patch(rect)
    ax.text(4.25, 8.35, 'Real-Time\nEEG Stream\n64 channels', 
            fontsize=7, ha='center', va='center')
    
    ax.annotate('', xy=(4.25, 7.5), xytext=(4.25, 7.95), 
                arrowprops=dict(arrowstyle='->', lw=2, color='#00695C'))
    
    # Real-time preprocessing
    rect = FancyBboxPatch((3.5, 6.2), 1.5, 1, boxstyle="round,pad=0.05", 
                          edgecolor='#F57F17', facecolor=colors['process'], linewidth=2)
    ax.add_patch(rect)
    ax.text(4.25, 6.95, 'Real-Time', fontsize=7, ha='center', fontweight='bold')
    ax.text(4.25, 6.6, 'Preprocessing', fontsize=7, ha='center')
    ax.text(4.25, 6.35, '(Sliding Window)', fontsize=6, ha='center')
    
    ax.annotate('', xy=(4.25, 6), xytext=(4.25, 6.2), 
                arrowprops=dict(arrowstyle='->', lw=2, color='#F57F17'))
    
    # Model loading
    rect = FancyBboxPatch((3.5, 4.8), 1.5, 0.95, boxstyle="round,pad=0.05", 
                          edgecolor='#7B1FA2', facecolor=colors['ml'], linewidth=2)
    ax.add_patch(rect)
    ax.text(4.25, 5.5, 'Model Loading', fontsize=7, ha='center', fontweight='bold')
    ax.text(4.25, 5.15, 'Trained Model', fontsize=6, ha='center')
    ax.text(4.25, 4.9, '(TensorFlow)', fontsize=6, ha='center')
    
    ax.annotate('', xy=(4.25, 4.6), xytext=(4.25, 4.8), 
                arrowprops=dict(arrowstyle='->', lw=2, color='#7B1FA2'))
    
    # Inference
    rect = FancyBboxPatch((3.5, 3.2), 1.5, 1.2, boxstyle="round,pad=0.05", 
                          edgecolor='#00695C', facecolor=colors['output'], linewidth=2)
    ax.add_patch(rect)
    ax.text(4.25, 4.1, 'Inference', fontsize=7, ha='center', fontweight='bold')
    ax.text(4.25, 3.75, 'Prediction', fontsize=6, ha='center')
    ax.text(4.25, 3.5, '<500ms', fontsize=6, ha='center')
    ax.text(4.25, 3.25, 'latency', fontsize=6, ha='center')
    
    ax.annotate('', xy=(4.25, 3), xytext=(4.25, 3.2), 
                arrowprops=dict(arrowstyle='->', lw=2, color='#00695C'))
    
    # Output
    rect = FancyBboxPatch((3.5, 1.5), 1.5, 1.2, boxstyle="round,pad=0.05", 
                          edgecolor='#C2185B', facecolor='#FCE4EC', linewidth=2)
    ax.add_patch(rect)
    ax.text(4.25, 2.4, 'Output Action', fontsize=7, ha='center', fontweight='bold')
    ax.text(4.25, 2.05, 'Mouse Move', fontsize=6, ha='center')
    ax.text(4.25, 1.8, 'Click Action', fontsize=6, ha='center')
    
    # =========== CONFIGURATION & STORAGE ===========
    ax.text(6.3, 9, 'CONFIG & STORAGE', fontsize=10, fontweight='bold')
    
    rect = FancyBboxPatch((6.1, 7.5), 1.8, 1.2, boxstyle="round,pad=0.05", 
                          edgecolor='#00796B', facecolor='#E0F2F1', linewidth=2)
    ax.add_patch(rect)
    ax.text(7, 8.4, 'Configuration', fontsize=7, ha='center', fontweight='bold')
    ax.text(7, 8.05, 'config.yaml', fontsize=6, ha='center')
    ax.text(7, 7.75, '• Model params', fontsize=5, ha='center')
    ax.text(7, 7.55, '• Training config', fontsize=5, ha='center')
    
    rect = FancyBboxPatch((6.1, 5.8), 1.8, 1.3, boxstyle="round,pad=0.05", 
                          edgecolor='#F57F17', facecolor=colors['storage'], linewidth=2)
    ax.add_patch(rect)
    ax.text(7, 6.8, 'Model Storage', fontsize=7, ha='center', fontweight='bold')
    ax.text(7, 6.45, 'models/', fontsize=6, ha='center')
    ax.text(7, 6.15, '• .h5 format', fontsize=5, ha='center')
    ax.text(7, 5.95, '• Versioning', fontsize=5, ha='center')
    
    rect = FancyBboxPatch((6.1, 4), 1.8, 1.5, boxstyle="round,pad=0.05", 
                          edgecolor='#D32F2F', facecolor='#FFEBEE', linewidth=2)
    ax.add_patch(rect)
    ax.text(7, 5.2, 'Outputs', fontsize=7, ha='center', fontweight='bold')
    ax.text(7, 4.85, 'outputs/', fontsize=6, ha='center')
    ax.text(7, 4.55, '• Training history', fontsize=5, ha='center')
    ax.text(7, 4.3, '• Metrics & curves', fontsize=5, ha='center')
    ax.text(7, 4.05, '• Visualizations', fontsize=5, ha='center')
    
    # =========== TECHNOLOGIES ===========
    ax.text(8.2, 9, 'TECHNOLOGIES', fontsize=10, fontweight='bold')
    
    tech_text = """
    🐍 Python 3.8+
    
    Deep Learning:
    • TensorFlow 2.x
    • Keras API
    
    Data Science:
    • NumPy, Pandas
    • Scikit-learn
    • MNE-Python
    
    Signal Processing:
    • SciPy
    • Matplotlib
    
    Deployment:
    • Flask, Socket.IO
    • Docker
    • PyAutoGUI
    """
    
    ax.text(8.8, 5.5, tech_text, fontsize=6, ha='center', va='center', 
            family='monospace', bbox=dict(boxstyle='round', facecolor='#E3F2FD', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(r'outputs\data_flow_diagram.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("✓ Data flow diagram saved: outputs\\data_flow_diagram.png")
    plt.close()

def create_module_dependency_diagram():
    """Create a module dependency diagram."""
    
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(5, 9.6, 'BCI Interface - Module Dependencies & Integration', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Core modules
    modules = {
        'config.py': (2, 8, '#E3F2FD'),
        'preprocessing.py': (1, 6.5, '#FFF9C4'),
        'data_loader.py': (3, 6.5, '#F3E5F5'),
        'data_preparation.py': (5, 6.5, '#C8E6C9'),
        'physionet_loader.py': (7, 6.5, '#FFCCBC'),
        
        'model.py': (3, 4.5, '#F3E5F5'),
        'train.py': (5, 4.5, '#F3E5F5'),
        'evaluate.py': (7, 4.5, '#F3E5F5'),
        'model_manager.py': (1, 4.5, '#E0F2F1'),
        
        'realtime_inference.py': (2, 2.5, '#C8E6C9'),
        'click_detection.py': (4, 2.5, '#FFCCBC'),
        'utils.py': (6, 2.5, '#E3F2FD'),
    }
    
    # Draw modules
    for name, (x, y, color) in modules.items():
        rect = FancyBboxPatch((x-0.6, y-0.35), 1.2, 0.6, boxstyle="round,pad=0.05", 
                              edgecolor='#333', facecolor=color, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x, y, name, fontsize=7, ha='center', va='center', fontweight='bold')
    
    # Dependencies (arrows)
    dependencies = [
        # Config is used everywhere
        ((2, 7.65), (1, 4.85)),  # config -> model_manager
        ((2, 7.65), (3, 5.15)),  # config -> model
        ((2, 7.65), (5, 5.15)),  # config -> train
        ((2, 7.65), (7, 5.15)),  # config -> evaluate
        ((2, 7.65), (3, 7.15)),  # config -> data_loader
        
        # Data pipeline
        ((3, 6.15), (5, 5.15)),  # data_loader -> train
        ((1, 6.15), (3, 5.15)),  # preprocessing -> model
        ((5, 6.15), (5, 5.15)),  # data_preparation -> train
        ((7, 6.15), (5, 5.15)),  # physionet -> train
        
        # Model training
        ((3, 4.15), (5, 4.5)),   # model -> train
        ((1, 4.85), (5, 5.15)),  # model_manager -> train
        ((5, 4.15), (7, 4.5)),   # train -> evaluate
        
        # Inference pipeline
        ((5, 4.15), (2, 3.15)),  # train -> realtime_inference
        ((6, 2.15), (4, 2.5)),   # utils -> click_detection
        ((2, 2.15), (4, 2.5)),   # realtime_inference -> click_detection
    ]
    
    for start, end in dependencies:
        ax.annotate('', xy=end, xytext=start, 
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='#666', alpha=0.6))
    
    # Legend for layers
    ax.text(0.5, 9.2, '📦 Configuration Layer', fontsize=8, fontweight='bold')
    ax.text(0.5, 8.8, '📊 Data Processing Layer', fontsize=8, fontweight='bold')
    ax.text(0.5, 8.4, '🧠 Model Layer', fontsize=8, fontweight='bold')
    ax.text(0.5, 8, '⚡ Inference Layer', fontsize=8, fontweight='bold')
    
    # Add layer indicators
    rect = FancyBboxPatch((0.2, 7.8), 2.5, 0.3, boxstyle="round,pad=0.02", 
                          edgecolor='#E3F2FD', facecolor='#E3F2FD', linewidth=1, alpha=0.5)
    ax.add_patch(rect)
    
    plt.tight_layout()
    plt.savefig(r'outputs\module_dependency_diagram.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("✓ Module dependency diagram saved: outputs\\module_dependency_diagram.png")
    plt.close()

if __name__ == '__main__':
    print("Generating Project Architecture Diagrams...\n")
    create_architecture_diagram()
    create_data_flow_diagram()
    create_module_dependency_diagram()
    
    print("\n" + "="*70)
    print("ARCHITECTURE DIAGRAMS GENERATED SUCCESSFULLY")
    print("="*70)
    print("\nGenerated Files:")
    print("  ✓ outputs\\project_architecture_diagram.png")
    print("  ✓ outputs\\data_flow_diagram.png")
    print("  ✓ outputs\\module_dependency_diagram.png")
    print("\n" + "="*70)
