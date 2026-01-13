import random
from datetime import datetime, timedelta

class MockDataGenerator:
    def __init__(self):
        self.channels = ["CodeMaster", "MathWizard", "AI Explained", "ThinkDeep", "ScienceNerd", "HistoryBuff", "PhilosoFile"]
        self.topics_cache = {}

    def generate_videos(self, topic, count=10):
        """Generate mock video data for testing"""
        videos = []
        for i in range(count):
            video_id = f'mock_video_{i}'
            published = self._random_date()
            views, likes, dislikes = self._generate_engagement(topic, published)
            
            video = {
                'id': video_id,
                'title': f'Learn {topic} - Part {i+1} [Full Course]',
                'description': f'A comprehensive tutorial on {topic} for all levels. We cover basic concepts to advanced theory.',
                'channel': random.choice(self.channels),
                'published_at': published.isoformat(),
                'year': published.year,
                'views': views,
                'likes': likes,
                'dislikes': dislikes,
                'comment_count': random.randint(5, 200),
                'duration': f"{random.randint(5, 120)}:00",
                'comments': self.generate_mock_comments(topic)
            }
            videos.append(video)
        return videos

    def _random_date(self):
        start = datetime(2018, 1, 1)
        end = datetime(2024, 1, 1)
        return start + timedelta(days=random.randint(0, (end - start).days))

    def _generate_engagement(self, topic, published_date):
        # Older videos might have more views, but random factor applies
        age_days = (datetime.now() - published_date).days
        # ensure age_days is at least 1 to avoid weird math if just published
        age_days = max(1, age_days)
        
        base_views = random.randint(1000, 500000)
        views = base_views + (age_days * random.randint(10, 100))
        
        # Like ratio 1-10%
        likes = int(views * random.uniform(0.01, 0.1))
        # Dislike ratio 1-5% of likes
        dislikes = int(likes * random.uniform(0.01, 0.05))
        
        return views, likes, dislikes

    def generate_mock_comments(self, topic, count=5):
        base_comments = [
            f"Great explanation of {topic}, really helped me understand!",
            f"The instructor could have gone slower in section 3",
            f"Correction: The formula at 5:30 should be slightly different.",
            f"Anyone have additional resources on this topic?",
            f"This video assumes you already know the basics.",
            "Amazing quality, subscribed!",
            "I am confused about the last part.",
            "Best tutorial on YouTube for this.",
            "Audio quality is a bit low.",
            f"Thanks for covering {topic}!"
        ]
        return random.sample(base_comments, min(count, len(base_comments)))
