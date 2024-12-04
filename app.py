import tkinter as tk
import customtkinter as ctk
from PIL import ImageTk
from authtoken import auth_token

import pandas as pd  # For reading the CSV
import torch
from torch import autocast
from diffusers import StableDiffusionPipeline

# Load the dataset
csv_file = "D:\SLIIT\Year 04\Research\Datasets\Dataset_Image_gen.csv"  # Replace with the actual path to your CSV file
data = pd.read_csv(csv_file)  # Load the CSV file
prompts = data.iloc[:, 0].tolist()  # Get all prompts from the first column

# Create the app GUI
app = tk.Tk()
app.geometry("532x632")
app.title("Text_to_Image_Generator")
ctk.set_appearance_mode("dark")

# GUI widgets
lmain = ctk.CTkLabel(app, height=512, width=512)
lmain.place(x=10, y=110)

# Model setup
modelid = "CompVis/stable-diffusion-v1-4"
device = "cuda"
pipe = StableDiffusionPipeline.from_pretrained(
    modelid, revision="fp16", torch_dtype=torch.float16, use_auth_token=auth_token
)
pipe.to(device)

# Index to keep track of current prompt
prompt_index = 0


def generate_from_dataset():
    global prompt_index  # To keep track of the current prompt
    
    if prompt_index < len(prompts):  # To ensure no to go out of bounds
        current_prompt = prompts[prompt_index]  # Fetch the next prompt
        with autocast(device):
            image = pipe(current_prompt, guidance_scale=8.5)["images"][0]
        image.save(f'generatedimage_{prompt_index}.png')  # Save with a unique name
        img = ImageTk.PhotoImage(image)
        lmain.configure(image=img)
        
        prompt_index += 1  # Move to the next prompt
    else:
        print("All prompts have been Added! Starting from the begining!")


# Button to trigger the generation
generate_button = ctk.CTkButton(
    app, height=40, width=200, text="Generate Next Image",
    font=("Arial", 20), text_color="white", fg_color="blue",
    command=generate_from_dataset
)
generate_button.place(x=166, y=60)

app.mainloop()
