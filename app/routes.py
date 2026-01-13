from flask import Blueprint, render_template, request, jsonify
from app.utils.mock_data import MockDataGenerator
from app.utils.gemini_client import GeminiClient
from app.utils.algorithm import EduRanker
import os
import concurrent.futures

main = Blueprint('main', __name__)

# Initialize components
mock_gen = MockDataGenerator()
# Ensure API Key is available
api_key = os.environ.get('GEMINI_API_KEY') or "AIzaSyDTrUUAk-mVC9DAcvhuSGb1_efgyPwoaiY"
gemini_client = GeminiClient(api_key)
ranker = EduRanker()

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/results')
def results():
    topic = request.args.get('topic', 'Python Programming')
    user_level_str = request.args.get('level', '3')
    try:
        user_level = int(user_level_str)
    except:
        user_level = 3

    # 1. Get Subject Decay Rate (Gemini)
    # Using 'get_subject_decay_rate' which returns (rate, category)
    decay_lambda, decay_category = gemini_client.get_subject_decay_rate(topic)

    # 2. Generate Mock Videos
    videos = mock_gen.generate_videos(topic, count=8)

    # 3. Process Videos (Calculate Scores)
    ranked_videos = []
    
    def process_video(video):
        # Specific Gemini Analysis per video
        try:
            # Difficulty
            diff_score = gemini_client.get_difficulty_score(video['title'], video['description'])
            video['difficulty'] = diff_score
            
            # Comment Quality
            c_score = gemini_client.analyze_comment_quality(video.get('comments', []))
            
            # Calculate ETAS
            score_data = ranker.calculate_etas(
                video, 
                decay_lambda, 
                decay_category, 
                c_score, 
                diff_score, 
                user_level
            )
            
            return {
                'video': video,
                'score': score_data
            }
        except Exception as e:
            # Simple handling to not crash entire loop
            print(f"Error processing video {video['id']}: {e}")
            return None

    # Use ThreadPoolExecutor for parallel API calls
    # Limiting workers to 4 to be safe with quota
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(process_video, videos))
        ranked_videos = [r for r in results if r is not None]

    # Sort by Total Score (Descending)
    ranked_videos.sort(key=lambda x: x['score']['total'], reverse=True)

    return render_template('results.html', 
                           ranked_videos=ranked_videos, 
                           topic=topic,
                           decoded_category=decay_category,
                           decay_info={'rate': decay_lambda, 'category': decay_category},
                           user_level=user_level)
