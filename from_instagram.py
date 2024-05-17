import json
import sys
import os
from common_utils import convert_to_timestamp
from geojson import Point
import datetime


def is_unix_timestamp(timestamp_str):
    try:
        timestamp_int = int(timestamp_str)
        return True  # Conversion successful, indicating a valid UNIX timestamp
    except ValueError:
        return False 
    
def is_iso_timestamp(timestamp_str):
    try:
        datetime.datetime.fromisoformat(timestamp_str)
        return True  # Conversion successful, indicating a valid ISO timestamp
    except ValueError:
        return False  # Conversion failed, indicating it's not a valid ISO timestamp
    
def extract_participant_name(path):
    # Split the path using the directory separator
    path_parts = path.split(os.path.sep)
    # Iterate through the path parts to find the participant's name
    for part in reversed(path_parts):
        # Check if the part looks like a participant name (e.g., "participant1")
        if part.startswith("participant"):
            return part
    return None

def extract_stories_with_exif_data(path_to_stories_data):
    """
    Extract the exif data from photo stories which contain exif data. The extracted exif data contains: `latitude`, `longitude`, `url`, `datetime_original` (some may not have it)

    Parameters:
        - path_to_stories_data (str): path to the stories.json file

    Returns:
        - stories_info (list): a list of dict each of which contains the exif data of stories
    """
    with open(path_to_stories_data, "r", encoding='utf-8') as json_file:
        try:
            stories_data = json.load(json_file)
        except json.JSONDecodeError:
            print(f"Error parsing JSON in file: {path_to_stories_data}")

    stories_info = []
    for story in stories_data["ig_stories"]:
        story_data = {}
        if "media_metadata" in story and "photo_metadata" in story["media_metadata"] and "exif_data" in story["media_metadata"]["photo_metadata"]:
            exif_data = story["media_metadata"]["photo_metadata"]["exif_data"]
            if len(exif_data) == 2:
                if "latitude" in exif_data[0] and "longitude" in exif_data[0]:
                    story_data["latitude"] = exif_data[0]["latitude"]
                    story_data["longitude"] = exif_data[0]["longitude"]
                if "date_time_original" in exif_data[1]:
                    story_data["datetime_original"] = str(exif_data[1]["date_time_original"])
                else:
                    story_data["datetime_story"] = str(story["creation_timestamp"])
                story_data["url"] = story["uri"]
                stories_info.append(story_data)
            else:
                story_data["datetime_story"] = str(story["creation_timestamp"])
                story_data["url"] = story["uri"]
                stories_info.append(story_data)
    return stories_info


def extract_media_path(media_path):
    """
    Parameters:
        - `media_path` (str): a string representing the path to a story media (photo)

    Returns:
        - `path` (str): extracted path

    Example Input:
        - media/stories/202108/232972524_784218242254668_6118226980962968239_n_17868053870536088.jpg
    """
    parts = media_path.split("media/stories")
    if len(parts) >= 2:
        return parts[1]
    else:
        print("The input string does not contain 'media/stories'")


