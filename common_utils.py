from datetime import datetime
import json
import os
import shutil
from PIL import Image
import sys

def copy_files(source_dir, target_dir):
    """
    Copy all files from source_dir and its subdirectories to target_dir.

    Parameters:
        source_dir (str): The root directory to search for files.
        target_dir (str): The directory where all files will be copied.
    """
    os.makedirs(target_dir, exist_ok=True)  # Ensure the target directory exists
    
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            # Construct full file path
            file_path = os.path.join(root, file)
            # Construct target file path
            target_file_path = os.path.join(target_dir, file)
            
            # Avoid overwriting existing files in target_dir by appending a number to the filename
            counter = 1
            original_target_file_path = target_file_path
            while os.path.exists(target_file_path):
                base, extension = os.path.splitext(original_target_file_path)
                target_file_path = f"{base}_{counter}{extension}"
                counter += 1
            
            # Copy the file
            shutil.copy2(file_path, target_file_path)
            # print(f"Copied '{file_path}' to '{target_file_path}'")

def convert_to_timestamp(time_str: str):
    """
    Return a POSIX timestamp 

    Parameters:
    - `time_str` (str): a string representing a datetime following the following formats:
        - "%Y-%m-%dT%H:%M:%S.%fZ"
        - "%Y-%m-%dT%H:%M:%SZ"
        - "%Y:%m:%d %H:%M:%S"
        - "%Y%m%dT%H%M%S.%fZ"
    """
    date_formats = ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ",
                    "%Y:%m:%d %H:%M:%S", "%Y%m%dT%H%M%S.%fZ"]
    datetime_obj = None
    for date_format in date_formats:
        try:
            datetime_obj = datetime.strptime(time_str, date_format)
            break
        except ValueError:
            continue
    if datetime is None:
        print("The input Datetime format is not recognized")
    else:
        if datetime_obj is None:
            print(time_str)
        return datetime_obj.timestamp()


def load_timeline(input_file_path):
    """
    Returns the timeline

    Parameters:
        - `input_file_path` (str): path to the input file

    Returns: a dictionary representing the timeline
    """
    with open(input_file_path, 'r') as json_file:
        try:
            maps_json = json.load(json_file)
        except json.JSONDecodeError:
            print(f"Error parsing JSON in file: {input_file_path}")
    return maps_json


def find_subfolders(input_dir_path):
    """
    Returns a list of all subfolders under the input directory

    Parameters:
        - `input_dir_path` (str): the path to the input directory

    Returns: a list of all subfolders under the input directory
    """
    subfolders = [f for f in os.listdir(
        input_dir_path) if os.path.isdir(os.path.join(input_dir_path, f))]
    return subfolders

def ask_true_false(prompt_msg: str):
    while True:
        response = input(prompt_msg + " (true/false) ").lower()
        if response == 'true':
            return True
        elif response == 'false':
            return False
        else:
            print("Invalid input. Please enter 'true' or 'false'.")

def resize_image(img, output_path, max_width, max_height):
    width, height = img.size

    # Calculate the aspect ratio
    aspect_ratio = width / height

    # Calculate new width and height based on the aspect ratio
    if width > max_width or height > max_height:
        if width / max_width > height / max_height:
            new_width = max_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = max_height
            new_width = int(new_height * aspect_ratio)
    else:
        new_width = width
        new_height = height

    # Resize the image
    resized_img = img.resize((new_width, new_height))
    # Save the resized image
    resized_img.save(output_path)

# def resize_image(input_path, output_path, max_width, max_height):
#     """
#     Resize an image file to fit within a maximum width and height, preserving the aspect ratio.

#     Args:
#         input_path (str): Path to the input image file.
#         output_path (str): Path to save the resized image.
#         max_width (int): Maximum width of the resized image.
#         max_height (int): Maximum height of the resized image.
#     """
#     # Open the image file
#     with Image.open(input_path) as img:
#         # Get the current width and height
#         width, height = img.size

#         # Calculate the aspect ratio
#         aspect_ratio = width / height

#         # Calculate new width and height based on the aspect ratio
#         if width > max_width or height > max_height:
#             if width / max_width > height / max_height:
#                 new_width = max_width
#                 new_height = int(new_width / aspect_ratio)
#             else:
#                 new_height = max_height
#                 new_width = int(new_height * aspect_ratio)
#         else:
#             new_width = width
#             new_height = height

#         # Resize the image
#         resized_img = img.resize((new_width, new_height))
#         # Save the resized image
#         resized_img.save(output_path)

def resize_images_in_folder(input_folder, output_folder, max_width, max_height):
    """
    Resize all images in a folder to fit within a maximum width and height, preserving the aspect ratio.

    Args:
        input_folder (str): Path to the input folder containing images.
        output_folder (str): Path to save the resized images.
        max_width (int): Maximum width of the resized images.
        max_height (int): Maximum height of the resized images.
    """
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop through each file in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.jpg'):
            input_path = os.path.join(input_folder, file_name)
            output_path = os.path.join(output_folder, file_name)
            # Resize the image and save it to the output folder
            resize_image(input_path, output_path, max_width, max_height)


if __name__ == "__main__":
    input_folder = "./data/anonymized_stories/participant1"
    output_folder = "./data/anonymized_stories/participant11"
    resize_images_in_folder(input_folder, output_folder, 400, 300)