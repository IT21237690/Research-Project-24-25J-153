import customtkinter as ctk
from PIL import Image, ImageTk
import pandas as pd
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
from image_generator import ImageGenerator
from utils.feedback import generate_feedback
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random

class ImageGrammarApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("See & Describe!")
        self.geometry("1200x800")
        
        self.load_background()
        self.load_prompts()
        self.load_models()
        
        self.current_prompt = ""
        self.similarity_scores = []
        
        self.create_widgets()
        self.update_display()
    
    def load_background(self):
        bg_image_path = "D:/SLIIT/Year 04/Research/UI/background.jpg"
        bg_image = Image.open(bg_image_path)
        bg_image = bg_image.resize((1200, 800))
        self.bg_photo = ImageTk.PhotoImage(bg_image)
        
        self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    def load_prompts(self):
        csv_path = "D:\\SLIIT\\Year 04\\Research\\Datasets\\Dataset_Image_gen.csv"
        self.df = pd.read_csv(csv_path)
        self.prompts = self.df.iloc[:, 0].tolist()
    
    def load_models(self):
        from authtoken import auth_token
        self.image_gen = ImageGenerator(auth_token)
        
        try:
            self.grammar_tokenizer = T5Tokenizer.from_pretrained("models/grammar_model")
            self.grammar_model = T5ForConditionalGeneration.from_pretrained("models/grammar_model")
        except Exception as e:
            print(f"Error loading grammar model: {str(e)}")
            raise
    
    def create_widgets(self):
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.pack(side="left", padx=20, pady=20, fill="both", expand=True)

        self.start_btn = ctk.CTkButton(left_frame, text="Start", command=self.generate_next_image)
        self.start_btn.pack(pady=5)
        
        self.image_label = ctk.CTkLabel(left_frame, text="")
        self.image_label.pack(pady=10)
        
        self.prompt_label = ctk.CTkLabel(left_frame, text="", wraplength=600)
        self.prompt_label.pack(pady=10)
        
        self.next_btn = ctk.CTkButton(left_frame, text="Move to Next", command=self.generate_next_image)
        self.next_btn.pack(pady=5)
        
        self.end_btn = ctk.CTkButton(left_frame, text="End", command=self.display_final_score)
        self.end_btn.pack(pady=5)
        
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.pack(side="right", padx=20, pady=20, fill="both", expand=True)
        
        ctk.CTkLabel(right_frame, text="Describe the image!").pack(pady=5)
        
        self.desc_input = ctk.CTkTextbox(right_frame, width=400, height=150, fg_color="#345bde", bg_color="transparent", text_color="white")
        self.desc_input.pack(pady=10)
        
        self.check_btn = ctk.CTkButton(right_frame, text="Check Grammar", command=self.check_grammar)
        self.check_btn.pack(pady=5)
        
        self.similarity_btn = ctk.CTkButton(right_frame, text="Check Similarity", command=self.check_similarity)
        self.similarity_btn.pack(pady=5)
        
        self.feedback_label = ctk.CTkLabel(right_frame, text="", wraplength=380, justify="left", fg_color="transparent")
        self.feedback_label.pack(pady=10)
        
        self.status_label = ctk.CTkLabel(self, text="Ready", fg_color="#345bde")
        self.status_label.pack(side="bottom", pady=10)
    
    def update_display(self):
        if len(self.prompts) > 0:
            self.prompt_label.configure(text="")
    
    def generate_next_image(self):
        if len(self.prompts) == 0:
            self.status_label.configure(text="No more prompts!")
            return

        try:
            
            self.desc_input.delete("1.0", "end-1c")
            self.feedback_label.configure(text="")

            prompt = random.choice(self.prompts)
            self.current_prompt = prompt
            self.status_label.configure(text="Generating image...")
            self.update()
            
            image = self.image_gen.generate(prompt)
            image = image.resize((512, 512))
            tk_image = ImageTk.PhotoImage(image)
            self.image_label.configure(image=tk_image)
            self.image_label.image = tk_image
            
            self.update_display()
            self.status_label.configure(text="Image generated successfully!")
        
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}")
    
    def check_grammar(self):
        text = self.desc_input.get("1.0", "end-1c").strip()
        if not text:
            self.feedback_label.configure(text="Please enter a description first!")
            return
        
        try:
            inputs = self.grammar_tokenizer(f"grammar: {text}", return_tensors="pt", max_length=128, truncation=True)
            outputs = self.grammar_model.generate(**inputs)
            feedback, _ = generate_feedback(text, self.grammar_tokenizer, self.grammar_model)
            self.feedback_label.configure(text=feedback)
            self.status_label.configure(text="Grammar check completed!")
        except Exception as e:
            self.feedback_label.configure(text=f"Grammar check error: {str(e)}")
    
    def check_similarity(self):
        text = self.desc_input.get("1.0", "end-1c").strip()
        if not text:
            self.feedback_label.configure(text="Please enter a description first!")
            return
        
        try:
            prompt = self.current_prompt
            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform([prompt, text])
            similarity_score = cosine_similarity(vectors[0], vectors[1])[0][0]
            self.similarity_scores.append(similarity_score)
            feedback = f"Similarity Score: {similarity_score:.2f}\n\nOriginal: {prompt}\nYour Description: {text}"
            self.feedback_label.configure(text=feedback)
            self.status_label.configure(text="Similarity check completed!")
        except Exception as e:
            self.feedback_label.configure(text=f"Similarity check error: {str(e)}")
    
    def display_final_score(self):
        if self.similarity_scores:
            avg_score = sum(self.similarity_scores) / len(self.similarity_scores)
            feedback_text = f"Final Average Similarity Score: {avg_score:.2f}\n"

            if avg_score > 0.8:
                feedback_text += "Great job! Your description and grammar is highly accurate. Keep up the good work!"
            elif avg_score > 0.5:
                feedback_text += "Good effort! Try improving your grammar and object identification."
            else:
                feedback_text += "Needs improvement. Focus on spelling, punctuation, and describing objects clearly."
            
            self.feedback_label.configure(text=feedback_text)

        else:
            self.feedback_label.configure(text="No similarity scores to display.")

if __name__ == '__main__':
    ctk.set_appearance_mode("dark")
    app = ImageGrammarApp()
    app.mainloop()