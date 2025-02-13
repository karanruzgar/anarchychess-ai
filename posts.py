import praw
import time
from openai import OpenAI

client = OpenAI(api_key='openai-api-key')

def create_reddit_bot():
    reddit = praw.Reddit(
        client_id='client-id',
        client_secret='client-secret',
        user_agent='user_agent',
        redirect_uri='http://localhost:8000'
    )
    return reddit

def get_ai_response(messages):
    response = client.chat.completions.create(
        model="ai-model",
        messages=messages,
        response_format={
            "type": "text"
        },
        temperature=1.1,
        max_completion_tokens=1024,
        top_p=0.8,
        frequency_penalty=0,
        presence_penalty=1.1
    )
    ai_response = response.choices[0].message.content
    slurs = []  # Hidden to public

    if any(slur in ai_response.lower() for slur in slurs):
        ai_response = "I'm sorry, but I can't respond to that."
    return ai_response

def bot_post_action(submission, respond=False):
    messages = [
        {
            "role": "system",
            "content": "" # Hidden to public
        },
        {
            "role": "user",
            "content": submission.title
        }
    ]
    print(f"Received post with title: {messages[-1]['content']}")
    
    if respond:
        ai_response = get_ai_response(messages)
        print(ai_response)
        warning = "\n\n---\n\n^This ^is ^a ^bot ^account ^and ^this ^action ^was ^performed ^automatically"
        submission.reply(ai_response + warning)

if __name__ == '__main__':
    reddit = create_reddit_bot()
    
    auth_url = reddit.auth.url(['identity', 'read', 'submit', 'privatemessages'], 'uniqueKey', 'permanent')
    print(f"URL: {auth_url}")
    
    auth_code = input("Auth code: ")
    reddit.auth.authorize(auth_code)

    while True:
        try:
            subreddit = reddit.subreddit('anarchychess')
            submission_stream = subreddit.stream.submissions(skip_existing=True)
            
            for submission in submission_stream:
                bot_post_action(submission, respond=True)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
