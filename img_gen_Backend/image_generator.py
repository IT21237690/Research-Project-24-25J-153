from diffusers import StableDiffusionPipeline
import torch
from PIL import Image, ImageEnhance

class ImageGenerator:
    def __init__(self, auth_token):
        # Set device to CUDA (GPU) if available, otherwise use CPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Use float16 for GPU (CUDA), float32 for CPU
        dtype = torch.float16 if device == "cuda" else torch.float32  # Use float16 on GPU, float32 on CPU
        
        # Load the Stable Diffusion model with the appropriate dtype and device
        self.pipe = StableDiffusionPipeline.from_pretrained(
            "CompVis/stable-diffusion-v1-4",
            variant="fp16" if device == "cuda" else None,  # Use fp16 variant only for GPU
            torch_dtype=dtype,  # Use dtype based on device
            use_auth_token=auth_token,
            cache_dir="models/diffusion_cache"
        ).to(device)

    def generate(self, prompt):
        # Run the image generation process on either GPU or CPU
        with torch.autocast("cuda" if torch.cuda.is_available() else "cpu"):  # Ensure the right device is used
            # Generate the image based on the provided prompt
            generated_image = self.pipe(prompt, guidance_scale=1).images[0]
            
            # Enhance sharpness of the generated image
            enhancer = ImageEnhance.Sharpness(generated_image)
            enhanced_image = enhancer.enhance(0.5)  # Increase sharpness
            
            return enhanced_image

