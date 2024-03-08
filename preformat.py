import os

planes_dir = "data/planes"

for root, dirs, files in os.walk(planes_dir):
    for filename in files:
        filepath = os.path.join(root, filename)
        new_filename = f"{filename[0]}.png"
        new_filepath = os.path.join(root, new_filename)
        os.rename(filepath, new_filepath)
        print(f"Renamed {filename} to {new_filename}")
