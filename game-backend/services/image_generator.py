import os
import base64
import requests
import random
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from config import get_theme

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define asset directories
assets_folder = 'services/assets'
generated_folder = os.path.join(assets_folder, "generated")

os.makedirs(generated_folder, exist_ok=True)

for folder in [assets_folder, generated_folder]:
    os.makedirs(folder, exist_ok=True)

class ImageGenerator:
    def __init__(self):
        self.stability_api_key = "stability-api-key"
        self.openai_api_key = "openai-api-key"

        self.difficulty_object_counts = {
            1: 2,  # Easy - 2 objects
            2: 3,  # Medium Easy - 3 objects
            3: 4,  # Medium - 4 objects
            4: 5,  # Medium Hard - 5 objects
            5: 6  # Hard - 6 objects
        }

        self.object_themes = get_theme()
        self.backgrounds = [
            "a clean colorful playroom floor",
            "a plain blue carpet",
            "a soft green grass area",
            "a wooden table with nothing else on it",
            "a sunny beach sand",
            "a playground surface",
            "a colorful patterned rug",
            "a school desk",
            "a picnic blanket",
            "a bedroom floor"
        ]

        self.fallback_enabled = True

    def get_objects_for_difficulty(self, difficulty):
        if difficulty <= 2:
            # Easy difficulty - mostly easy objects
            pool = self.object_themes["easy"] + random.sample(self.object_themes["medium"], 3)
        elif difficulty <= 4:
            # Medium difficulty - mix of easy and medium objects
            pool = random.sample(self.object_themes["easy"], 5) + self.object_themes["medium"]
        else:
            # Hard difficulty - mix of all difficulties with more hard objects
            pool = random.sample(self.object_themes["easy"], 3) + \
                   random.sample(self.object_themes["medium"], 5) + \
                   self.object_themes["hard"]

        # Ensure we have enough objects
        return random.sample(pool, min(len(pool), self.difficulty_object_counts[difficulty]))

    def generate_prompt(self, difficulty_level):
        theme = self.get_objects_for_difficulty(difficulty_level)
        background = random.choice(self.backgrounds)

        prompt = (
            f"A vibrant, colorful, clear and playful 3D cartoon-style illustration featuring {', '.join(theme)}. "
            f"The scene is bright, cheerful, and designed for kids aged 3-8, with soft edges, warm lighting, "
            f"and a joyful atmosphere. The background is {background}. "
            f"Make the objects easily recognizable, separated from each other, and visually distinct. "
            f"Each object should be clearly visible and not overlapping or merged with other objects. "
            f"Make sure complete objects are added without having parts of objects and the given objects "
            f"should be similar to real world objects rather than cartoon objects. "
            f"Don't add objects close to the edges and corners of the image. "
            f"The image should have high contrast between objects and background for easy identification."
        )

        return prompt, theme

    def save_image(self, image_data, filename):
        """Save a base64 image to the assets folder"""
        image_path = os.path.join(generated_folder, filename)
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image_data))
        return image_path

    def download_image(self, image_url, filename):
        """Download and save image from a URL"""
        image_path = os.path.join(generated_folder, filename)
        print(image_url)
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(image_path, "wb") as f:
                f.write(response.content)
            return image_path
        else:
            raise Exception(f"Failed to download image: {response.text}")

    def generate_with_stability_ai(self, difficulty_level):
        """Generate image using Stability AI API"""
        prompt, objects = self.generate_prompt(difficulty_level)

        try:
            response = requests.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.stability_api_key}"
                },
                json={
                    "text_prompts": [{"text": prompt, "weight": 1}],
                    "cfg_scale": 7,
                    "height": 896,
                    "width": 1152,
                    "samples": 1,
                    "steps": 30
                },
                timeout=30  # Set a timeout
            )

            if response.status_code == 200:
                data = response.json()
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"generated_stability_{timestamp}.png"
                image_path = self.save_image(data["artifacts"][0]["base64"], filename)
                return {"image_path": image_path, "objects": objects, "prompt": prompt}
            else:
                logger.error(f"Stability AI API error: {response.status_code} - {response.text}")
                raise Exception(f"Image generation failed: {response.text}")

        except Exception as e:
            logger.error(f"Error generating image with Stability AI: {str(e)}")
            if self.fallback_enabled:
                return self.generate_fallback_image(difficulty_level, objects, prompt)
            raise e

    def generate_with_openai(self, difficulty_level):
        """Generate image using OpenAI DALL-E API"""
        prompt, objects = self.generate_prompt(difficulty_level)

        try:
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.openai_api_key}"
                },
                json={
                    "prompt": prompt,
                    "n": 1,
                    "size": "1024x1024",
                    "response_format": "url"
                },
                timeout=30  # Set a timeout
            )

            if response.status_code == 200:
                data = response.json()
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"generated_openai_{timestamp}.png"
                image_path = self.download_image(data["data"][0]["url"], filename)

                return {"image_path": image_path, "image_url": data["data"][0]["url"], "objects": objects,
                        "prompt": prompt}
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                raise Exception(f"Image generation failed: {response.text}")

        except Exception as e:
            logger.error(f"Error generating image with OpenAI: {str(e)}")
            if self.fallback_enabled:
                return self.generate_fallback_image(difficulty_level, objects, prompt)
            raise e

    def generate_with_pollinations(self, difficulty_level):
        prompt, theme = self.generate_prompt(difficulty_level)
        width = 1024
        height = 1024
        seed = 42
        model = 'flux'

        image_url = f"https://pollinations.ai/p/{prompt}?width={width}&height={height}&seed={seed}&model={model}"

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"generated_pollinations_{timestamp}.png"
        image_path = self.download_image(image_url, filename)
        return {"image_path": image_path, "image_url": image_url, "theme": theme, "prompt": prompt}

    def generate_fallback_image(self, difficulty_level, objects=None, prompt=None):
        """Generate a fallback placeholder image when APIs fail"""
        logger.info("Using fallback image generation")

        if objects is None or prompt is None:
            prompt, objects = self.generate_prompt(difficulty_level)

        # Create a simple placeholder image
        width, height = 1024, 768
        image = Image.new('RGB', (width, height), color=(random.randint(200, 255),
                                                         random.randint(200, 255),
                                                         random.randint(200, 255)))
        draw = ImageDraw.Draw(image)

        try:
            # Try to use a TrueType font, fallback to default if not available
            font = ImageFont.truetype("arial.ttf", 32)
        except IOError:
            font = ImageFont.load_default()

        # Draw text listing the objects
        object_text = "Objects in this image:\n" + "\n".join(objects)
        draw.text((50, 50), object_text, fill=(0, 0, 0), font=font)

        # Draw shapes to represent objects
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255),
                  (255, 255, 0), (255, 0, 255), (0, 255, 255)]

        shapes = [
            lambda x, y, size, color: draw.rectangle([x, y, x + size, y + size], fill=color),
            lambda x, y, size, color: draw.ellipse([x, y, x + size, y + size], fill=color),
            lambda x, y, size, color: draw.polygon([(x, y + size), (x + size / 2, y), (x + size, y + size)], fill=color)
        ]

        for i, obj in enumerate(objects):
            # Calculate position based on object index
            x = 100 + (i % 3) * 300
            y = 200 + (i // 3) * 200
            size = 100
            color = colors[i % len(colors)]
            shape_func = shapes[i % len(shapes)]

            # Draw the shape
            shape_func(x, y, size, color)

            # Add object label
            draw.text((x, y + size + 10), obj, fill=(0, 0, 0), font=font)

        # Save the image
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"fallback_{timestamp}.png"
        image_path = os.path.join(generated_folder, filename)
        image.save(image_path)

        return {"image_path": image_path, "objects": objects, "prompt": prompt}

    def generate_image(self, difficulty_level, provider="stability"):
        logger.info(f"Generating image with difficulty level {difficulty_level} using {provider}")

        try:
            if provider == "stability":
                return self.generate_with_stability_ai(difficulty_level)
            elif provider == "openai":
                return self.generate_with_openai(difficulty_level)
            elif provider == "pollination":
                return self.generate_with_pollinations(difficulty_level)
            else:
                raise ValueError(f"Unknown provider: {provider}")
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            # Always return a fallback image if all else fails
            return self.generate_fallback_image(difficulty_level)
