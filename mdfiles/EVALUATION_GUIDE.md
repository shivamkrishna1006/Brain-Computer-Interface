# Model Evaluation Guide

## Overview

This guide provides comprehensive model evaluation functionality for the CNN-LSTM EEG classification system. The evaluation module calculates accuracy, precision, recall, F1-score, generates classification reports, plots confusion matrices, and saves all results.

**Supports:**
- Multi-class classification (5-class motor imagery: Left, Right, Hands, Feet, Click)
- Accuracy, precision, recall, F1-score (macro and weighted)
- Per-class metrics calculation
- Confusion matrix heatmap visualization
- Per-class metrics comparison bar chart
- Prediction distribution histogram
- Comprehensive text reports
- JSON results storage

---

## Quick Start

### Basic Usage

```python
from src.evaluate import ModelEvaluator
from tensorflow import keras

# Load model
model = keras.models.load_model('models/cnn_lstm_model.h5')

# Initialize evaluator
evaluator = ModelEvaluator(model, n_classes=5)
evaluator.set_class_names(['Left', 'Right', 'Hands', 'Feet', 'Click'])

# Evaluate
metrics = evaluator.evaluate(test_data, test_labels)

# Plot results
evaluator.plot_confusion_matrix()
evaluator.plot_metrics_comparison()
evaluator.plot_prediction_distribution()

# Save results
evaluator.save_evaluation_report()
evaluator.save_results_json()
```

### Run Complete Example

```bash
python evaluate_eeg_model.py
```

---

## Core Components

### ModelEvaluator Class

The main evaluation class that handles all evaluation operations.

#### Initialization

```python
evaluator = ModelEvaluator(
    model: keras.Model,
    config: Dict = None,
    n_classes: int = 5
)
```

**Parameters:**
- `model` - Trained Keras model
- `config` - Configuration dictionary (optional)
- `n_classes` - Number of classification classes (default: 5)

**Methods:**

#### 1. `evaluate(test_data, test_labels) -> Dict`

Comprehensive evaluation on test set.

**Parameters:**
- `test_data` - Test features (shape: n_samples, channels, timesteps) OR model predictions (shape: n_samples, n_classes)
- `test_labels` - Test labels (shape: n_samples,) integer indices OR (n_samples, n_classes) one-hot encoded

**Returns:** Dictionary with all metrics

**Metrics Calculated:**
- `accuracy` - Overall accuracy
- `precision_macro` - Macro-averaged precision
- `precision_weighted` - Weighted precision (by class support)
- `recall_macro` - Macro-averaged recall
- `recall_weighted` - Weighted recall
- `f1_macro` - Macro-averaged F1-score
- `f1_weighted` - Weighted F1-score
- `precision_per_class` - Per-class precision (list)
- `recall_per_class` - Per-class recall (list)
- `f1_per_class` - Per-class F1-score (list)
- `confusion_matrix` - Confusion matrix
- `classification_report` - Detailed classification report

```python
metrics = evaluator.evaluate(X_test, y_test)

print(f"Accuracy: {metrics['accuracy']:.4f}")
print(f"F1-Score (Macro): {metrics['f1_macro']:.4f}")
print(f"F1-Score (Weighted): {metrics['f1_weighted']:.4f}")
```

#### 2. `set_class_names(class_names: list) -> None`

Set class names for better visualization and reports.

```python
evaluator.set_class_names(['Left', 'Right', 'Hands', 'Feet', 'Click'])
```

#### 3. `plot_confusion_matrix(save_path=None, figsize=(10, 8)) -> None`

Plot confusion matrix as a heatmap with class names.

**Features:**
- Annotated cells with prediction counts
- Color gradient indicating frequency
- Full class names on axes
- High-resolution output (300 DPI)

**Output:** `outputs/confusion_matrix_{timestamp}.png`

```python
evaluator.plot_confusion_matrix()
# Or specify path:
evaluator.plot_confusion_matrix('results/my_confusion_matrix.png')
```

#### 4. `plot_metrics_comparison(save_path=None, figsize=(12, 6)) -> None`

Create grouped bar chart comparing precision, recall, and F1-score per class.

**Features:**
- Side-by-side bars for each metric
- Per-class breakdown
- Clear legend and labels
- Grid reference lines

**Output:** `outputs/metrics_comparison_{timestamp}.png`

```python
evaluator.plot_metrics_comparison()
```

#### 5. `plot_prediction_distribution(save_path=None, figsize=(12, 5)) -> None`

Visualize prediction probability distributions.

**Components:**
- Histogram: Comparing correct vs incorrect predictions
- Box plot: Probability distribution per class

**Output:** `outputs/prediction_distribution_{timestamp}.png`

```python
evaluator.plot_prediction_distribution()
```

#### 6. `save_evaluation_report(save_path=None) -> None`

Save comprehensive text report with all metrics.

**Report Sections:**
- Overall metrics
- Per-class metrics
- Confusion matrix with analysis
- Detailed classification report

