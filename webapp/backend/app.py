"""
Main Flask application for BCI Interface Web App
Real-time EEG visualization and model prediction dashboard
"""

import logging
import os
from pathlib import Path
from flask import Flask, render_template, jsonify, send_from_directory, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import numpy as np
from datetime import datetime

# Import configuration
from config import config

# Initialize Flask
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

# Initialize extensions
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Setup logging
logging.basicConfig(
    level=app.config['LOG_LEVEL'],
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# MODELS AND DATA SIMULATION
# ============================================================================

class EEGSimulator:
    """Simulate real-time EEG data"""
    
    def __init__(self, channels=8, sampling_rate=250):
        self.channels = channels
        self.sampling_rate = sampling_rate
        self.buffer = np.zeros((channels, 250))  # 1 second buffer
        
    def generate_sample(self):
        """Generate synthetic EEG sample"""
        # Generate realistic EEG-like signals
        sample = np.random.normal(0, 1, self.channels)
        
        # Add some frequency content (alpha/beta bands)
        for i in range(self.channels):
            t = np.arange(250) / self.sampling_rate
            alpha = 10 * np.sin(2 * np.pi * 10 * t + np.random.rand() * 2 * np.pi)  # 10 Hz
            beta = 5 * np.sin(2 * np.pi * 20 * t + np.random.rand() * 2 * np.pi)    # 20 Hz
            sample[i] = sample[i] + alpha[np.random.randint(0, 250)] + beta[np.random.randint(0, 250)]
        
        return sample


class ModelPredictor:
    """Simulate model predictions"""
    
    def __init__(self):
        self.classes = ['Left Hand', 'Right Hand', 'Both Hands', 'Both Feet', 'Tongue/Click']
        self.last_prediction = 0
        
    def predict(self, eeg_data):
        """Make prediction from EEG data"""
        # Simulate model prediction
        predictions = np.random.rand(len(self.classes))
        predictions = predictions / predictions.sum()  # Normalize
        
        predicted_class = np.argmax(predictions)
        confidence = float(predictions[predicted_class])
        
        return {
            'class': self.classes[predicted_class],
            'class_idx': int(predicted_class),
            'confidence': confidence,
            'probabilities': {self.classes[i]: float(predictions[i]) for i in range(len(self.classes))}
        }


# Global instances
eeg_simulator = EEGSimulator()
model_predictor = ModelPredictor()


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main dashboard page"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error loading index: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/models')
def get_models():
    """Get available models with detailed information"""
    try:
        models_dir = Path(app.config['MODELS_DIR'])
        models = []
        
        # Predefined model options with metadata
        predefined_models = [
            {
                'name': 'best_eeg_model',
                'display_name': 'Best Trained Model (71.47%)',
                'version': '1.0',
                'accuracy': '71.47%',
                'description': 'Original CNN-LSTM model with baseline accuracy',
                'status': 'available',
                'type': 'production'
            },
            {
                'name': 'best_eeg_model_v2',
                'display_name': 'Enhanced Model v2.0 (76.43%)',
                'version': '2.0',
                'accuracy': '76.43%',
                'description': 'Enhanced CNN-LSTM with 50% more capacity and optimized parameters (Recommended)',
                'status': 'available',
                'type': 'production'
            },
            {
                'name': 'checkpoint_best',
                'display_name': 'Latest Checkpoint',
                'version': '2.0',
                'accuracy': '~76%',
                'description': 'Most recent model checkpoint',
                'status': 'available',
                'type': 'checkpoint'
            },
            {
                'name': 'new_model',
                'display_name': 'New Model (Untrained)',
                'version': '2.0',
                'accuracy': 'N/A',
                'description': 'Fresh model for training',
                'status': 'ready',
                'type': 'new'
            }
        ]
        
        # Add any models found in the models directory
        if models_dir.exists():
            for model_file in models_dir.glob('*.h5'):
                # Check if already in predefined list
                stem = model_file.stem
                if not any(m['name'] == stem for m in predefined_models):
                    model_info = {
                        'name': stem,
                        'display_name': f"Custom Model: {stem}",
                        'path': str(model_file),
                        'size': f"{model_file.stat().st_size / (1024*1024):.2f}MB",
                        'created': datetime.fromtimestamp(model_file.stat().st_ctime).isoformat(),
                        'accuracy': 'Unknown',
                        'version': '1.0',
                        'description': 'Custom model file',
                        'status': 'available',
                        'type': 'custom'
                    }
                    models.append(model_info)
        
        # Add predefined models to the list
        for pred_model in predefined_models:
            model_file = models_dir / f"{pred_model['name']}.h5" if models_dir.exists() else None
            if model_file and model_file.exists():
                pred_model['path'] = str(model_file)
                pred_model['size'] = f"{model_file.stat().st_size / (1024*1024):.2f}MB"
                pred_model['created'] = datetime.fromtimestamp(model_file.stat().st_ctime).isoformat()
            models.append(pred_model)
        
        return jsonify({
            'models': models,
            'count': len(models),
            'categories': {
                'production': [m for m in models if m.get('type') == 'production'],
                'checkpoint': [m for m in models if m.get('type') == 'checkpoint'],
                'new': [m for m in models if m.get('type') == 'new'],
                'custom': [m for m in models if m.get('type') == 'custom']
            }
        })
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/status')
def get_status():
    """Get system status"""
    try:
        return jsonify({
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'webapp_version': '1.0.0'
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/config')
def get_config():
    """Get webapp configuration"""
    try:
        return jsonify({
            'sampling_rate': eeg_simulator.sampling_rate,
            'channels': eeg_simulator.channels,
            'classes': model_predictor.classes,
            'buffer_size': 250
        })
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# WEBSOCKET EVENTS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('response', {'data': 'Connected to BCI Live Dashboard'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('start_stream')
def handle_start_stream():
    """Start streaming EEG data"""
    logger.info("Starting EEG stream")
    
    try:
        # Send initial configuration
        emit('eeg_config', {
            'channels': eeg_simulator.channels,
            'sampling_rate': eeg_simulator.sampling_rate,
            'classes': model_predictor.classes
        })
        emit('stream_status', {'status': 'started'})
    except Exception as e:
        logger.error(f"Error starting stream: {e}")
        emit('error', {'message': str(e)})


@socketio.on('stop_stream')
def handle_stop_stream():
    """Stop streaming EEG data"""
    logger.info("Stopping EEG stream")
    emit('stream_status', {'status': 'stopped'})


@socketio.on('request_eeg_sample')
def handle_eeg_request():
    """Send EEG sample on demand"""
    try:
        # Generate sample
        sample = eeg_simulator.generate_sample()
        
        # Make prediction
        prediction = model_predictor.predict(sample)
        
        # Send data
        emit('eeg_sample', {
            'timestamp': datetime.now().isoformat(),
            'sample': sample.tolist(),
            'channels': ['CH1', 'CH2', 'CH3', 'CH4', 'CH5', 'CH6', 'CH7', 'CH8']
        })
        
        emit('prediction', {
            'timestamp': datetime.now().isoformat(),
            'class': prediction['class'],
            'class_idx': prediction['class_idx'],
            'confidence': prediction['confidence'],
            'probabilities': prediction['probabilities']
        })
        
    except Exception as e:
        logger.error(f"Error in EEG request: {e}")
        emit('error', {'message': str(e)})


@socketio.on('train_model')
def handle_train_model(data):
    """Simulate model training"""
    logger.info(f"Training model: {data}")
    
    try:
        config_data = data.get('config', {})
        
        # Simulate training progress
        for epoch in range(1, int(config_data.get('epochs', 50)) + 1):
            progress = (epoch / int(config_data.get('epochs', 50))) * 100
            emit('training_progress', {
                'epoch': epoch,
                'progress': progress,
                'loss': float(np.random.rand() * 0.5),
                'val_loss': float(np.random.rand() * 0.5),
                'accuracy': float(50 + np.random.rand() * 30)
            })
            
            # Simulate computation time
            import time
            time.sleep(0.1)
        
        emit('training_complete', {
            'status': 'completed',
            'final_accuracy': float(70 + np.random.rand() * 5),
            'model_name': f"bci_model_{int(datetime.now().timestamp())}"
        })
        
    except Exception as e:
        logger.error(f"Error in training: {e}")
        emit('error', {'message': str(e)})


@socketio.on('evaluate_model')
def handle_evaluate_model(data):
    """Simulate model evaluation"""
    logger.info(f"Evaluating model: {data}")
    
    try:
        model_name = data.get('model', 'default_model')
        
        # Simulate evaluation
        emit('evaluation_start', {
            'model': model_name,
            'status': 'evaluating'
        })
        
        import time
        time.sleep(1)
        
        emit('evaluation_result', {
            'model': model_name,
            'accuracy': float(71.47),
            'per_class_accuracy': {
                'Left Hand': 72.3,
                'Right Hand': 73.1,
                'Both Hands': 70.5,
                'Both Feet': 68.9,
                'Tongue/Click': 72.1
            },
            'f1_score': 0.70
        })
        
    except Exception as e:
        logger.error(f"Error in evaluation: {e}")
        emit('error', {'message': str(e)})


# ============================================================================
# APPLICATION FACTORY
# ============================================================================

def create_app(config_name='development'):
    """Application factory"""
    app.config.from_object(config[config_name])
    return app


if __name__ == '__main__':
    logger.info("Starting BCI Web App...")
    socketio.run(app, 
                 host='0.0.0.0',
                 port=5000,
                 debug=app.config['DEBUG'])
