import os
import sys
import json
import requests
import shutil
from PIL import Image
from novita_client import NovitaClient
from novita_client.utils import base64_to_image, image_to_base64
from config import *
from common_utils import *

client = NovitaClient(TEXT_REMOVAL_API_KEY)

def save_image_from_url(url, save_path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            # print("Image saved successfully.")
        else:
            print("Failed to download image: HTTP status code",
                  response.status_code)
    except Exception as e:
        print("An error occurred:", e)

def copy_image(source_path, destination_path):
    try:
        # Copy the file from source_path to destination_path
        shutil.copyfile(source_path, destination_path)
        # print("Image copied successfully.")
    except Exception as e:
        print("An error occurred:", e)

def make_blur_request(image_path, filename):
    url = 'https://www.ailabapi.com/api/portrait/effects/blurred-faces'
    headers = {'ailabapi-api-key': BLUR_FACE_API_KEY}
    payload={}
    files = [
        ('image', (filename, open(image_path, 'rb'), 'application/octet-stream'))
    ]
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    # print(response.text)
    # print(response.content)
    response_json = json.loads(response.text)
    if response_json["error_detail"]["status_code"] == 200:
        return response_json['data']['image_url']
    else:
        return "422"
    
def remove_text(input_dir, output_dir):
    """
    Make API calls to NovitaAI to remove texts from images
    """
    if os.path.exists(input_dir) == False:
        print("Invalid path: " + str(input_dir))
    if os.path.exists(output_dir) == False:
        print("Invalid path: " + str(output_dir))
    os.makedirs(output_dir, exist_ok = True)

    subfolders = [f for f in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, f))]
    for subfolder in subfolders:
        subfolder_path = os.path.join(input_dir, subfolder)
        for filename in os.listdir(subfolder_path):
            if filename.endswith('.jpg'):
                img_path = os.path.join(subfolder_path, filename)
                with open(img_path, "rb") as image_file:
                    img = Image.open(image_file)
                    img.thumbnail((1024, 1024))
                    # to be modified
                    # output_folder = os.path.join(output_dir, subfolder)
                    # os.makedirs(output_folder, exist_ok=True)
                    # output_dir_path = os.path.join(output_folder, filename)
                    output_dir_path = os.path.join(output_dir, filename)
                    img.save(output_dir_path)

                with open(output_dir_path, "rb") as image:
                    img = Image.open(image)
                    res = client.remove_text(image_to_base64(img))
                    resize_image(base64_to_image(res.image_file), output_dir_path, 400, 300)
        shutil.rmtree(subfolder_path)

def blur_face_in_image(input_file_path, output_file_path):
    image_url = make_blur_request(input_file_path)
    if image_url != "422":
        save_image_from_url(image_url, output_file_path)
    else:
        copy_image(input_file_path, output_file_path)

def blur_face(input_dir, output_dir):
    if os.path.exists(input_dir) == False:
        print("Invalid path: " + str(input_dir))
    
    os.makedirs(output_dir, exist_ok=True)
    subfolders = [f for f in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, f))]
    for subfolder in subfolders:
        subfolder_path = os.path.join(input_dir, subfolder)
        output_file_dir = os.path.join(output_dir, subfolder)
        os.makedirs(output_file_dir, exist_ok=True)
        for filename in os.listdir(subfolder_path):
            image_url = make_blur_request(os.path.join(subfolder_path, filename), filename)
            output_file_path= os.path.join(output_file_dir, filename)
            if image_url != "422":
                save_image_from_url(image_url, output_file_path)
            else:
                copy_image(os.path.join(subfolder_path, filename), output_file_path)
    
    return output_dir

if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    blurred_output_dir = blur_face(input_dir, output_dir)
    remove_text(blurred_output_dir, output_dir)

            