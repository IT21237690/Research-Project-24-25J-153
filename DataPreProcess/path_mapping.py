# import os
# import pandas as pd

# # Define the base directory
# base_audio_dir = "../dataset/audio"
# base_transcription_dir = "../dataset/transcriptions"

# # List to hold file pairs
# data = []

# # Walk through the directories to find .wav and .txt files
# for root, _, files in os.walk(base_audio_dir):
#     for file in files:
#         if file.endswith(".wav"):
#             audio_path = os.path.join(root, file)
#             transcription_path = audio_path.replace(base_audio_dir, base_transcription_dir).replace(".wav", ".txt")
#             if os.path.exists(transcription_path):
#                 data.append({"audio": audio_path, "transcription": transcription_path})

# # Create a DataFrame
# df = pd.DataFrame(data)

# # Save the DataFrame as a CSV
# df.to_csv("../dataset/path_file.csv", index=False)


# .json output path map
import os
import pandas as pd

# Define the base directories
base_audio_dir = "/home/bhagya/Documents/Research/pp1/dataset/audio"
base_transcription_dir = "/home/bhagya/Documents/Research/pp1/dataset/transcriptions"

# List to hold file pairs
data = []

# Walk through the directories to find .wav and .txt files
for root, _, files in os.walk(base_audio_dir):
    for file in files:
        if file.endswith(".wav"):
            audio_path = os.path.join(root, file)
            transcription_path = audio_path.replace(base_audio_dir, base_transcription_dir).replace(".wav", ".txt")
            if os.path.exists(transcription_path):
                data.append({"audio": audio_path, "transcription": transcription_path})

# Create a DataFrame
df = pd.DataFrame(data)

# Save the DataFrame as a JSON
df.to_json("/home/bhagya/Documents/Research/pp1/dataset/path_file.json", orient="records", lines=False, indent=4)

print("JSON file created successfully!")