def create_story_point(stories_info, input_path, google_data_path, buffer_hours=0):
    """
    Parameters: 
        - `stories_info` (list): a list of extracted exif data from the Instagram stories

    Returns:
        - `points` (list): a list of geojson Points each of which contains the geojson data of where the image used in that story was taken along with the timestamp and corresponding url to the image
    """
    points = []
    for story_info in stories_info:
        properties = {}
        if "longitude" in story_info and "latitude" in story_info:
            properties["longitude"] = story_info["longitude"]
            properties["latitude"] = story_info["latitude"]
            if story_info["url"].lower().endswith("jpg"):
                properties["has_url"] = True
            if "datetime_original" in story_info:
                if is_unix_timestamp(story_info["datetime_original"]) == False:
                    timestamp = convert_to_timestamp(story_info["datetime_original"])
                properties["timestamp"] = timestamp
                properties["datetime"] = str(datetime.datetime.fromtimestamp(timestamp))
            if str(extract_media_path(story_info["url"])).endswith(".jpg"):
                properties["relative_url"] = story_info["url"]
                if story_info["url"].startswith("media/stories/"):
                    properties["has_image"] = True
                    url = "http://localhost:3000/" + extract_participant_name(input_path) + "/" + story_info["url"].split("/")[-1]
                    properties["url"] = url
                    properties["<img>_tooltip"] = url
            point_and_properties = (
                Point((story_info["longitude"], story_info["latitude"])), 
                properties
            )
            points.append(point_and_properties)
        else:
            result = find_matching_place_visit_coordinates(story_info, google_data_path, buffer_hours)
            if result == False:
                pass
            else:
                if story_info["url"].lower().endswith("jpg"):
                    properties["has_image"] = True
                    properties["longitude"] = result[1]/ 10e6
                    properties["latitude"] = result[0]/ 10e6
                    url = "http://localhost:3000/" + extract_participant_name(input_path) + "/" + story_info["url"].split("/")[-1]
                    properties["url"] = url
                    properties["<img>_tooltip"] = url
                    point_and_properties = (Point((properties["longitude"], properties["latitude"])), properties)
                    points.append(point_and_properties)
    return points

def find_matching_place_visit_coordinates(story_info, path, buffer_hours):
    timestamp_str = story_info.get('datetime_original') or story_info.get('datetime_story')
    if not timestamp_str:
        print("Error: No valid timestamp found.")
        return None

    creation_time = None
    if timestamp_str.isdigit():
        creation_time = datetime.datetime.fromtimestamp(int(timestamp_str))
    elif is_iso_timestamp(timestamp_str):
        creation_time = datetime.datetime.fromisoformat(timestamp_str.rstrip('Z'))
    else:
        try:
            creation_time = datetime.datetime.strptime(timestamp_str, "%Y:%m:%d %H:%M:%S")
        except ValueError:
            print("Error: Timestamp format is not recognized.")
            return None

    def check_timestamp_in_place_visit(creation_time, timeline_objects, buffer_hours):
        buffer_delta = datetime.timedelta(hours=buffer_hours)
        closest_location = None
        closest_time_difference = datetime.timedelta.max

        if 'timelineObjects' not in timeline_objects:
            print("no timelineObjects")

        for timeline_object in timeline_objects.get('timelineObjects', []):
            if "placeVisit" in timeline_object:
                duration = timeline_object['placeVisit']['duration']
                start_timestamp = datetime.datetime.fromisoformat(duration['startTimestamp'].rstrip('Z')) - buffer_delta
                end_timestamp = datetime.datetime.fromisoformat(duration['endTimestamp'].rstrip('Z')) + buffer_delta
                if start_timestamp <= creation_time <= end_timestamp:
                    time_difference = min(abs(creation_time - start_timestamp), abs(creation_time - end_timestamp))
                    if time_difference < closest_time_difference:
                        closest_time_difference = time_difference
                        location = timeline_object['placeVisit']['location']
                        closest_location = (location['latitudeE7'], location['longitudeE7'])

            if "activitySegment" in timeline_object:
                activity = timeline_object["activitySegment"]
                if "duration" in activity:
                    duration = activity['duration']
                    start_timestamp = datetime.datetime.fromisoformat(duration['startTimestamp'].rstrip('Z')) - buffer_delta
                    end_timestamp = datetime.datetime.fromisoformat(duration['endTimestamp'].rstrip('Z')) + buffer_delta
                    if start_timestamp <= creation_time <= end_timestamp:
                        time_difference = min(abs(creation_time - start_timestamp), abs(creation_time - end_timestamp))
                        if time_difference < closest_time_difference:
                            closest_time_difference = time_difference
                            location = activity["startLocation"]
                            closest_location = (location['latitudeE7'], location['longitudeE7'])

        if closest_location is not None:
            print("Found a matching location with time difference: " + str(closest_time_difference))

        return closest_location

    
    # Traverse the directory structure
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.json'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    place_visit_json = json.load(f)
                    result = check_timestamp_in_place_visit(creation_time, place_visit_json, buffer_hours)
                    if result:
                        return result
    
    return False



