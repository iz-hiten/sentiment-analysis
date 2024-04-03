# -*- coding: utf-8 -*-
"""sentiment analyser.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1W-lQA0Br8ztIk6yFuwrK8Jb87e_KWqJC
"""

from googleapiclient.discovery import build
from io import BytesIO
from textblob import TextBlob
import matplotlib.pyplot as plt
import base64
from IPython.display import display, HTML

# Set up YouTube API
api_key = 'AIzaSyDhlCZLO_MR4Va_J3pFplsPf_2ja2BCGE4'
youtube = build('youtube', 'v3', developerKey=api_key)

# Function to fetch YouTube video details
def get_video_details(video_id):
    try:
        request = youtube.videos().list(part='snippet,statistics', id=video_id)
        response = request.execute()
        video = response['items'][0]
        title = video['snippet']['title']
        likes = int(video['statistics']['likeCount'])
        return title, likes
    except Exception as e:
        print(f"Error fetching video details: {e}")
        return None, None

# Function to fetch YouTube comments
def get_video_comments(video_id):
    try:
        comments = []
        request = youtube.commentThreads().list(part='snippet', videoId=video_id, textFormat='plainText')
        while request:
            response = request.execute()
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment)
            request = youtube.commentThreads().list_next(request, response)
        return comments
    except Exception as e:
        print(f"Error fetching comments: {e}")
        return []

# Function to analyze sentiment
def analyze_sentiment(comment):
    analysis = TextBlob(comment)
    return analysis.sentiment.polarity

# Function to get top comments
def get_top_comments(comments, num_comments=3):
    sorted_comments = sorted(comments, key=analyze_sentiment, reverse=True)
    top_positive = sorted_comments[:num_comments]
    top_negative = sorted_comments[-num_comments:]
    return top_positive, top_negative

# Function to visualize results
# Function to visualize results
def visualize_sentiment(sentiment_scores):
    # Categorize sentiments
    positive_comments = sum(1 for score in sentiment_scores if score > 0)
    negative_comments = sum(1 for score in sentiment_scores if score < 0)
    neutral_comments = len(sentiment_scores) - positive_comments - negative_comments

    # Plot
    labels = 'Positive', 'Negative', 'Neutral'
    sizes = [positive_comments, negative_comments, neutral_comments]
    colors = ['gold', 'lightcoral', 'lightskyblue']

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # Pie chart for sentiment distribution
    axes[0].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    axes[0].set_title('Sentiment Distribution')

    # Bar chart for sentiment polarity distribution
    axes[1].bar(labels, sizes, color=colors)
    axes[1].set_title('Sentiment Polarity Distribution')

    plt.tight_layout()

    # Save the plot as an image and encode to base64
    image_buffer = BytesIO()
    plt.savefig(image_buffer, format='png')
    plt.clf()  # Clear the previous plot
    image_buffer.seek(0)
    image_data = base64.b64encode(image_buffer.read()).decode('utf-8')

    return image_data


# Input your video ID
video_id = '_byC1e9ShM0'

# Fetch video details
video_title, video_likes = get_video_details(video_id)

# Fetch comments
comments = get_video_comments(video_id)

# Perform sentiment analysis
sentiment_scores = [analyze_sentiment(comment) for comment in comments]

# Get top comments
top_positive, top_negative = get_top_comments(comments)

# Calculate sentiment percentages
total_comments = len(sentiment_scores)
positive_comments = sum(1 for score in sentiment_scores if score > 0)
negative_comments = sum(1 for score in sentiment_scores if score < 0)
neutral_comments = total_comments - positive_comments - negative_comments
positive_percentage = (positive_comments / total_comments) * 100
negative_percentage = (negative_comments / total_comments) * 100

# Visualize results
image_data = visualize_sentiment(sentiment_scores)

# Display summary using HTML, CSS, and JavaScript
output_html = f"""
    <div style="background-color:#f0f0f0; padding:20px; border-radius:10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
        <h2 style="color:#333; text-align:center;">YouTube Video Sentiment Analysis</h2>
        <hr style="border: 1px solid #ddd; margin-bottom: 20px;">
        <h3 style="color:#333;">Video Details:</h3>
        <p><b>Title:</b> {video_title}</p>
        <p><b>Likes:</b> {video_likes}</p>
        <br>
        <h3 style="color:#333;">Summary:</h3>
        <p>Positive Comments: {positive_comments} ({positive_percentage:.2f}%)</p>
        <p>Negative Comments: {negative_comments} ({negative_percentage:.2f}%)</p>
        <br>
        <h3 style="color:#333;">Top Positive Comments:</h3>
        <ul>{''.join(f'<li style="color:green;">{comment}</li>' for comment in top_positive)}</ul>
        <h3 style="color:#333;">Top Negative Comments:</h3>
        <ul>{''.join(f'<li style="color:red;">{comment}</li>' for comment in top_negative)}</ul>
        <br>
        <h3 style="color:#333;">Sentiment Analysis:</h3>
        <img src="data:image/png;base64,{image_data}" style="max-width: 100%; border-radius: 10px;">

        <!-- JavaScript for pop-up message -->
        <script>
            // Check if the sentiment is positive
            var positiveThreshold = 60; // You can adjust this threshold as needed
            var positivePercentage = {positive_percentage};
            if (positivePercentage >= positiveThreshold) {{
                // Print a message to the console
                console.log("Great news! This video has a positive sentiment analysis!");
            }}
        </script>
    </div>
"""

display(HTML(output_html))