import numpy as np
from datetime import datetime

class EduRanker:
    def __init__(self):
        self.epsilon = 1e-10
        self.view_norm = 100000
        
    def calculate_etas(self, video, decay_lambda, decay_category, comment_quality_score, difficulty_score, user_level_score):
        """
        Calculate ETAS score for a single video.
        
        Args:
            video (dict): Video object with stats
            decay_lambda (float): Subject-specific decay rate
            decay_category (str): FAST, MODERATE, etc.
            comment_quality_score (float): 0-10 from Gemini
            difficulty_score (int): 1-5 from Gemini
            user_level_score (int): 1-5 (User preference)
            
        Returns:
            dict: Score breakdown
        """
        # 1. Engagement (E)
        views = video.get('views', 0)
        likes = video.get('likes', 0)
        dislikes = video.get('dislikes', 0)
        
        # E = (2 * likes / (likes + dislikes + ε)) * tanh(views / VIEW_NORM) * 100
        like_ratio = likes / (likes + dislikes + self.epsilon)
        e_raw = (2 * like_ratio) * np.tanh(views / self.view_norm) * 100
        E = max(0, min(100, e_raw)) # Clamp 0-100

        # 2. Relevance Decay (R)
        # R = exp(-λ(topic) * t) * freshness_boost(t)
        if 'published_at' in video:
            published_at = datetime.fromisoformat(video['published_at'].replace('Z', ''))
        else:
            published_at = datetime.now()
            
        age_years = max(0, (datetime.now() - published_at).days / 365.0)
        
        # freshness_boost(t) = 1 + α * exp(-β * t)
        alpha = 0.2
        beta = 2.0
        freshness = 1 + alpha * np.exp(-beta * age_years)
        
        R_raw = np.exp(-decay_lambda * age_years) * freshness * 100
        R = max(0, min(100, R_raw))

        # 3. Comment Quality (C)
        # comment_quality_score is 0-10. Scale to 0-100.
        C = min(100, comment_quality_score * 10)

        # 4. Subject Complexity (S)
        # Simplified: heuristic bonus score (80-100)
        S = 90.0

        # 5. Difficulty Alignment (D)
        # D = 1 - |video_difficulty - user_level| / max_difficulty
        # diff_delta is difference (0 to 4)
        diff_delta = abs(difficulty_score - user_level_score)
        D_factor = 1 - (diff_delta / 5.0)
        D = D_factor * 100

        # Weights based on Subject Category
        # [E, R, C, S, D]
        if decay_category == 'FAST':
            # Fast moving topics need Recency (R)
            weights = [0.20, 0.35, 0.15, 0.10, 0.20]
        elif decay_category == 'SLOW':
            # Math/Physics need Clarity (C) and Complexity (S)
            weights = [0.15, 0.10, 0.30, 0.25, 0.20]
        elif decay_category == 'TIMELESS':
            # Philosophy needs Content (C) and Engagement (E) (discussion)
            weights = [0.25, 0.05, 0.35, 0.15, 0.20]
        else: # MODERATE
            weights = [0.20, 0.20, 0.20, 0.20, 0.20]

        w1, w2, w3, w4, w5 = weights

        # ETAS Calculation
        # Formula: 10 * (E^w1 * R^w2 * C^w3 * S^w4 * D^w5)
        # We scale inputs to 0-10 for the geometric mean to work nicely into 0-100 result
        def scale(x): return max(0.1, x / 10.0)
        
        etas_score = 10 * (
            (scale(E) ** w1) *
            (scale(R) ** w2) *
            (scale(C) ** w3) *
            (scale(S) ** w4) *
            (scale(D) ** w5)
        )
        
        return {
            'total': round(etas_score, 1),
            'E': round(E, 1),
            'R': round(R, 1),
            'C': round(C, 1),
            'S': round(S, 1),
            'D': round(D, 1),
            'weights': weights,
            'category': decay_category,
            'age_years': round(age_years, 1)
        }
