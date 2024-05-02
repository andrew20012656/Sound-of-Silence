from filter_locations import *
from location_anonymizer import *
from to_heatmap import *

def get_filter_keywords():
    while True:
        print()
        keywords_input = input("Enter the list of filtering keywords separated by spaces: ")
        keywords = keywords_input.split()
        if keywords:
            print("Filtering on " + str(keywords))
            return keywords
        else:
            print("No keywords entered")
            return None

def get_filter_filename():
     while True:
        print()
        filename = input("Enter the filename for the output file (without .json extension): ")
        if '.' in filename:
            print("Please enter a filename without any file extension.")
        elif not filename:
            print("Please enter the filename")
        else:
            return filename
        
def main():
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    ins_stories_file_path = sys.argv[3]

    filter_enabled = ask_true_false("Filter Locations?")
    filter_keywords = None
    if filter_enabled:
        filter_keywords = get_filter_keywords()
        filtered_filename = get_filter_filename()

    os.makedirs(output_dir, exist_ok=True)

    print("Start anonymizing participant's data")
    anonymized_data_dir = anonymize_data(input_dir, output_dir)

    places_visited = []
    if ins_stories_file_path is not None:
        path_to_stories_data = ins_stories_file_path
        stories_info = extract_stories_with_exif_data(path_to_stories_data)
        points = create_story_point(stories_info, ins_stories_file_path, input_dir)
        for point in points:
            places_visited.append(point)
            # Process images based on those points
            # point["relative_url"].split("/")[-1]

    subfolders = [f for f in os.listdir(anonymized_data_dir) if os.path.isdir(os.path.join(anonymized_data_dir, f))]
    for subfolder in subfolders:
        subfolder_path = os.path.join(anonymized_data_dir, subfolder)
        for filename in os.listdir(subfolder_path):
            if filename.endswith('.json'):
                file_path = os.path.join(subfolder_path, filename)
                with open(file_path, 'r') as json_file:
                    try:
                        maps_json = json.load(json_file)
                    except json.JSONDecodeError:
                        print(f"Error parsing JSON in file: {file_path}")

                    for idx, timeline_object in enumerate(maps_json["timelineObjects"]):
                        if "placeVisit" in timeline_object:
                            if "activitySegment" in maps_json["timelineObjects"][idx - 1]:
                                activitySegment = maps_json["timelineObjects"][idx - 1]["activitySegment"]
                                if "activityType" in activitySegment:
                                    transportation_mode = maps_json["timelineObjects"][idx - 1]["activitySegment"]["activityType"]
                                    places_visited.append(place_visit(timeline_object["placeVisit"], transportation_mode))
                                else:
                                    places_visited.append(place_visit(timeline_object["placeVisit"]))
                            else:
                                places_visited.append(place_visit(timeline_object["placeVisit"]))
        

    output_geojson = make_geojson(places_visited)
    output_file = os.path.join(output_dir, output_dir.split("/")[-1]) + ".json"
    json.dump(output_geojson, open(output_file, "w"), indent=2)

    if filter_enabled:
        filtered_output_file = os.path.join(output_dir, filtered_filename) + ".json"
        if filter_keywords is None:
            filter_locations(output_file, filtered_output_file)
        else:
            filter_locations(output_file, filtered_output_file, filter_keywords)
    
    # remove the folder containing all anonymized Google location data
    # comment out this line if want to keep the anonymized location data
    shutil.rmtree(anonymized_data_dir)
if __name__ == "__main__":
    main()

