import os
import shutil
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

if __name__ == "__main__":
    source_directory = sys.argv[1]
    target_directory = sys.argv[2]
    
    copy_files(source_directory, target_directory)

