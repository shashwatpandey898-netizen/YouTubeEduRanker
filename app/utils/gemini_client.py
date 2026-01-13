import google.generativeai as genai
import os
import time
import re

class GeminiClient:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("Gemini API Key is required")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.cache = {}

    def get_subject_decay_rate(self, topic):
        """
        Use Gemini to classify topic into decay category
        Returns lambda value and the category name.
        """
        cache_key = f"decay_{topic}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        prompt = f"""
        Analyze this educational topic: "{topic}"
        
        Classify decay rate (choose ONE):
        1. FAST (e.g. AI, Crypto, Web Frameworks)
        2. MODERATE (e.g. Programming, Data Science)
        3. SLOW (e.g. Math, Physics, Classics)
        4. TIMELESS (e.g. Philosophy, Study Methods)
        
        Return ONLY one word: FAST, MODERATE, SLOW, or TIMELESS.
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text.strip().upper()
            
            decay_map = {
                'FAST': 0.693,
                'MODERATE': 0.347,
                'SLOW': 0.139,
                'TIMELESS': 0.035
            }
            
            # Default fallback
            rate = 0.347 
            category = "MODERATE"

            # Extract keyword if extra text exists
            found = False
            for key in decay_map:
                if key in result:
                    rate = decay_map[key]
                    category = key
                    found = True
                    break
            
            self.cache[cache_key] = (rate, category)
            return rate, category
            
        except Exception as e:
            print(f"Gemini API Error (Decay): {e}")
            return 0.347, "MODERATE" # Fallback

    def analyze_comment_quality(self, comments):
        """
        Analyze educational value of comments.
        Returns a score 0-10.
        """
        if not comments:
            return 5.0
            
        comments_str = "\n".join([f"- {c}" for c in comments])
        prompt = f"""
        Analyze these YouTube comments for educational value (clarity, corrections, additional info):
        {comments_str}
        
        Rate the overall educational quality of discussion on a scale of 0 to 10.
        Return ONLY the number.
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            # extract number
            match = re.search(r"(\d+(\.\d+)?)", text)
            if match:
                return float(match.group(1))
            return 5.0
        except Exception as e:
            print(f"Gemini API Error (Comments): {e}")
            return 5.0

    def get_difficulty_score(self, title, description):
        """
        Rate video difficulty 1-5.
        """
        prompt = f"""
        Rate the difficulty level of this video content on a scale of 1 (Beginner) to 5 (Advanced).
        Title: {title}
        Description: {description}
        
        Return ONLY the number (1-5).
        """
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            match = re.search(r"(\d+)", text)
            if match:
                val = int(match.group(1))
                return max(1, min(5, val))
            return 3
        except Exception:
            return 3
