import os
import requests
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.environ.get("RAPIDAPI_HOST")
TWITTER_HANDLE = os.environ.get("TWITTER_HANDLE")
if TWITTER_HANDLE:
    TWITTER_HANDLE = TWITTER_HANDLE.strip(' "\'')

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")

COUNT_FILE = "last_count.txt"


def get_post_count(handle):
    """Fetch the post count using a free RapidAPI Twitter endpoint."""
    url = f"https://{RAPIDAPI_HOST}/screenname.php"
    querystring = {"screenname": handle}
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        post_count = data.get("statuses_count", 0)
        return post_count
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def read_last_count():
    if os.path.exists(COUNT_FILE):
        with open(COUNT_FILE, "r") as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return 0
    return 0

def save_current_count(count):
    with open(COUNT_FILE, "w") as f:
        f.write(str(count))

def send_email_notification(handle, old_count, new_count):
    subject = f"🔔 Twitter Post Alert: {handle} posted!"
    body = f"User {handle} has a new post!\n\nPrevious post count: {old_count}\nCurrent post count: {new_count}\n\nCheck it out: https://x.com/{handle}"
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("Email notification sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


def main():
    if not TWITTER_HANDLE:
        print("TWITTER_HANDLE is not set. Please add TWITTER_HANDLE to your .env or environment.")
        return

    print(f"Checking post count for @{TWITTER_HANDLE}...")
    current_count = get_post_count(TWITTER_HANDLE)
    
    if current_count is None:
        return
        
    print(f"Current count is: {current_count}")
    
    last_count = read_last_count()
    
    if current_count > last_count:
        print("New posts detected! Sending email...")
        send_email_notification(TWITTER_HANDLE, last_count, current_count)
        save_current_count(current_count)
    else:
        print("No new posts detected.")
        if last_count == 0 and current_count > 0:
            save_current_count(current_count)

if __name__ == "__main__":
    main()
