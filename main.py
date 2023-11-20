import os
import shutil
import sys
import re
from pathlib import Path
from typing import Set

# File extension categories
CATEGORIES = {
    "images": ['jpeg', 'png', 'jpg', 'svg'],
    "video": ['avi', 'mp4', 'mov', 'mkv'],
    "documents": ['doc', 'docx', 'txt', 'pdf', 'xlsx', 'pptx'],
    "music": ['mp3', 'ogg', 'wav', 'amr'],
    "archives": ['zip', 'gz', 'tar']
}

# Function to transliterate and normalize file names
CYRILLIC_SYMBOLS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяєії'
TRANSLATION = ('а', 'b', 'v', 'g', 'd', 'e', 'e', 'zh', 'z', 'i', 'y', 'k', 'l', 'm', 'n', 'o', 'p', 'r',
               's', 't', 'u', 'f', 'kh', 'ts', 'ch', 'sh', 'shch', '', 'y', '', 'e', 'yu', 'ya', 'ye', 'i', 'yi')

TRANS = {}

for cyr, lat in zip(CYRILLIC_SYMBOLS, TRANSLATION):

    TRANS[ord(cyr)] = lat
    TRANS[ord(cyr.upper())] = lat.upper()


def normalize(filename):
    normal_name = filename.translate(TRANS)
    normal_name = re.sub(r'\W', '_', normal_name)
    return normal_name


# Function to process folders
def process_folder(folder_path: str, base_path: str, known_extensions: Set[str], unknown_extensions: Set[str]):
    # Skip if the folder has been moved or deleted
    if not os.path.exists(folder_path):
        return

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            # Recursive call for subdirectories
            process_folder(item_path, base_path,
                           known_extensions, unknown_extensions)

            # Check again if the directory exists before trying to delete
            if os.path.exists(item_path) and not os.listdir(item_path):
                os.rmdir(item_path)

        else:
            _, ext = os.path.splitext(item)
            ext = ext.lower().lstrip('.')
            new_name = normalize(os.path.splitext(item)[0]) + '.' + ext
            category = next(
                (cat for cat, exts in CATEGORIES.items() if ext in exts), None)

            if category:
                known_extensions.add(ext)
                target_dir = os.path.join(base_path, category)
                os.makedirs(target_dir, exist_ok=True)
                shutil.move(item_path, os.path.join(target_dir, new_name))

                # Handle archives
                if category == "archives":
                    try:
                        shutil.unpack_archive(os.path.join(target_dir, new_name), os.path.join(
                            target_dir, new_name.split('.')[0]))
                    except shutil.ReadError:
                        print(
                            f"Warning: Unable to unpack archive {os.path.join(target_dir, new_name)}")

            else:
                unknown_extensions.add(ext)
                target_dir = os.path.join(base_path, "unknown")
                os.makedirs(target_dir, exist_ok=True)
                shutil.move(item_path, os.path.join(target_dir, new_name))
                print(
                    f"file {item_path} with an unknown extension was moved to the {target_dir}")


# Main function
def main(folder_path: str):
    folder = Path(folder_path)
    if not folder.is_dir():
        print("The provided path is not a valid directory.")
        sys.exit(1)

    known_extensions = set()
    unknown_extensions = set()
    process_folder(folder_path, folder_path,
                   known_extensions, unknown_extensions)

    # Printing reports
    print("Known extensions:", known_extensions)
    print("Unknown extensions:", unknown_extensions)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python sort.py <path_to_folder>")
        sys.exit(1)

    main(sys.argv[1])
