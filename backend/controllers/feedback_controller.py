import os
import re
from flask import Blueprint, request, jsonify
from config.database import get_db
# ML-based sentiment service (must be available)
try:
    from services.sentiment_service import predict as ml_predict
except Exception:
    ml_predict = None

feedback_controller = Blueprint('feedback_controller', __name__)

# Note: rule-based fallback removed — system uses fine-tuned ML model for sentiment

@feedback_controller.route('/sentiment-stats', methods=['GET'])
def get_sentiment_stats():
    try:
        db = get_db()
        
        # Aggregate sentiment labels
        pipeline = [
            {"$group": {"_id": "$sentiment_label", "count": {"$sum": 1}}}
        ]
        
        results = list(db.sentiment_analysis.aggregate(pipeline))
        
        stats = {
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "total": 0
        }
        
        for r in results:
            label = r["_id"]
            if label in stats:
                stats[label] = r["count"]
            stats["total"] += r["count"]
            
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch stats", "details": str(e)}), 500

@feedback_controller.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Validate that all required fields are present and contain only letters and spaces
    fields = ["logoQuality", "videoQuality", "generationTime", "scheduling", "comments"]
    for field in fields:
        val = data.get(field)
        if not isinstance(val, str) or not re.match(r"^[a-zA-Z\s]+$", val):
            return jsonify({"error": f"Invalid input for field '{field}'. All answers must be text containing letters and spaces only."}), 400

    comments = data.get('comments', '')
    # Use ML-based sentiment only; return 503 if model unavailable
    if ml_predict is None:
        return jsonify({"error": "Sentiment model not available"}), 503
    try:
        sentiment, score = ml_predict(comments)
    except Exception as e:
        return jsonify({"error": "Sentiment analysis failed", "details": str(e)}), 500

    db = get_db()
    
    # 1. Insert into feedbacks collection
    feedback_doc = {
        "logoQuality": data.get("logoQuality"),
        "videoQuality": data.get("videoQuality"),
        "generationTime": data.get("generationTime"),
        "scheduling": data.get("scheduling"),
        "comments": comments
    }
    
    try:
        feedback_result = db.feedbacks.insert_one(feedback_doc)
        
        # 2. Insert into sentiment_analysis collection with a reference to the feedback
        sentiment_doc = {
            "feedback_id": feedback_result.inserted_id,
            "comments": comments,
            "sentiment_label": sentiment,
            "sentiment_score": score
        }
        db.sentiment_analysis.insert_one(sentiment_doc)
        
    except Exception as e:
        return jsonify({"error": "Failed to save feedback to database", "details": str(e)}), 500
    
    return jsonify({
        "message": "Feedback submitted successfully!",
        "sentiment": sentiment,
        "score": score,
        "data": data
    }), 200

@feedback_controller.route('/feedbacks', methods=['GET'])
def get_feedbacks():
    try:
        db = get_db()
        feedbacks = list(db.feedbacks.find({}))
        
        # Fetch all sentiment records to create a mapping: feedback_id -> sentiment
        sentiments = list(db.sentiment_analysis.find({}))
        sentiment_map = {}
        for s in sentiments:
            fb_id = str(s.get("feedback_id"))
            sentiment_map[fb_id] = {
                "sentiment_label": s.get("sentiment_label"),
                "sentiment_score": s.get("sentiment_score")
            }
            
        formatted = []
        for fb in feedbacks:
            fb_id_str = str(fb["_id"])
            s_data = sentiment_map.get(fb_id_str, {"sentiment_label": "neutral", "sentiment_score": 0.0})
            
            formatted.append({
                "id": fb_id_str,
                "logoQuality": fb.get("logoQuality"),
                "videoQuality": fb.get("videoQuality"),
                "generationTime": fb.get("generationTime"),
                "scheduling": fb.get("scheduling"),
                "comments": fb.get("comments", ""),
                "sentiment": s_data["sentiment_label"],
                "score": s_data["sentiment_score"]
            })
            
        # Return newest feedbacks first
        formatted.reverse()
        return jsonify(formatted), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch feedbacks", "details": str(e)}), 500