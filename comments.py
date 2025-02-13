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

def contains_disallowed_words(message):
    blacklist = []  # Hidden to public (read README.md)
    return any(word in message.lower() for word in blacklist)

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
    print(f"AI response: {ai_response}")
    if contains_disallowed_words(ai_response) or contains_disallowed_words(messages[-1]['content']):
        ai_response = "I'm sorry, but I can't respond to that."
    return ai_response

def check_condition(comment):
    return (f'u/anarchychess' in comment.body or 
            (comment.parent_id.startswith('t1_') and comment.parent().author == reddit.user.me())) and \
           not comment.body.startswith("Are you kidding ??? What the **** are you talking about man") and \
           comment.author not in ['anarchychess-ai', 'bot-sleuth-bot', 'pixel-counter-bot', 'AutoModerator']

def bot_action(comment, respond=False):
    messages = [
        {
            "role": "system",
            "content": "" # Hidden to public (read README.md)
        },
        {
            "role": "user",
            "content": comment.body.replace(f'u/anarchychess-ai', '').strip()
        }
    ]
    print(f"Received comment with text: {messages[-1]['content']}")

    if comment.parent_id.startswith('t1_'):
        parent_comment = comment.parent().body
        messages.insert(1, {
            "role": "assistant",
            "content": parent_comment.replace("\n\n---\n\n^This ^is ^a ^bot ^account ^and ^this ^action ^was ^performed ^automatically","")
        })

        if comment.parent().parent_id.startswith('t1_'):
            grandparent_comment = comment.parent().parent().body
            messages.insert(1, {
                "role": "user",
                "content": grandparent_comment
            })

    if respond:
        ai_response = get_ai_response(messages)
        warning = "\n\n---\n\n^This ^is ^a ^bot ^account ^and ^this ^action ^was ^performed ^automatically"
        comment.reply(ai_response + warning)


if __name__ == '__main__':
    reddit = create_reddit_bot()
    
    auth_url = reddit.auth.url(['identity', 'read', 'submit', 'privatemessages'], 'uniqueKey', 'permanent')
    print(f"URL: {auth_url}")
    
    auth_code = input("Auth code: ")
    reddit.auth.authorize(auth_code)

    while True:
        try:
            subreddit = reddit.subreddit('anarchychess')
            comment_stream = subreddit.stream.comments(skip_existing=True)
            
            for comment in comment_stream:
                if check_condition(comment):
                    bot_action(comment, respond=True)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)  # Wait for 5 seconds before retrying