**Output:** `outputs/evaluation_report_{timestamp}.txt`

```python
evaluator.save_evaluation_report()
```

**Sample Report Structure:**
```
================================================================================
MODEL EVALUATION REPORT
================================================================================

OVERALL METRICS
--------------------------------------------------------------------------------
Accuracy: 0.8500
Precision (Macro): 0.8450
Precision (Weighted): 0.8520
Recall (Macro): 0.8400
Recall (Weighted): 0.8500
F1-Score (Macro): 0.8420
F1-Score (Weighted): 0.8480

PER-CLASS METRICS
--------------------------------------------------------------------------------

Left:
  Precision: 0.8600
  Recall:    0.8400
  F1-Score:  0.8500

Right:
  Precision: 0.8500
  Recall:    0.8500
  F1-Score:  0.8500

...

CONFUSION MATRIX
--------------------------------------------------------------------------------
             Left      Right     Hands      Feet     Click
Left          42         3         1         2         2
Right          2        41         3         2         2
Hands          1         2        40         4         3
Feet           2         2         4        41         1
Click          2         1         2         2        43

...

DETAILED CLASSIFICATION REPORT
--------------------------------------------------------------------------------
              precision    recall  f1-score   support

        Left       0.86      0.84      0.85        50
       Right       0.85      0.85      0.85        50
       Hands       0.84      0.83      0.84        50
        Feet       0.85      0.86      0.86        50
       Click       0.87      0.88      0.87        50

    accuracy                           0.85       250
   macro avg       0.85      0.85      0.85       250
weighted avg       0.85      0.85      0.85       250
```

#### 7. `save_results_json(save_path=None) -> None`

Save all evaluation results in JSON format for programmatic access.

**Output:** `outputs/evaluation_results_{timestamp}.json`

**JSON Structure:**
```json
{
  "timestamp": "20260410_143022",
  "n_classes": 5,
  "class_names": ["Left", "Right", "Hands", "Feet", "Click"],
  "metrics": {
    "accuracy": 0.85,
    "precision_macro": 0.845,
    "precision_weighted": 0.852,
    "recall_macro": 0.84,
    "recall_weighted": 0.85,
    "f1_macro": 0.842,
    "f1_weighted": 0.848,
    "precision_per_class": [0.86, 0.85, 0.84, 0.85, 0.87],
    "recall_per_class": [0.84, 0.85, 0.83, 0.86, 0.88],
    "f1_per_class": [0.85, 0.85, 0.84, 0.86, 0.87],
    "confusion_matrix": [[42, 3, 1, 2, 2], ...],
    "classification_report": {...}
  },
  "summary": {
    "total_samples": 250,
    "correct_predictions": 212
  }
}
```

```python
evaluator.save_results_json()

# Load results later
import json
with open('outputs/evaluation_results_20260410_143022.json') as f:
    results = json.load(f)
```

---

## Usage Examples

### Example 1: Basic Evaluation

```python
from src.evaluate import ModelEvaluator
from tensorflow import keras
import numpy as np

# Load trained model
model = keras.models.load_model('models/best_model.h5')

# Load test data
test_data = np.load('data/test_data.npy')
test_labels = np.load('data/test_labels.npy')

# Create evaluator
evaluator = ModelEvaluator(model, n_classes=5)
evaluator.set_class_names(['Left', 'Right', 'Hands', 'Feet', 'Click'])

# Evaluate
metrics = evaluator.evaluate(test_data, test_labels)

# Print key metrics
print(f"Accuracy: {metrics['accuracy']:.4f}")
print(f"Weighted F1: {metrics['f1_weighted']:.4f}")
```

### Example 2: Complete Visualization

```python
# ... after evaluate() call ...

# Generate all visualizations
evaluator.plot_confusion_matrix()
evaluator.plot_metrics_comparison()
evaluator.plot_prediction_distribution()

# Save reports
evaluator.save_evaluation_report()
evaluator.save_results_json()

print("Evaluation complete! Check outputs/ directory for results.")
```

### Example 3: Using Pre-computed Predictions

```python
# If you already have model predictions
predictions = model.predict(test_data)  # Shape: (n_samples, 5)

# Pass predictions directly to evaluate
metrics = evaluator.evaluate(predictions, test_labels)
```

### Example 4: One-Hot Encoded Labels

```python
from tensorflow.keras.utils import to_categorical

# If labels are one-hot encoded
test_labels_onehot = to_categorical(test_labels, num_classes=5)

# Pass directly to evaluate
metrics = evaluator.evaluate(test_data, test_labels_onehot)
```

### Example 5: Custom Paths

```python
# Save all results to custom locations
evaluator.plot_confusion_matrix('results/cm_final.png')
evaluator.plot_metrics_comparison('results/metrics.png')
evaluator.save_evaluation_report('results/report.txt')
evaluator.save_results_json('results/metrics.json')
```

---

## Function Reference

### Top-Level Function

