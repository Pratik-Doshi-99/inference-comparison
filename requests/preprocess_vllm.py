import json
import random

# Path to the sharedgpt52k dataset file (assumes it's in JSON format)
dataset_path = "sg_52k.json"

# Load the dataset
def load_dataset(path):
    with open(path, "r") as file:
        data = json.load(file)
    return data

# Process the dataset to create the desired structure
def process_dataset(dataset, sample_size):
    # Randomly select `sample_size` entries from the dataset
    sampled_data = random.sample(dataset, sample_size)
    
    # Extract human prompts from the conversations and transform them
    processed_data = []
    for entry in sampled_data:
        for conversation in entry.get("conversations", []):
            if conversation.get("from") == "human":
                processed_data.append({
                    "model": "meta-llama/Llama-3.1-8B-Instruct",
                    "prompt": conversation.get("value", ""),
                    "max_tokens": 200,
                    "stream": True,
                    "temperature": 0.7
                })
    
    return processed_data

# Save the processed data to a JSON file
def save_to_json(data, output_path):
    with open(output_path, "w") as file:
        json.dump(data, file, indent=2)

# Main function
def main():
    # Load the dataset
    dataset = load_dataset(dataset_path)

    # Process the dataset to get 500 samples
    processed_data = process_dataset(dataset, 500)

    # Save the processed data to a file
    output_path = "vllm.json"
    save_to_json(processed_data, output_path)

    print(f"Processed data saved to {output_path}")

if __name__ == "__main__":
    main()
