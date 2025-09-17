import os
import pandas as pd
from flask import Flask, jsonify, render_template
from loguru import logger
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)
analyzer = SentimentIntensityAnalyzer()

DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

@app.route('/')
def index():
    available_videos = [f.replace('.csv', '') for f in os.listdir(DATA_FOLDER) if f.endswith('.csv')]
    return render_template('index.html', videos=available_videos)

@app.route('/api/data/<video_id>')
def get_data(video_id):
    file_path = os.path.join(DATA_FOLDER, f"{video_id}.csv")
    
    if not os.path.exists(file_path):
        return jsonify({"error": "Data untuk video ini tidak ditemukan."}), 404

    try:
        df = pd.read_csv(file_path)

        # REVISI: Membersihkan nilai NaN di kolom-kolom penting
        # Ganti NaN di kolom teks dengan string kosong
        df['comment_text'] = df['comment_text'].fillna('')
        # Ganti NaN di kolom angka dengan 0
        df['like_count'] = df['like_count'].fillna(0)

        # --- Analisis Sentimen ---
        sentiments = {'positif': 0, 'negatif': 0, 'netral': 0}
        main_comments = df[df['parent_comment_id'].isna()]['comment_text'].dropna()
        for comment in main_comments:
            score = analyzer.polarity_scores(comment)
            if score['compound'] >= 0.05: sentiments['positif'] += 1
            elif score['compound'] <= -0.05: sentiments['negatif'] += 1
            else: sentiments['netral'] += 1

        # --- Kalkulasi Statistik ---
        total_comments = len(main_comments)
        total_replies = len(df[df['parent_comment_id'].notna()])
        total_likes = df['like_count'].sum()
        
        # Top 5 komentator
        top_commenters = df[df['parent_comment_id'].isna()]['username'].value_counts().nlargest(5).reset_index().to_dict('records')
        
        # Top 5 komentar dengan like terbanyak
        top_comments_by_like = df.nlargest(5, 'like_count')[['username', 'comment_text', 'like_count']].to_dict('records')
        
        # Analisis waktu komentar
        df['create_time'] = pd.to_datetime(df['create_time'])
        comments_per_hour = df.groupby(df['create_time'].dt.hour).size().reset_index(name='count').to_dict('records')

        analysis_data = {
            "stats": {
                "total_comments": int(total_comments),
                "total_replies": int(total_replies),
                "total_likes": int(total_likes)
            },
            "sentiment_analysis": sentiments,
            "top_commenters": top_commenters,
            "top_comments_by_like": top_comments_by_like,
            "comments_per_hour": comments_per_hour
        }
        
        return jsonify(analysis_data)

    except Exception as e:
        logger.error(f"Gagal memproses file {file_path}: {e}")
        return jsonify({"error": "Terjadi kesalahan saat memproses data."}), 500

if __name__ == '__main__':
    app.run(debug=True)