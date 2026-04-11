"""
Model evaluation module for BCI.

This module provides comprehensive evaluation metrics and visualizations
for assessing multi-class CNN-LSTM model performance on motor imagery tasks.

Supports:
- Multi-class classification metrics (accuracy, precision, recall, f1-score)
- Per-class and weighted metrics
- Confusion matrix visualization (heatmap)
- Classification report generation
- Results storage (JSON, TXT)
"""

import json
import logging
import os
from typing import Dict, Tuple, Optional, Union

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
from tensorflow import keras

try:
    from utils import get_timestamp
except ImportError:
    def get_timestamp():
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")


logger = logging.getLogger('BCI')


class ModelEvaluator:
    """
    Comprehensive model evaluator for multi-class CNN-LSTM models.
    
    Calculates accuracy, precision, recall, F1-score with macro and weighted
    averaging. Generates confusion matrix heatmaps and classification reports.
    Saves all results to structured files.
    """
    
    def __init__(self, model: keras.Model, config: Dict = None, n_classes: int = 5):
        """
        Initialize model evaluator.
        
        Args:
            model: Trained Keras model
            config: Configuration dictionary (optional)
            n_classes: Number of classification classes (default: 5 for motor imagery)
        """
        self.model = model
        self.config = config or {}
        self.n_classes = n_classes
        self.evaluation_results = {}
        self.class_names = None
        self.timestamp = get_timestamp()
    
    def set_class_names(self, class_names: list) -> None:
        """
        Set class names for better visualization.
        
        Args:
            class_names: List of class names (e.g., ['Left', 'Right', 'Hands', 'Feet', 'Click'])
        """
        if len(class_names) != self.n_classes:
            raise ValueError(f"Expected {self.n_classes} class names, got {len(class_names)}")
        self.class_names = class_names
    
    def evaluate(self, test_data: np.ndarray, test_labels: np.ndarray) -> Dict:
        """
        Comprehensive evaluation on test set.
        
        Calculates:
        - Overall accuracy
        - Precision (macro, weighted, per-class)
        - Recall (macro, weighted, per-class)
        - F1-score (macro, weighted, per-class)
        - Confusion matrix
        
        Args:
            test_data: Test data (n_samples, features...) or predictions
            test_labels: Test labels (n_samples,) or (n_samples, n_classes)
            
        Returns:
            Dictionary of evaluation metrics
        """
        logger.info("Evaluating model on test set...")
        
        # Get predictions
        if test_data.shape[-1] == self.n_classes and test_labels.ndim == 1:
            # test_data contains class probabilities
            predictions = test_data
            predicted_classes = np.argmax(predictions, axis=1)
        else:
            # test_data contains features, need model prediction
            predictions = self.model.predict(test_data, verbose=0)
            predicted_classes = np.argmax(predictions, axis=1)
        
        # Handle test labels
        if test_labels.ndim == 2:
            # One-hot encoded labels
            true_classes = np.argmax(test_labels, axis=1)
        else:
            # Class indices
            true_classes = test_labels.astype(int)
        
        # Calculate metrics
        accuracy_overall = accuracy_score(true_classes, predicted_classes)
        
        metrics = {
            'accuracy': float(accuracy_overall),
            'precision_macro': float(precision_score(
                true_classes, predicted_classes, average='macro', zero_division=0
            )),
            'precision_weighted': float(precision_score(
                true_classes, predicted_classes, average='weighted', zero_division=0
            )),
            'recall_macro': float(recall_score(
                true_classes, predicted_classes, average='macro', zero_division=0
            )),
            'recall_weighted': float(recall_score(
                true_classes, predicted_classes, average='weighted', zero_division=0
            )),
            'f1_macro': float(f1_score(
                true_classes, predicted_classes, average='macro', zero_division=0
            )),
            'f1_weighted': float(f1_score(
                true_classes, predicted_classes, average='weighted', zero_division=0
            )),
            'confusion_matrix': confusion_matrix(true_classes, predicted_classes).tolist()
        }
        
        # Per-class metrics
        precision_per_class = precision_score(
            true_classes, predicted_classes, average=None, zero_division=0
        )
        recall_per_class = recall_score(
            true_classes, predicted_classes, average=None, zero_division=0
        )
        f1_per_class = f1_score(
            true_classes, predicted_classes, average=None, zero_division=0
        )
        
        metrics['precision_per_class'] = precision_per_class.tolist()
        metrics['recall_per_class'] = recall_per_class.tolist()
        metrics['f1_per_class'] = f1_per_class.tolist()
        
        # Classification report
        class_report = classification_report(
            true_classes, predicted_classes,
            target_names=self.class_names,
            zero_division=0,
            output_dict=True
        )
        metrics['classification_report'] = class_report
        
        # Store results for visualization
        self.evaluation_results = {
            'metrics': metrics,
            'predictions': predicted_classes.tolist(),
            'probabilities': predictions.tolist(),
            'true_labels': true_classes.tolist()
        }
        
        # Log metrics
        self._log_metrics(metrics)
        
        return metrics
    
    def _log_metrics(self, metrics: Dict) -> None:
        """Log metrics to logger."""
        logger.info("=" * 80)
        logger.info("EVALUATION METRICS")
        logger.info("=" * 80)
        logger.info(f"Overall Accuracy: {metrics['accuracy']:.4f}")
        logger.info(f"\nPrecision (Macro): {metrics['precision_macro']:.4f}")
        logger.info(f"Precision (Weighted): {metrics['precision_weighted']:.4f}")
        logger.info(f"\nRecall (Macro): {metrics['recall_macro']:.4f}")
        logger.info(f"Recall (Weighted): {metrics['recall_weighted']:.4f}")
        logger.info(f"\nF1-Score (Macro): {metrics['f1_macro']:.4f}")
        logger.info(f"F1-Score (Weighted): {metrics['f1_weighted']:.4f}")
        
        # Per-class metrics
        if self.class_names:
            logger.info("\nPER-CLASS METRICS:")
            logger.info("-" * 80)
            for i, class_name in enumerate(self.class_names):
                logger.info(f"{class_name}:")
                logger.info(f"  Precision: {metrics['precision_per_class'][i]:.4f}")
                logger.info(f"  Recall:    {metrics['recall_per_class'][i]:.4f}")
                logger.info(f"  F1-Score:  {metrics['f1_per_class'][i]:.4f}")
        
        # Confusion matrix
        cm = np.array(metrics['confusion_matrix'])
        logger.info(f"\nConfusion Matrix:\n{cm}")
        
        # Classification report
        logger.info("\nCLASSIFICATION REPORT:")
        logger.info("-" * 80)
        report_text = classification_report(
            self.evaluation_results['true_labels'],
            self.evaluation_results['predictions'],
            target_names=self.class_names,
            zero_division=0
        )
        logger.info(report_text)
    
    def plot_confusion_matrix(self, save_path: Optional[str] = None,
                             figsize: Tuple[int, int] = (10, 8)) -> None:
        """
        Plot and save confusion matrix as heatmap.
        
        Args:
            save_path: Path to save figure (default: outputs/confusion_matrix_{timestamp}.png)
            figsize: Figure size (width, height)
        """
        if 'confusion_matrix' not in self.evaluation_results.get('metrics', {}):
            logger.warning("No confusion matrix to plot")
            return
        
        cm = np.array(self.evaluation_results['metrics']['confusion_matrix'])
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot heatmap
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True,
                   xticklabels=self.class_names, yticklabels=self.class_names,
                   ax=ax, cbar_kws={'label': 'Count'})
        
        ax.set_title('Confusion Matrix', fontsize=14, fontweight='bold')
        ax.set_ylabel('True Label', fontsize=12)
        ax.set_xlabel('Predicted Label', fontsize=12)
        
        plt.tight_layout()
        
        # Save figure
        if save_path is None:
            save_path = f'outputs/confusion_matrix_{self.timestamp}.png'
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved confusion matrix to {save_path}")
    
    def plot_metrics_comparison(self, save_path: Optional[str] = None,
                               figsize: Tuple[int, int] = (12, 6)) -> None:
        """
        Plot comparison of precision, recall, and F1-score per class.
        
        Args:
            save_path: Path to save figure
            figsize: Figure size (width, height)
        """
        if 'precision_per_class' not in self.evaluation_results.get('metrics', {}):
            logger.warning("No per-class metrics to plot")
            return
        
        metrics = self.evaluation_results['metrics']
        precision = metrics['precision_per_class']
        recall = metrics['recall_per_class']
        f1 = metrics['f1_per_class']
        
        x = np.arange(len(precision))
        width = 0.25
        
        fig, ax = plt.subplots(figsize=figsize)
        ax.bar(x - width, precision, width, label='Precision', alpha=0.8)
        ax.bar(x, recall, width, label='Recall', alpha=0.8)
        ax.bar(x + width, f1, width, label='F1-Score', alpha=0.8)
        
        ax.set_xlabel('Class', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Per-Class Metrics Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(self.class_names if self.class_names else [f'Class {i}' for i in range(len(precision))])
        ax.legend()
        ax.set_ylim([0, 1.05])
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = f'outputs/metrics_comparison_{self.timestamp}.png'
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved metrics comparison to {save_path}")
    
    def plot_prediction_distribution(self, save_path: Optional[str] = None,
                                    figsize: Tuple[int, int] = (12, 5)) -> None:
        """
        Plot distribution of predicted probabilities per class.
        
        Args:
            save_path: Path to save figure
            figsize: Figure size (width, height)
        """
        if 'probabilities' not in self.evaluation_results:
            logger.warning("No predictions available")
            return
        
        probabilities = np.array(self.evaluation_results['probabilities'])
        true_labels = np.array(self.evaluation_results['true_labels'])
        
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        
        # Histogram - max probability for each prediction
        max_probs = np.max(probabilities, axis=1)
        correct = predicted_classes = np.argmax(probabilities, axis=1)
        correct_mask = (true_labels == predicted_classes)
        
        axes[0].hist(max_probs[correct_mask], bins=30, alpha=0.7, label='Correct',
                    edgecolor='black')
        axes[0].hist(max_probs[~correct_mask], bins=30, alpha=0.7, label='Incorrect',
                    edgecolor='black')
        axes[0].set_xlabel('Max Predicted Probability', fontsize=11)
        axes[0].set_ylabel('Frequency', fontsize=11)
        axes[0].set_title('Distribution of Predicted Probabilities', fontsize=12, fontweight='bold')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Box plot per class
        data_to_plot = []
        for i in range(self.n_classes):
            class_mask = (true_labels == i)
            if class_mask.any():
                data_to_plot.append(probabilities[class_mask, i])
            else:
                data_to_plot.append([])
        
        axes[1].boxplot(data_to_plot, labels=self.class_names if self.class_names
                       else [f'Class {i}' for i in range(self.n_classes)])
        axes[1].set_ylabel('Predicted Probability', fontsize=11)
        axes[1].set_title('Predicted Probability per Class', fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = f'outputs/prediction_distribution_{self.timestamp}.png'
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved prediction distribution to {save_path}")
    
    def save_evaluation_report(self, save_path: Optional[str] = None) -> None:
        """
        Save comprehensive evaluation report to text file.
        
        Args:
            save_path: Path to save report (default: outputs/evaluation_report_{timestamp}.txt)
        """
        if not self.evaluation_results:
            logger.warning("No evaluation results to save")
            return
        
        if save_path is None:
            save_path = f'outputs/evaluation_report_{self.timestamp}.txt'
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        metrics = self.evaluation_results['metrics']
        
        with open(save_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("MODEL EVALUATION REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            # Overall Metrics
            f.write("OVERALL METRICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Accuracy: {metrics['accuracy']:.4f}\n")
            f.write(f"Precision (Macro): {metrics['precision_macro']:.4f}\n")
            f.write(f"Precision (Weighted): {metrics['precision_weighted']:.4f}\n")
            f.write(f"Recall (Macro): {metrics['recall_macro']:.4f}\n")
            f.write(f"Recall (Weighted): {metrics['recall_weighted']:.4f}\n")
            f.write(f"F1-Score (Macro): {metrics['f1_macro']:.4f}\n")
            f.write(f"F1-Score (Weighted): {metrics['f1_weighted']:.4f}\n")
            
            # Per-Class Metrics
            f.write("\n\nPER-CLASS METRICS\n")
            f.write("-" * 80 + "\n")
            for i, class_name in enumerate(self.class_names if self.class_names
                                          else [f'Class {j}' for j in range(self.n_classes)]):
                f.write(f"\n{class_name}:\n")
                f.write(f"  Precision: {metrics['precision_per_class'][i]:.4f}\n")
                f.write(f"  Recall:    {metrics['recall_per_class'][i]:.4f}\n")
                f.write(f"  F1-Score:  {metrics['f1_per_class'][i]:.4f}\n")
            
            # Confusion Matrix
            f.write("\n\nCONFUSION MATRIX\n")
            f.write("-" * 80 + "\n")
            cm = np.array(metrics['confusion_matrix'])
            
            # Matrix
            if self.class_names:
                # Header
                f.write("             " + "  ".join(f"{name:>8}" for name in self.class_names) + "\n")
                for i, row in enumerate(cm):
                    f.write(f"{self.class_names[i]:>12}" + "  ".join(f"{val:>8d}" for val in row) + "\n")
            else:
                f.write(f"{cm}\n")
            
            # Summary
            f.write("\n\nCONFUSION MATRIX ANALYSIS\n")
            f.write("-" * 80 + "\n")
            for i in range(cm.shape[0]):
                true_positives = cm[i, i]
                false_negatives = cm[i, :].sum() - true_positives
                false_positives = cm[:, i].sum() - true_positives
                class_name = self.class_names[i] if self.class_names else f'Class {i}'
                f.write(f"\n{class_name}:\n")
                f.write(f"  True Positives: {true_positives}\n")
                f.write(f"  False Positives: {false_positives}\n")
                f.write(f"  False Negatives: {false_negatives}\n")
            
            # Classification Report
            f.write("\n\nDETAILED CLASSIFICATION REPORT\n")
            f.write("-" * 80 + "\n")
            report_text = classification_report(
                self.evaluation_results['true_labels'],
                self.evaluation_results['predictions'],
                target_names=self.class_names,
                zero_division=0
            )
            f.write(report_text)
        
        logger.info(f"Saved evaluation report to {save_path}")
    
    def save_results_json(self, save_path: Optional[str] = None) -> None:
        """
        Save all evaluation results to JSON file.
        
        Args:
            save_path: Path to save JSON (default: outputs/evaluation_results_{timestamp}.json)
        """
        if not self.evaluation_results:
            logger.warning("No evaluation results to save")
            return
        
        if save_path is None:
            save_path = f'outputs/evaluation_results_{self.timestamp}.json'
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Prepare data for JSON serialization
        results_json = {
            'timestamp': self.timestamp,
            'n_classes': self.n_classes,
            'class_names': self.class_names,
            'metrics': self.evaluation_results['metrics'],
            'summary': {
                'total_samples': len(self.evaluation_results['true_labels']),
                'correct_predictions': sum(
                    p == t for p, t in zip(
                        self.evaluation_results['predictions'],
                        self.evaluation_results['true_labels']
                    )
                )
            }
        }
        
        with open(save_path, 'w') as f:
            json.dump(results_json, f, indent=2)
        
        logger.info(f"Saved JSON results to {save_path}")




def evaluate_model(model_path: str, test_data: np.ndarray,
                   test_labels: np.ndarray, config: Dict = None,
                   n_classes: int = 5, class_names: list = None) -> Dict:
    """
    Evaluate a trained model with comprehensive metrics and visualizations.
    
    Generates:
    - Accuracy, precision, recall, F1-score (overall, macro, weighted, per-class)
    - Confusion matrix heatmap
    - Metrics comparison bar chart
    - Prediction distribution histogram
    - Comprehensive text report
    - JSON results file
    
    Args:
        model_path: Path to trained Keras model
        test_data: Test data or model predictions
        test_labels: Test labels (integer class indices or one-hot encoded)
        config: Configuration dictionary (optional)
        n_classes: Number of classes (default: 5)
        class_names: List of class names for better visualization
        
    Returns:
        Dictionary of evaluation metrics
    """
    logger.info(f"Loading model from {model_path}...")
    model = keras.models.load_model(model_path)
    
    # Create evaluator
    evaluator = ModelEvaluator(model, config=config, n_classes=n_classes)
    if class_names:
        evaluator.set_class_names(class_names)
    
    # Evaluate
    metrics = evaluator.evaluate(test_data, test_labels)
    
    # Plot results
    logger.info("Generating visualizations...")
    evaluator.plot_confusion_matrix()
    evaluator.plot_metrics_comparison()
    evaluator.plot_prediction_distribution()
    
    # Save results
    logger.info("Saving results...")
    evaluator.save_evaluation_report()
    evaluator.save_results_json()
    
    return metrics


if __name__ == '__main__':
    # Example usage - setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Evaluation module loaded successfully")