```python
def evaluate_model(
    model_path: str,
    test_data: np.ndarray,
    test_labels: np.ndarray,
    config: Dict = None,
    n_classes: int = 5,
    class_names: list = None
) -> Dict
```

All-in-one evaluation function.

**Usage:**
```python
metrics = evaluate_model(
    model_path='models/cnn_lstm.h5',
    test_data=X_test,
    test_labels=y_test,
    n_classes=5,
    class_names=['Left', 'Right', 'Hands', 'Feet', 'Click']
)
```

---

## Output Files

### Visualizations

| File | Description |
|------|-------------|
| `confusion_matrix_{timestamp}.png` | Confusion matrix heatmap |
| `metrics_comparison_{timestamp}.png` | Per-class metrics bar chart |
| `prediction_distribution_{timestamp}.png` | Probability distributions |

### Reports

| File | Description |
|------|-------------|
| `evaluation_report_{timestamp}.txt` | Comprehensive text report |
| `evaluation_results_{timestamp}.json` | Structured results (JSON) |

### Location

All outputs saved to `outputs/` directory by default.

---

## Metrics Explanation

### Accuracy
Percentage of correct predictions out of total predictions.

$$\text{Accuracy} = \frac{\text{TP} + \text{TN}}{\text{TP} + \text{TN} + \text{FP} + \text{FN}}$$

### Precision
Of all positive predictions, how many were correct.

$$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}$$

### Recall (Sensitivity)
Of all actual positives, how many were found.

$$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$$

### F1-Score
Harmonic mean of precision and recall.

$$\text{F1} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

### Macro vs Weighted

- **Macro**: Simple average of per-class metrics
- **Weighted**: Average weighted by class support (number of samples)

Use **weighted** when classes are imbalanced, **macro** for unbiased comparison.

---

## Advanced Usage

### Class Imbalance Handling

The evaluation automatically handles class imbalances:

```python
# Automatically uses weighted metrics for imbalanced data
metrics = evaluator.evaluate(X_test, y_test)

# Weighted metrics account for class distribution
print(f"F1 (weighted): {metrics['f1_weighted']:.4f}")  # Accounts for imbalance
print(f"F1 (macro):    {metrics['f1_macro']:.4f}")     # Unbiased average
```

### Multi-Language Class Names

```python
# Set custom class names
evaluator.set_class_names(['Izquierda', 'Derecha', 'Manos', 'Pies', 'Click'])
```

### Batch Evaluation

```python
# Evaluate on multiple test sets
test_sets = [
    ('subject_1.npy', 'labels_1.npy'),
    ('subject_2.npy', 'labels_2.npy'),
    ('subject_3.npy', 'labels_3.npy')
]

results = []
for data_file, label_file in test_sets:
    X = np.load(data_file)
    y = np.load(label_file)
    metrics = evaluator.evaluate(X, y)
    results.append(metrics)

# Compare results across subjects
print([r['accuracy'] for r in results])
```

---

## Troubleshooting

### Issue: "No confusion matrix to plot"
**Cause:** `evaluate()` not called before plotting.
**Solution:** Always call `evaluate()` first.

```python
evaluator.evaluate(test_data, test_labels)  # Must call first
evaluator.plot_confusion_matrix()
```

### Issue: Shape mismatch error
**Cause:** Data shape incompatible with model.
**Solution:** Ensure test_data matches model input shape.

```python
# Model was trained with input_shape=(320, 64)
assert test_data.shape == (n_samples, 320, 64)

# If shape is (n_samples, 64, 320), need to transpose
test_data = np.transpose(test_data, (0, 2, 1))
```

### Issue: Low metrics despite good training loss
**Cause:** Model overfitting or class distribution mismatch.
**Solution:** Check per-class metrics to identify problematic classes.

```python
metrics = evaluator.evaluate(test_data, test_labels)

for i, class_name in enumerate(CLASS_NAMES):
    print(f"{class_name}: F1={metrics['f1_per_class'][i]:.4f}")
```

---

## Integration with Training Pipeline

```python
from src.train import ModelTrainer
from src.evaluate import ModelEvaluator

# Train model
trainer = ModelTrainer(config, n_classes=5)
trainer.train(X_train, y_train, X_val, y_val)

# Evaluate on test set
model = trainer.model
evaluator = ModelEvaluator(model, n_classes=5)
evaluator.set_class_names(['Left', 'Right', 'Hands', 'Feet', 'Click'])

metrics = evaluator.evaluate(X_test, y_test)
evaluator.plot_confusion_matrix()
evaluator.save_evaluation_report()
```

---

## Performance Tips

1. **Batch Processing**: Use `batch_size` in config for large datasets
2. **Memory Management**: Process large test sets in chunks if needed
3. **Visualization**: Save plots to disk to avoid memory issues
4. **JSON Export**: Lightweight format for storing results

---

## References

- [Scikit-learn Metrics](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [Confusion Matrix](https://en.wikipedia.org/wiki/Confusion_matrix)
- [F1 Score](https://en.wikipedia.org/wiki/F-score)

---

*Last Updated: April 2026*
