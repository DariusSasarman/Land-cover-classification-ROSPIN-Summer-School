"""
Compares the available Random Forest and multispectral reports and
reports which one performed better. Run the matching training scripts
first.
"""

import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_ROOT = os.path.join(REPO_ROOT, "reports")

REPORTS = {
    "Baseline (RGB stats)": os.path.join(REPORTS_ROOT, "baseline_rf_report.txt"),
    "Spectral (B08/B11/B12 + indices)": os.path.join(REPORTS_ROOT, "spectral_rf_report.txt"),
}


def parse_summary(path):
    with open(path) as f:
        text = f.read()
    acc = re.search(r"accuracy\s+([\d.]+)\s+\d+", text)
    macro = re.search(r"macro avg\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", text)
    weighted = re.search(r"weighted avg\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", text)
    return {
        "accuracy": float(acc.group(1)) if acc else None,
        "macro_f1": float(macro.group(3)) if macro else None,
        "weighted_f1": float(weighted.group(3)) if weighted else None,
    }


def main():
    results = {}
    for name, path in REPORTS.items():
        if not os.path.exists(path):
            print(f"Missing '{path}' - run the matching training script first.")
            continue
        results[name] = parse_summary(path)

    if len(results) < 2:
        print("\nNeed at least two reports present to compare.")
        return

    header = f"{'Model':38s}{'Accuracy':>10s}{'Macro F1':>10s}{'Weighted F1':>13s}"
    lines = [header]
    for name, m in results.items():
        lines.append(f"{name:38s}{m['accuracy']:>10.3f}{m['macro_f1']:>10.3f}{m['weighted_f1']:>13.3f}")

    winner = max(
        results,
        key=lambda name: results[name]["weighted_f1"] if results[name]["weighted_f1"] is not None else -1,
    )
    lines.append(f"\nBest model by weighted F1: {winner}")

    output = "\n".join(lines)
    print(output)

    os.makedirs("reports", exist_ok=True)
    with open("reports/comparison_report.txt", "w") as f:
        f.write(output)
    print("\nSaved to reports/comparison_report.txt")


if __name__ == "__main__":
    main()
