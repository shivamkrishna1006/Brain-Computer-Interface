# Evaluation Quick Reference

## Basic Evaluation Pipeline

```python
from src.evaluate import ModelEvaluator
from tensorflow import keras

# Load model
model = keras.models.load_model('models/best_model.h5')

# Create evaluator
evaluator = ModelEvaluator(model, n_classes=5)
evaluator.set_class_names(['Left', 'Right', 'Hands', 'Feet', 'Click'])

# Evaluate
metrics = evaluator.evaluate(test_data, test_labels)

# Visualize
evaluator.plot_confusion_matrix()
evaluator.plot_metrics_comparison()
evaluator.plot_prediction_distribution()

# Save results
evaluator.save_evaluation_report()
evaluator.save_results_json()
```

---

## Key Metrics

| Metric | Formula | Meaning |
|--------|---------|---------|
| **Accuracy** | (TP+TN)/(TP+TN+FP+FN) | % correct predictions |
| **Precision** | TP/(TP+FP) | % positive predictions correct |
| **Recall** | TP/(TP+FN) | % actual positives found |
| **F1-Score** | 2×(P×R)/(P+R) | Harmonic mean of P and R |

**Macro**: Simple average across classes  
**Weighted**: Average weighted by class support

---

## ModelEvaluator Methods

| Method | Purpose | Output |
|--------|---------|--------|
| `evaluate()` | Calculate all metrics | Dict of metrics |
| `plot_confusion_matrix()` | Heatmap visualization | PNG image |
| `plot_metrics_comparison()` | Per-class bar chart | PNG image |
| `plot_prediction_distribution()` | Probability histograms | PNG image |
| `save_evaluation_report()` | Text report with details | TXT file |
| `save_results_json()` | Structured results | JSON file |
| `set_class_names()` | Set custom label names | N/A |

---

## Access Metrics

```python
metrics = evaluator.evaluate(X_test, y_test)

# Overall metrics
acc = metrics['accuracy']
prec_macro = metrics['precision_macro']
recall_macro = metrics['recall_macro']
f1_weighted = metrics['f1_weighted']

# Per-class metrics (lists)
precision_per_class = metrics['precision_per_class']  # [0.86, 0.85, ...]
recall_per_class = metrics['recall_per_class']
f1_per_class = metrics['f1_per_class']

# Detailed data
cm = metrics['confusion_matrix']  # 2D list
report = metrics['classification_report']  # Dict with detailed stats
```

---

## Output Files

Default location: `outputs/`

**Generated Files:**
- `confusion_matrix_{timestamp}.png` - Heatmap
- `metrics_comparison_{timestamp}.png` - Bar chart
- `prediction_distribution_{timestamp}.png` - Histograms
- `evaluation_report_{timestamp}.txt` - Text summary
- `evaluation_results_{timestamp}.json` - Structured data

---

## Common Patterns

### Load and Evaluate Trained Model
```python
model = keras.models.load_model('models/trained_model.h5')
evaluator = ModelEvaluator(model, n_classes=5)
metrics = evaluator.evaluate(X_test, y_test)
```

### From Pre-computed Predictions
```python
predictions = model.predict(X_test)  # Shape: (n_samples, 5)
metrics = evaluator.evaluate(predictions, y_test)
```

### With One-Hot Labels
```python
from tensorflow.keras.utils import to_categorical
y_onehot = to_categorical(y_test, num_classes=5)
metrics = evaluator.evaluate(X_test, y_onehot)
```

### Custom Save Paths
```python
evaluator.plot_confusion_matrix('my_results/cm.png')
evaluator.save_evaluation_report('my_results/report.txt')
evaluator.save_results_json('my_results/metrics.json')
```

---

## Example Output

```
Accuracy:        0.8500
Precision (macro):   0.8450
Recall (macro):      0.8400
F1-Score (macro):    0.8420

Per-Class:
  Left:    P=0.86, R=0.84, F1=0.85
  Right:   P=0.85, R=0.85, F1=0.85
  Hands:   P=0.84, R=0.83, F1=0.84
  Feet:    P=0.85, R=0.86, F1=0.86
  Click:   P=0.87, R=0.88, F1=0.87
```

---

## Run Example Script

```bash
python evaluate_eeg_model.py
```

Generates all visualizations and reports automatically.

---

## Interpretation Guide

- **High accuracy but low recall for class X**: Model rarely predicts class X
- **High F1 but low precision**: False positives present
- **High recall but low precision**: Missing specificity
- **Confusion between classes X and Y**: Check if similar features

---

## Tips

1. Always call `evaluate()` before plotting
2. Use `set_class_names()` for readable outputs
3. Check per-class metrics to identify problem classes
4. Use weighted metrics for imbalanced datasets
5. Compare accuracy and F1-score (F1 better for imbalance)

---

*Quick Reference - See EVALUATION_GUIDE.md for complete documentation*
