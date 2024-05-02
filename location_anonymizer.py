import sys
import json
import random
import os

def generate_noise():
    """
    Return a noise value
    """
    return random.randrange(1, 10) * (10 ** 4)


def anonymize_sensitive_locations(timeline_objects, random_noise):
    """
    Anonymize sensitive location data (E.g. Home Address)

    Parameters:
        - `timeline_objects`: a list of timeline_objects from Google Takeout Data

    Returns: A list of anonymized timeline_objects
    """
    for idx, timeline_object in enumerate(timeline_objects):
        if "placeVisit" in timeline_object:
            if "location" in timeline_object["placeVisit"]:
                if "semanticType" in timeline_object["placeVisit"]["location"]:
                    if timeline_object["placeVisit"]["location"]["semanticType"] == "TYPE_HOME":
                        timeline_objects[idx]["placeVisit"]["location"]["semanticType"] = "TYPE_UNKNOWN"
                        timeline_objects[idx]["placeVisit"]["location"]["latitudeE7"] += random_noise
                        timeline_objects[idx]["placeVisit"]["location"]["longitudeE7"] -= random_noise
                        timeline_objects[idx]["placeVisit"]["location"]["address"] = "Google Searched Place"
            if "otherCandidateLocations" in timeline_object["placeVisit"]:
                for candidate in timeline_object["placeVisit"]["otherCandidateLocations"]:
                    if "semanticType" in candidate:
                        if candidate["semanticType"] == "TYPE_HOME":
                            candidate["semanticType"] = "TYPE_SEARCHED_ADDRESS"
    return timeline_objects

def anonymize_data(input_dir, output_dir):
    """
    Generate a random noise specifically used for this participant. 

    Returns:
        - `output_dir`: the path to the output directory
    """
    random_noise = generate_noise()

    subfolders = [folder for folder in os.listdir(
        input_dir) if os.path.isdir(os.path.join(input_dir, folder))]

    for subfolder in subfolders:
        subfolder_path = os.path.join(input_dir, subfolder)
        for filename in os.listdir(subfolder_path):
            if filename.endswith('.json'):
                file_path = os.path.join(subfolder_path, filename)
                with open(file_path, 'r') as json_file:
                    try:
                        maps_json = json.load(json_file)
                        if not maps_json:
                            print(f"No data found in the file {file_path}")
                            continue
                        # anonymize locations
                        maps_json["timelineObjects"] = anonymize_sensitive_locations(
                            maps_json["timelineObjects"], random_noise)
                        output_file_dir = os.path.join(output_dir, "anonymized_location_data",subfolder)
                        if not os.path.exists(output_file_dir):
                            os.makedirs(output_file_dir)
                        output_file = os.path.join(output_file_dir, filename)
                        json.dump(maps_json, open(output_file, "w"), indent=2)

                    except json.JSONDecodeError:
                        print(f"Error parsing JSON in file: {file_path}")
                        return None
    print(f"Sensitive data has been anonymized and saved at {output_dir}")

    return os.path.join(output_dir, "anonymized_location_data")


if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    anonymize_data(input_dir, output_dir)
