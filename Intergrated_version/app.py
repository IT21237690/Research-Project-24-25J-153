import customtkinter as ctk
from PIL import Image, ImageTk
import pandas as pd
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
from image_generator import ImageGenerator
import random  # Added random module for random selection
from utils.feedback import generate_feedback
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ImageGrammarApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("See & Describe!")
        self.geometry("1200x800")

        # Load background image
        self.load_background()

        # Initialize components
        self.load_prompts()
        self.load_models()
        self.current_prompt_index = 0

        # Create UI
        self.create_widgets()
        self.update_display()

    def load_background(self):
        """Set a background image"""
        bg_image_path = "D:/SLIIT/Year 04/Research/UI/background.jpg"  # Change to your image path
        bg_image = Image.open(bg_image_path)
        bg_image = bg_image.resize((1200, 800))  # Resize if needed
        self.bg_photo = ImageTk.PhotoImage(bg_image)

        self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Cover entire window        

    def load_prompts(self):
        """Load image prompts from CSV"""
        csv_path = "D:\\SLIIT\\Year 04\\Research\\Datasets\\Dataset_Image_gen.csv"
        self.df = pd.read_csv(csv_path)
        self.prompts = self.df.iloc[:, 0].tolist()

    def load_models(self):
        """Load both image and grammar models"""
        from authtoken import auth_token

        # Image generator
        self.image_gen = ImageGenerator(auth_token)

        # Grammar checker
        print("Loading grammar model...")
        try:
            self.grammar_tokenizer = T5Tokenizer.from_pretrained("models/grammar_model")
            print("Tokenizer loaded successfully!")
            
            self.grammar_model = T5ForConditionalGeneration.from_pretrained("models/grammar_model")
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading grammar model: {str(e)}")
            raise  # Stop execution if the model fails to load

    def create_widgets(self):
        """Create GUI components"""

        # Left panel - Image generation
        left_frame = ctk.CTkFrame(self, fg_color="transparent")  # Transparent Frame
        left_frame.pack(side="left", padx=20, pady=20, fill="both", expand=True)

        self.image_label = ctk.CTkLabel(left_frame, text="")
        self.image_label.pack(pady=10)

        self.prompt_label = ctk.CTkLabel(left_frame, text="", wraplength=600)
        self.prompt_label.pack(pady=10)

        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")  # Transparent Button Frame
        btn_frame.pack(pady=10)

        self.next_btn = ctk.CTkButton(btn_frame, text="Let's Go to the Next!", command=self.generate_next_image)
        self.next_btn.pack(side="left", padx=5)

        # self.auto_btn = ctk.CTkButton(btn_frame, text="Auto Generate All", command=self.auto_generate_all)
        # self.auto_btn.pack(side="left", padx=5)

        # Right panel - User interaction
        right_frame = ctk.CTkFrame(self, fg_color="transparent")  # Transparent Frame
        right_frame.pack(side="right", padx=20, pady=20, fill="both", expand=True)

         # Description input
        ctk.CTkLabel(right_frame, text="Describe the image!").pack(pady=5)

        self.desc_input = ctk.CTkTextbox(
        right_frame,
        width=400,
        height=150,
        fg_color="#345bde",  # Light Blue (Hex Code)
        bg_color="transparent",  # Keep transparent background
        text_color="white"  # Optional: Change text color for visibility
        )
        self.desc_input.pack(pady=10)

        # Buttons
        self.check_btn = ctk.CTkButton(right_frame, text="Check Grammar", command=self.check_grammar)
        self.check_btn.pack(pady=5)

        self.similarity_btn = ctk.CTkButton(right_frame, text="Check Similarity", command=self.check_similarity)
        self.similarity_btn.pack(pady=5)

        # Feedback display
        self.feedback_label = ctk.CTkLabel(right_frame, text="", wraplength=380, justify="left", fg_color="transparent")
        self.feedback_label.pack(pady=10)

        # Status bar
        self.status_label = ctk.CTkLabel(self, text="Ready", fg_color="transparent")
        self.status_label.pack(side="bottom", pady=10)

    def update_display(self):
        """Update current prompt display"""
        if self.current_prompt_index < len(self.prompts):
            self.prompt_label.configure(text="")

    def generate_next_image(self):
        """Generate and display next image from CSV"""
        if self.current_prompt_index >= len(self.prompts):
            self.status_label.configure(text="All images generated!")
            return

        try:
            prompt = self.prompts[self.current_prompt_index]
            self.status_label.configure(text="Generating image...")
            self.update()

            # Generate and display image
            image = self.image_gen.generate(prompt)
            image = image.resize((512, 512))
            tk_image = ImageTk.PhotoImage(image)
            self.image_label.configure(image=tk_image)
            self.image_label.image = tk_image

            # Save image
            image.save(f"generated_image_{self.current_prompt_index}.png")
            self.current_prompt_index += 1
            self.update_display()
            self.status_label.configure(text="Image generated successfully!")

        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}")

    def auto_generate_all(self):
        """Generate all images automatically"""
        self.current_prompt_index = 0
        while self.current_prompt_index < len(self.prompts):
            self.generate_next_image()

    def check_grammar(self):
        """Check grammar of user description"""
        text = self.desc_input.get("1.0", "end-1c").strip()  # Strip to remove any extra spaces or newlines
        print(f"Retrieved text: '{text}'")  # Debugging
        print(f"Text length: {len(text)}")

        if not text:
            self.feedback_label.configure(text="Please enter a description first!")
            return

        try:
            # Grammar correction using your trained model
            inputs = self.grammar_tokenizer(
                f"grammar: {text}",
                return_tensors="pt",
                max_length=128,
                truncation=True
            )
            outputs = self.grammar_model.generate(**inputs)
            corrected = self.grammar_tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Generate detailed feedback
            feedback, _ = generate_feedback(text, self.grammar_tokenizer, self.grammar_model)
            print(f"Feedback output: {feedback}")  # Debugging
            self.feedback_label.configure(text=feedback)
            self.status_label.configure(text="Grammar check completed!")

        except Exception as e:
            print(f"Error in check_grammar: {str(e)}")
            self.feedback_label.configure(text=f"Grammar check error: {str(e)}")

    def check_similarity(self):
        """Check similarity between user input and original prompt"""
        text = self.desc_input.get("1.0", "end-1c").strip()
        print(f"Retrieved text for similarity: '{text}'")  # Debugging
        if not text:
            self.feedback_label.configure(text="Please enter a description first!")
            return

        try:
            prompt = self.prompts[self.current_prompt_index - 1]
            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform([prompt, text])
            similarity_score = cosine_similarity(vectors[0], vectors[1])[0][0]

            feedback = f"Similarity Score: {similarity_score:.2f}\n\n"
            feedback += f"Original Description of the image: {prompt}\n"
            feedback += f"Your Description: {text}"

            self.feedback_label.configure(text=feedback)
            self.status_label.configure(text="Similarity check completed!")

        except Exception as e:
            print(f"Error in check_similarity: {str(e)}")
            self.feedback_label.configure(text=f"Similarity check error: {str(e)}")

if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    app = ImageGrammarApp()
    app.mainloop()