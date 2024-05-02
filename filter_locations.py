import json
import sys

def load_json_file(filepath):
    """ Load JSON data from a file. """
    with open(filepath, 'r') as file:
        return json.load(file)

def save_json_file(data, filepath):
    """ Save JSON data to a file. """
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

def filter_features(features, keywords):
    """ Filter features to include only those containing specified keywords in the name. """
    filtered_features = []
    for feature in features:
        name = feature.get('properties', {}).get('name', '').lower()
        if any(keyword in name for keyword in keywords):
            filtered_features.append(feature)
    return filtered_features

def filter_locations(input_path, output_path, keywords=None):
    # Load JSON data
    data = load_json_file(input_path)

    # Keywords to keep in features
    default_keywords = [
        "park", "plaza", "church", "school", "community center",
        "parking lot", "playground", "promenade", "boardwalk",
        "mall", "garden", "beach", "strip", "overlook"
    ]
    default_keywords = [keyword.lower() for keyword in default_keywords]

    # Filter features
    filtered_data = data.copy()
    filtered_data['features'] = filter_features(data['features'], default_keywords if keywords is None else keywords)

    # Save filtered JSON
    save_json_file(filtered_data, output_path)

    print(f"Filtered GeoJson file has been saved to {output_path}")

if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    keywords = input("List of keywords: ").split()
    filter_locations(input_dir, output_dir, keywords)