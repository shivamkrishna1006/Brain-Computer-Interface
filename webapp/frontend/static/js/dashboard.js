// BCI Dashboard - Main JavaScript Application

// Initialize Socket.io connection
const socket = io();

// Global variables
let charts = {};
let isStreaming = false;
let streamStartTime = 0;
let streamDuration = 0;
let streamUpdateInterval = null;
let eegBuffer = [];
let predictionHistory = [];
let trainingMetrics = {
    epochs: [],
    losses: [],
    valLosses: [],
    accuracies: []
};

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing BCI Dashboard...');
    
    // Initialize charts
    initializeCharts();
    
    // Load initial data
    loadModels();
    getSystemStatus();
    
    // Setup real-time clock
    updateClock();
    setInterval(updateClock, 1000);
    
    // Socket.io event listeners
    setupSocketListeners();
    
    console.log('Dashboard initialized successfully');
});

// ============================================================================
// SOCKET.IO HANDLERS
// ============================================================================

function setupSocketListeners() {
    // Connection events
    socket.on('connect', function() {
        console.log('Connected to server');
        updateStatusIndicator(true);
        showToast('Connected to BCI Backend', 'success');
    });

    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        updateStatusIndicator(false);
        showToast('Disconnected from BCI Backend', 'danger');
    });

    socket.on('error', function(data) {
        console.error('Socket error:', data);
        showToast('Error: ' + (data.message || 'Unknown error'), 'danger');
    });

    // Stream events
    socket.on('eeg_sample', function(data) {
        handleEEGSample(data);
    });

    socket.on('prediction', function(data) {
        handlePrediction(data);
    });

    socket.on('stream_status', function(data) {
        console.log('Stream status:', data.status);
    });

    // Training events
    socket.on('training_progress', function(data) {
        handleTrainingProgress(data);
    });

    socket.on('training_complete', function(data) {
        handleTrainingComplete(data);
    });

    // Evaluation events
    socket.on('evaluation_result', function(data) {
        handleEvaluationResult(data);
    });

    socket.on('response', function(data) {
        console.log('Server response:', data);
    });
}

// ============================================================================
// CHART INITIALIZATION
// ============================================================================

