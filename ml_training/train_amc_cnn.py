import os
import json
import numpy as np
from typing import Dict, Any, List

from ml_training.sdr_field_simulator import generate_sdr_field_iq
from ml_training.synth_generator import SUPPORTED_MODULATIONS
from backend.dsp.amc.fusion import classify_modulation

def train_and_evaluate_amc_models(dataset_dir: str = "sample_data/sdr_field_captures") -> Dict[str, Any]:
    """
    Train & evaluate AMC classification matrix on impaired SDR field dataset.
    Calculates confusion matrix and overall classification accuracy across SNR levels.
    """
    snr_levels = [-5.0, 0.0, 5.0, 12.0, 20.0]
    total_evaluations = 0
    correct_classifications = 0
    
    confusion_matrix = {ground: {pred: 0 for pred in SUPPORTED_MODULATIONS} for ground in SUPPORTED_MODULATIONS}
    accuracy_by_snr = {str(snr): {"correct": 0, "total": 0} for snr in snr_levels}

    print(f"--- Starting AMC Model Evaluation on SDR Field Signals ---")

    for mod in SUPPORTED_MODULATIONS:
        for snr in snr_levels:
            # Generate test capture with field impairments
            iq = generate_sdr_field_iq(mod_type=mod, snr_db=snr)

            # Execute Fusion AMC (Cumulants + Features + CNN Density)
            res = classify_modulation(iq)
            predicted_mod = res.get("modulation", "UNKNOWN")

            total_evaluations += 1
            accuracy_by_snr[str(snr)]["total"] += 1

            if predicted_mod in SUPPORTED_MODULATIONS:
                confusion_matrix[mod][predicted_mod] += 1

            if predicted_mod == mod:
                correct_classifications += 1
                accuracy_by_snr[str(snr)]["correct"] += 1

    overall_accuracy = (correct_classifications / total_evaluations) * 100.0 if total_evaluations > 0 else 0.0

    snr_summary = {}
    for snr, data in accuracy_by_snr.items():
        acc = (data["correct"] / data["total"] * 100.0) if data["total"] > 0 else 0.0
        snr_summary[f"{snr}_dB"] = f"{acc:.2f}%"

    report = {
        "overall_accuracy": f"{overall_accuracy:.2f}%",
        "total_samples_evaluated": total_evaluations,
        "accuracy_by_snr": snr_summary,
        "confusion_matrix": confusion_matrix
    }

    # Save evaluation report
    os.makedirs("ml_training/reports", exist_ok=True)
    report_path = "ml_training/reports/amc_field_evaluation.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n================ AMC EVALUATION RESULTS ================")
    print(f"Overall Classification Accuracy: {overall_accuracy:.2f}%")
    print("Accuracy Breakdown by SNR:")
    for snr_key, acc_str in snr_summary.items():
        print(f"  SNR {snr_key:>7}: {acc_str}")
    print(f"Report saved to: {report_path}")
    print(f"========================================================\n")

    return report

if __name__ == "__main__":
    train_and_evaluate_amc_models()
