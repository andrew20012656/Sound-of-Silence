import sys
import os
import json
import re
import chardet
from pprint import pprint
from common_utils import *

class DataValidator:
    def __init__(self, input_dir, output_dir = None):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.stats = {'basic_stats': {}}
    
    def load_history(self):
        subfolders = [folder for folder in os.listdir(self.input_dir) if os.path.isdir(os.path.join(self.input_dir, folder))]

        num_empty_files = 0
        num_empty_data_files = 0
        places_visited = set()

        timeline_objects_by_year = {} 
        for subfolder in subfolders:
            subfolder_path = os.path.join(self.input_dir, subfolder)
            places_visited_by_year = set()
            for filename in os.listdir(subfolder_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(subfolder_path, filename)
                    enc = chardet.detect(open(file_path,'rb').read())['encoding']
                    with open(file_path, 'r', encoding=enc) as json_file:
                        try:
                            maps_json = json.load(json_file)
                            if not maps_json:
                                print(f"No data found in the file {file_path}")
                                num_empty_data_files += 1
                            else:
                                if subfolder not in timeline_objects_by_year:
                                    timeline_objects_by_year[subfolder] = {filename.rstrip(".json"): maps_json}
                                else:
                                    timeline_objects_by_year[subfolder][filename.rstrip(".json")] = maps_json
                                # places_visited_by_month = analyze_file(maps_json, filename)
                                # places_visited_by_year = places_visited_by_year.union(places_visited_by_month)
                                # places_visited = places_visited.union(places_visited_by_month)
                        except json.JSONDecodeError:
                            print(f"Error parsing JSON in file: {file_path}")
                            num_empty_files += 1
        self.analyze_history(timeline_objects_by_year)
        self.stats['basic_stats']['num_empty_files'] = num_empty_files
        self.stats['basic_stats']['num_empty_data_files'] = num_empty_data_files
        
    
    def analyze_history(self, timeline_objects_by_year, **kwargs):
        """
        Collect the statistics of locations in the provided file

        Arguments:
            - `min_places_visited_per_month`: the minimum number of unique places visited per month
            - `min_month_history`: the minimum number of months in history
        """
        min_num_of_unique_places_visited_per_month = kwargs.get('min_places_visited_per_month', 20)
        min_num_of_months_history = kwargs.get("min_month_history", 12)
        self.stats['min_num_of_unique_places_visited_per_month'] = min_num_of_unique_places_visited_per_month
        self.stats['min_num_of_months_history'] = min_num_of_months_history

        num_of_years = 0
        num_of_months = 0

        months_too_few_places_visited = []
        unique_rate_by_month = {}
        num_of_unique_places_by_month = {}
        num_of_locations_in_CA = {}
        
    
        for year in timeline_objects_by_year:
            num_of_years += 1
            unique_places_visited_by_year = set()
            

            for month in timeline_objects_by_year[year]:
                num_of_locations_in_CA_by_month = 0
                total_num_places_visited = 0
                num_of_months += 1
                unique_places_visited_by_month = set()
                # print("year " + year + "month " + month)
                timeline_objects_by_month = timeline_objects_by_year[year][month]["timelineObjects"]
                for timeline_object in timeline_objects_by_month:
                    if "placeVisit" in timeline_object:
                        if "location" in timeline_object["placeVisit"]:
                            if "placeId" in timeline_object["placeVisit"]["location"]:
                                total_num_places_visited += 1
                                unique_places_visited_by_month.add(timeline_object["placeVisit"]["location"]["placeId"])
                                unique_places_visited_by_year.add(timeline_object["placeVisit"]["location"]["placeId"])
                            if "address" in timeline_object["placeVisit"]["location"]:
                                if re.search(r'\bCA\b', timeline_object["placeVisit"]["location"]["address"]):
                                    num_of_locations_in_CA_by_month += 1
                unique_rate_by_month[month] = "{:.3%}".format(len(unique_places_visited_by_month) / total_num_places_visited) + f"     {len(unique_places_visited_by_month)} out of {total_num_places_visited} places visited"

                num_of_unique_places_by_month[month] = len(unique_places_visited_by_month)

                if (len(unique_places_visited_by_month) < min_num_of_unique_places_visited_per_month):
                    months_too_few_places_visited.append(month)
                if num_of_locations_in_CA_by_month > 0:
                    num_of_locations_in_CA[month] = num_of_locations_in_CA_by_month
                
        self.stats['basic_stats']['num_of_years'] = num_of_years
        self.stats['basic_stats']['num_of_months'] = num_of_months
        self.stats['num_of_unique_places_visited_by_month'] = num_of_unique_places_by_month
        self.stats['months_too_few_places_visited'] = months_too_few_places_visited
        