function initializeCharts() {
    // Prediction Distribution Chart
    const predictionCtx = document.getElementById('predictionChart').getContext('2d');
    charts.prediction = new Chart(predictionCtx, {
        type: 'doughnut',
        data: {
            labels: ['Left Hand', 'Right Hand', 'Both Hands', 'Both Feet', 'Tongue/Click'],
            datasets: [{
                data: [0, 0, 0, 0, 0],
                backgroundColor: [
                    '#0d6efd',
                    '#dc3545',
                    '#198754',
                    '#ffc107',
                    '#0dcaf0'
                ],
                borderColor: '#ffffff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });

    // Confidence Trend Chart
    const confidenceCtx = document.getElementById('confidenceChart').getContext('2d');
    charts.confidence = new Chart(confidenceCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Confidence',
                data: [],
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1
                }
            },
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });

    // EEG Signal Chart
    const eegCtx = document.getElementById('eegSignalChart').getContext('2d');
    charts.eeg = new Chart(eegCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'CH1',
                    data: [],
                    borderColor: '#0d6efd',
                    tension: 0.2,
                    fill: false,
                    pointRadius: 0
                },
                {
                    label: 'CH2',
                    data: [],
                    borderColor: '#dc3545',
                    tension: 0.2,
                    fill: false,
                    pointRadius: 0
                },
                {
                    label: 'CH3',
                    data: [],
                    borderColor: '#198754',
                    tension: 0.2,
                    fill: false,
                    pointRadius: 0
                },
                {
                    label: 'CH4',
                    data: [],
                    borderColor: '#ffc107',
                    tension: 0.2,
                    fill: false,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'Amplitude (µV)'
                    }
                }
            }
        }
    });

    // Training Chart
    const trainingCtx = document.getElementById('trainingChart').getContext('2d');
    charts.training = new Chart(trainingCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Loss',
                    data: [],
                    borderColor: '#dc3545',
                    yAxisID: 'y'
                },
                {
                    label: 'Val Loss',
                    data: [],
                    borderColor: '#ffc107',
                    yAxisID: 'y'
                },
                {
                    label: 'Accuracy',
                    data: [],
                    borderColor: '#198754',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: {
                mode: 'index',
                intersect: false
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    title: {
                        display: true,
                        text: 'Loss'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Accuracy (%)'
                    }
                }
            }
        }
    });

    // Class Accuracy Chart
    const classCtx = document.getElementById('classAccuracyChart').getContext('2d');
    charts.classAccuracy = new Chart(classCtx, {
        type: 'bar',
        data: {
            labels: ['Left Hand', 'Right Hand', 'Both Hands', 'Both Feet', 'Tongue/Click'],
            datasets: [{
                label: 'Accuracy (%)',
                data: [0, 0, 0, 0, 0],
                backgroundColor: '#0d6efd'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

// ============================================================================
// REAL-TIME STREAMING
// ============================================================================

function startStream() {
    console.log('Starting EEG stream');
    isStreaming = true;
    streamStartTime = Date.now();
    
    document.getElementById('startStreamBtn').disabled = true;
    document.getElementById('stopStreamBtn').disabled = false;
    
    // Update stream duration
    streamUpdateInterval = setInterval(function() {
        streamDuration = Math.floor((Date.now() - streamStartTime) / 1000);
        document.getElementById('streamDuration').textContent = streamDuration + 's';
    }, 1000);
    
    socket.emit('start_stream');
    
    // Simulate continuous data reception
    let sampleCount = 0;
    const streamInterval = setInterval(function() {
        if (!isStreaming) {
            clearInterval(streamInterval);
            return;
        }
        
        socket.emit('request_eeg_sample');
        sampleCount++;
        
        if (sampleCount % 10 === 0) {
            socket.emit('request_eeg_sample');
        }
    }, 100);
    
    showToast('EEG Stream Started', 'success');
}

function stopStream() {
    console.log('Stopping EEG stream');
    isStreaming = false;
    
    document.getElementById('startStreamBtn').disabled = false;
    document.getElementById('stopStreamBtn').disabled = true;
    
    if (streamUpdateInterval) {
        clearInterval(streamUpdateInterval);
    }
    
    socket.emit('stop_stream');
    showToast('EEG Stream Stopped', 'info');
}

function handleEEGSample(data) {
    // Update EEG chart with new data
    const sample = data.sample;
    
    if (charts.eeg.data.labels.length > 250) {
        charts.eeg.data.labels.shift();
        for (let i = 0; i < 4; i++) {
            charts.eeg.data.datasets[i].data.shift();
        }
    }
    
    charts.eeg.data.labels.push(charts.eeg.data.labels.length);
    
    for (let i = 0; i < Math.min(4, sample.length); i++) {
        charts.eeg.data.datasets[i].data.push(sample[i]);
    }
    
    charts.eeg.update();
    
    // Update statistics
    updateSignalStats(sample);
    
    // Store in buffer
    eegBuffer.push(sample);
    if (eegBuffer.length > 250) {
        eegBuffer.shift();
    }
}

function handlePrediction(data) {
    const predictionClass = data.class;
    const confidence = data.confidence;
    const probabilities = data.probabilities;
    
    // Update last prediction display
    document.getElementById('lastPrediction').textContent = predictionClass;
    document.getElementById('predictionConfidence').textContent = 
        'Confidence: ' + (confidence * 100).toFixed(2) + '%';
    
    // Update prediction distribution chart
    const classIndex = ['Left Hand', 'Right Hand', 'Both Hands', 'Both Feet', 'Tongue/Click']
        .indexOf(predictionClass);
    const newData = charts.prediction.data.datasets[0].data.map((val, idx) => 
        idx === classIndex ? (val || 0) + 1 : val
    );
    charts.prediction.data.datasets[0].data = newData;
    charts.prediction.update();
    
    // Update confidence trend
    if (charts.confidence.data.labels.length > 30) {
        charts.confidence.data.labels.shift();
        charts.confidence.data.datasets[0].data.shift();
    }
    charts.confidence.data.labels.push('');
    charts.confidence.data.datasets[0].data.push(confidence);
    charts.confidence.update();
    
    // Add to predictions list
    addPredictionItem(predictionClass, confidence, probabilities);
    
    // Store in history
    predictionHistory.push({
        class: predictionClass,
        confidence: confidence,
        timestamp: new Date().toISOString()
    });
}

function addPredictionItem(predictionClass, confidence, probabilities) {
    const predictionsList = document.getElementById('predictionsList');
    
    const confidenceClass = confidence > 0.7 ? 'high-confidence' : 
                           confidence > 0.5 ? 'medium-confidence' : 'low-confidence';
    const confidenceLabel = confidence > 0.7 ? 'High' : 
                           confidence > 0.5 ? 'Medium' : 'Low';
    const badgeClass = confidence > 0.7 ? 'confidence-high' : 
                      confidence > 0.5 ? 'confidence-medium' : 'confidence-low';
    
    const item = document.createElement('div');
    item.className = `prediction-item ${confidenceClass}`;
    item.innerHTML = `
        <div class="prediction-class">
            ${predictionClass}
            <span class="confidence-badge ${badgeClass}">${confidenceLabel}</span>
        </div>
        <div class="prediction-confidence">
            ${(confidence * 100).toFixed(1)}% Confidence
        </div>
    `;
    
    predictionsList.insertBefore(item, predictionsList.firstChild);
    
    // Keep only last 10 items
    while (predictionsList.children.length > 10) {
        predictionsList.removeChild(predictionsList.lastChild);
    }
}

function updateSignalStats(sample) {
    const mean = sample.reduce((a, b) => a + b) / sample.length;
    const variance = sample.reduce((a, b) => a + Math.pow(b - mean, 2)) / sample.length;
    const std = Math.sqrt(variance);
    const min = Math.min(...sample);
    const max = Math.max(...sample);
    
    document.getElementById('signalMin').textContent = min.toFixed(2);
    document.getElementById('signalMax').textContent = max.toFixed(2);
    document.getElementById('signalMean').textContent = mean.toFixed(2);
    document.getElementById('signalStd').textContent = std.toFixed(2);
}

// ============================================================================
// TRAINING
// ============================================================================

function startTraining() {
    const config = {
        epochs: parseInt(document.getElementById('epochsInput').value),
        batch_size: parseInt(document.getElementById('batchSizeInput').value),
        learning_rate: parseFloat(document.getElementById('learningRateInput').value),
        samples: parseInt(document.getElementById('samplesInput').value)
    };
    
    console.log('Starting training with config:', config);
    
    document.getElementById('trainingStatus').classList.remove('hide');
    document.getElementById('trainingStatusText').textContent = 'Training in progress...';
    
    trainingMetrics = {
        epochs: [],
        losses: [],
        valLosses: [],
        accuracies: []
    };
    
    socket.emit('train_model', { config: config });
    
    showToast('Training started', 'success');
}

function handleTrainingProgress(data) {
    const epoch = data.epoch;
    const progress = data.progress;
    const loss = data.loss;
    const valLoss = data.val_loss;
    const accuracy = data.accuracy;
    
    // Update progress bar
    document.getElementById('trainingProgress').textContent = progress.toFixed(2) + '%';
    document.getElementById('trainingProgressBar').style.width = progress + '%';
    
    // Update status
    document.getElementById('trainingStatusText').textContent = 
        `Epoch ${epoch}: Loss=${loss.toFixed(4)}, Val Loss=${valLoss.toFixed(4)}, Accuracy=${accuracy.toFixed(2)}%`;
    
    // Store metrics
    trainingMetrics.epochs.push(epoch);
    trainingMetrics.losses.push(loss);
    trainingMetrics.valLosses.push(valLoss);
    trainingMetrics.accuracies.push(accuracy);
    
    // Update training chart
    charts.training.data.labels = trainingMetrics.epochs;
    charts.training.data.datasets[0].data = trainingMetrics.losses;
    charts.training.data.datasets[1].data = trainingMetrics.valLosses;
    charts.training.data.datasets[2].data = trainingMetrics.accuracies;
    charts.training.update();
}

function handleTrainingComplete(data) {
    document.getElementById('trainingProgressBar').style.width = '100%';
    document.getElementById('trainingProgress').textContent = '100%';
    document.getElementById('trainingStatusText').textContent = 
        `Training complete! Model saved as: ${data.model_name}`;
    
    showToast('Training completed successfully! Model: ' + data.model_name, 'success');
    
    // Reload models list
    setTimeout(function() {
        loadModels();
    }, 1000);
}

// ============================================================================
// EVALUATION
// ============================================================================

function startEvaluation() {
    const modelName = document.getElementById('modelSelect').value;
    
    if (!modelName) {
        showToast('Please select a model first', 'warning');
        return;
    }
    
    console.log('Starting evaluation for model:', modelName);
    
    socket.emit('evaluate_model', { model: modelName });
    
    showToast('Evaluating model...', 'info');
}

function handleEvaluationResult(data) {
    const accuracy = data.accuracy;
    const perClassAccuracy = data.per_class_accuracy;
    const f1Score = data.f1_score;
    
    // Update evaluation results
    document.getElementById('overallAccuracy').textContent = accuracy.toFixed(2) + '%';
    document.getElementById('f1Score').textContent = f1Score.toFixed(3);
    
    // Update class accuracy chart
    charts.classAccuracy.data.datasets[0].data = [
        perClassAccuracy['Left Hand'],
        perClassAccuracy['Right Hand'],
        perClassAccuracy['Both Hands'],
        perClassAccuracy['Both Feet'],
        perClassAccuracy['Tongue/Click']
    ];
    charts.classAccuracy.update();
    
    showToast('Model evaluation complete! Accuracy: ' + accuracy.toFixed(2) + '%', 'success');
}

// ============================================================================
// MODELS MANAGEMENT
// ============================================================================

function loadModels() {
    console.log('Loading available models...');
    
    fetch('/api/models')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load models');
            }
            return response.json();
        })
        .then(data => {
            console.log('Models loaded:', data);
            
            // Update models list
            const modelsList = document.getElementById('modelsList');
            const modelSelect = document.getElementById('modelSelect');
            
            modelsList.innerHTML = '';
            modelSelect.innerHTML = '<option value="">Choose a model...</option>';
            
            if (data.models.length === 0) {
                modelsList.innerHTML = '<p class="text-muted col-12">No models available. Train a model first.</p>';
            } else {
                data.models.forEach(model => {
                    // Add to list
                    const modelCard = document.createElement('div');
                    modelCard.className = 'col-md-4 model-card';
                    modelCard.innerHTML = `
                        <div class="model-card-title">${model.name}</div>
                        <div class="model-card-info">Size: ${model.size}</div>
                        <div class="model-card-info">Created: ${new Date(model.created).toLocaleString()}</div>
                    `;
                    modelsList.appendChild(modelCard);
                    
                    // Add to select
                    const option = document.createElement('option');
                    option.value = model.name;
                    option.textContent = model.name;
                    modelSelect.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error('Error loading models:', error);
            showToast('Failed to load models', 'danger');
        });
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function updateClock() {
    const now = new Date();
    const time = now.toLocaleTimeString();
    document.getElementById('currentTime').textContent = time;
}

function updateStatusIndicator(connected) {
    const indicator = document.getElementById('statusIndicator');
    if (connected) {
        indicator.classList.add('connected');
        indicator.innerHTML = '<i class="fas fa-circle"></i> Connected';
    } else {
        indicator.classList.remove('connected');
        indicator.innerHTML = '<i class="fas fa-circle"></i> Disconnected';
    }
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'danger' ? 'danger' : type === 'warning' ? 'warning' : 'info'}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove after hiding
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

function getSystemStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            console.log('System status:', data);
        })
        .catch(error => console.error('Error getting system status:', error));
}
