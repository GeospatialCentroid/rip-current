"""
The following analizes the model output values compared with a source of truth

Ref: https://chatgpt.com/share/68792e4f-49c4-8004-bd6d-05190393bad7
python src/compare_models.py \
  --file combined_output.csv \
  --objectid_col OBJECTID \
  --model_col model \
  --manual_value manual \
  --value_cols age gender WFO

"""

import pandas as pd
import argparse
import sys
from tabulate import tabulate

import pandas as pd
import argparse
import sys
from tabulate import tabulate

def compare_models_long(file, objectid_col, model_col, manual_value, value_cols):
    """
    Compare model outputs in long format to manual entries, outputting total and per-column accuracy as Markdown table.
    """
    try:
        df = pd.read_excel(file) if file.endswith('.xlsx') else pd.read_csv(file)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    required_cols = [objectid_col, model_col] + value_cols
    for col in required_cols:
        if col not in df.columns:
            print(f"Missing column '{col}' in the data.")
            sys.exit(1)

    models = df[model_col].unique()
    results = {}

    for model in models:
        if model == manual_value:
            continue

        total_correct = 0
        total_comparisons = 0
        col_correct = {col: 0 for col in value_cols}
        col_total = {col: 0 for col in value_cols}

        for obj_id in df[objectid_col].unique():
            manual_row = df[(df[objectid_col] == obj_id) & (df[model_col] == manual_value)]
            model_row = df[(df[objectid_col] == obj_id) & (df[model_col] == model)]

            if manual_row.empty or model_row.empty:
                continue  # Skip incomplete pairs

            for col in value_cols:
                manual_val = manual_row.iloc[0][col]
                model_val = model_row.iloc[0][col]

                if pd.isna(manual_val):
                    continue

                col_total[col] += 1
                total_comparisons += 1

                if manual_val == model_val:
                    col_correct[col] += 1
                    total_correct += 1

        # Calculate accuracies
        col_accuracies = {
            col: round((col_correct[col] / col_total[col]) * 100, 2) if col_total[col] > 0 else None
            for col in value_cols
        }
        total_accuracy = round((total_correct / total_comparisons) * 100, 2) if total_comparisons > 0 else None

        results[model] = {
            "total_accuracy": total_accuracy,
            "col_accuracies": col_accuracies
        }

    # Prepare markdown table
    headers = ["Model", "Total Accuracy"] + value_cols
    table = []

    for model, res in results.items():
        row = [model, f"{res['total_accuracy']}%"]
        for col in value_cols:
            acc = res['col_accuracies'][col]
            acc_display = f"{acc}%" if acc is not None else "N/A"
            row.append(acc_display)
        table.append(row)

    print("\nModel Comparison Results (Markdown Table):\n")
    print(tabulate(table, headers=headers, tablefmt="github"))

    # Identify best model by total accuracy
    if results:
        valid_models = {m: r['total_accuracy'] for m, r in results.items() if r['total_accuracy'] is not None}
        if valid_models:
            best_model = max(valid_models, key=valid_models.get)
            print(f"\nBest performing model: {best_model} with {valid_models[best_model]}% total accuracy.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare model outputs to manual entries in long format spreadsheet.")
    parser.add_argument("--file", type=str, required=True, help="Input spreadsheet file (.csv or .xlsx)")
    parser.add_argument("--objectid_col", type=str, required=True, help="Column name for OBJECTID (unique key)")
    parser.add_argument("--model_col", type=str, required=True, help="Column name indicating model source (e.g., 'model')")
    parser.add_argument("--manual_value", type=str, required=True, help="Value in model_col that represents manual/source-of-truth")
    parser.add_argument("--value_cols", type=str, nargs='+', required=True, help="Value columns to compare (e.g., value value2)")

    args = parser.parse_args()

    compare_models_long(
        file=args.file,
        objectid_col=args.objectid_col,
        model_col=args.model_col,
        manual_value=args.manual_value,
        value_cols=args.value_cols
    )
