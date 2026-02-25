import requests
import random
import string
import concurrent.futures
import time

# API endpoint
API_URL = "https://api.mvssive.net/auth/register"

# Fixed password
PASSWORD = "@Tekken1122"

# Number of users to create
NUM_USERS = 3000000

# Number of concurrent threads (adjust based on your system's capacity and to avoid rate limiting)
MAX_WORKERS = 100  # Start with a reasonable number to avoid overwhelming the server immediately

def generate_random_email():
    """Generate a random email address."""
    username_length = random.randint(8, 12)
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=username_length))
    domains = ["hiepth.com", "gmail.com", "yahoo.com", "icloud.com","mvssive.net","aol.com"]  # Add more domains if needed
    domain = random.choice(domains)
    return f"{username}@{domain}"

def register_user():
    """Send a POST request to register a user."""
    email = generate_random_email()
    payload = {
        "email": email,
        "password": PASSWORD
    }
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200 or response.status_code == 201:
            print(f"Successfully registered: {email}")
            return True
        else:
            print(f"Failed to register {email}: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error registering {email}: {e}")
        return False

def main():
    successful_registrations = 0
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(register_user) for _ in range(NUM_USERS)]
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                successful_registrations += 1
    
    end_time = time.time()
    print(f"\nCompleted. Successful registrations: {successful_registrations}/{NUM_USERS}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()