from diffusers import StableDiffusionPipeline
import torch
from PIL import Image, ImageEnhance

class ImageGenerator:
    def __init__(self, auth_token):
        self.pipe = StableDiffusionPipeline.from_pretrained(
            "CompVis/stable-diffusion-v1-4",
            revision="fp16",
            torch_dtype=torch.float16,
            use_auth_token=auth_token,
            cache_dir="models/diffusion_cache"
        ).to("cuda" if torch.cuda.is_available() else "cpu")
        
    def generate(self, prompt):
        with torch.autocast("cuda" if torch.cuda.is_available() else "cpu"):
            # Generate the image
            generated_image = self.pipe(prompt, guidance_scale=1).images[0]
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(generated_image)
            enhanced_image = enhancer.enhance(0.0)  # Increase sharpness
            
            return enhanced_image