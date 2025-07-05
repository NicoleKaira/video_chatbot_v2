import json

def calculate_average_metrics(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Initialize accumulators
    total_context_precision = 0.0
    total_response_relevancy = 0.0
    total_faithfulness_result = 0.0
    total_context_recall = 0.0
    count = 0

    for entry in data:
        try:
            total_context_precision += entry["context_precision"]
            total_response_relevancy += entry["response_relevancy"]
            total_faithfulness_result += entry["faithfulness_result"]
            total_context_recall += entry["context_recall"]
            count += 1
        except KeyError:
            # Skip entries missing any metric
            continue

    if count == 0:
        raise ValueError("No valid entries with all four metrics found.")

    averages = {
        "average_context_precision": total_context_precision / count,
        "average_response_relevancy": total_response_relevancy / count,
        "average_faithfulness_result": total_faithfulness_result / count,
        "average_context_recall": total_context_recall / count,
        "total_entries_used": count
    }

    return averages

# Example usage
json_file = "evaluation_results_pre_t.json"  # Replace with your JSON file path
averages = calculate_average_metrics(json_file)

# Print results
for metric, value in averages.items():
    print(f"{metric}: {value:.4f}")
