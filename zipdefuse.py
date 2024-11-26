import pyzipper 
import os
import shutil
import sys

sys.setrecursionlimit(5000)

def extract_zip(zip_path, target_path):
    passwords = [f"{i:02}" for i in range(100)]
    
    with pyzipper.AESZipFile(zip_path, 'r') as zip_ref:
        for password in passwords:
            try:
                zip_ref.extractall(target_path, pwd=bytes(password, 'utf-8'))
                print(f"Extracted {zip_path} with password '{password}'")
                return target_path
            except (RuntimeError, pyzipper.BadZipFile):
                continue  # Try next password
        print(f"Failed to extract {zip_path}: No matching password found.")
    return None

def combine_text(folder_path):
    contents = b""
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                        contents += file_content
                        print(f"Read binary content from {file_path}")
                except Exception as e:
                    print(f"Skipping file {file_path} due to error: {e}")
                    continue
    return contents

def process(zip_path, output_content=b"", processed_paths=None, depth=0):
    if processed_paths is None:
        processed_paths = set()
        
    if zip_path in processed_paths:
        return output_content

    processed_paths.add(zip_path)
    temp_dir = f"temp_extracted_{depth}" 
    os.makedirs(temp_dir, exist_ok=True)

    # Extract ZIP file and get extracted path
    extracted_path = extract_zip(zip_path, temp_dir)
    if extracted_path:
        # Gather all text files' content from the current extracted ZIP directory
        output_content += combine_text(temp_dir)

        # Now, locate and process any nested ZIP files within this directory
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(".zip"):
                    nested_path = os.path.join(root, file)
                    print(f"Found nested zip file: {nested_path}")
                    output_content = process(
                        nested_path, output_content, processed_paths, depth + 1
                    )

    # Clean up extracted files immediately after processing to free up resources
    shutil.rmtree(temp_dir)
    return output_content

input_file = 'chall.zip'
text = process(input_file)

with open("flag.png", "wb") as output_file: 
    output_file.write(text)

print("Text extraction and concatenation complete.")
