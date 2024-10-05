import re
import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def check_and_add_columns(conn):
    """
    Checks for required columns in the 'tiktok_videos' table and adds them if they do not exist.

    Parameters:
    conn: SQLite database connection object.
    """
    cursor = conn.cursor()
    # Check if necessary columns exist
    cursor.execute("PRAGMA table_info(tiktok_videos)")
    columns = [info[1] for info in cursor.fetchall()]

    # Add missing columns
    if 'user_bio' not in columns:
        cursor.execute("ALTER TABLE tiktok_videos ADD COLUMN user_bio TEXT")
        print("Added column 'user_bio' to the table.")

    if 'email' not in columns:
        cursor.execute("ALTER TABLE tiktok_videos ADD COLUMN email TEXT")
        print("Added column 'email' to the table.")

    if 'instagram_handle' not in columns:
        cursor.execute("ALTER TABLE tiktok_videos ADD COLUMN instagram_handle TEXT")
        print("Added column 'instagram_handle' to the table.")

    if 'instagram_profile_link' not in columns:
        cursor.execute("ALTER TABLE tiktok_videos ADD COLUMN instagram_profile_link TEXT")
        print("Added column 'instagram_profile_link' to the table.")

    if 'followers_count' not in columns:
        cursor.execute("ALTER TABLE tiktok_videos ADD COLUMN followers_count INTEGER")
        print("Added column 'followers_count' to the table.")

    conn.commit()


def read_usernames_from_db(db_file):
    """
    Reads distinct usernames from the 'tiktok_videos' table in the database.

    Parameters:
    db_file (str): Path to the SQLite database file.

    Returns:
    List of usernames.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT username FROM tiktok_videos WHERE username IS NOT NULL")
    usernames = [row[0] for row in cursor.fetchall()]
    conn.close()
    return usernames


def update_user_info(conn, username, bio, email, instagram, instagram_link, followers_count):
    """
    Updates the 'user_bio', 'email', 'instagram_handle', 'instagram_profile_link', and 'followers_count' fields.

    Parameters:
    conn: SQLite database connection object.
    username (str): Username of the TikTok user.
    bio (str): The bio content to be updated.
    email (str): The extracted email from the bio.
    instagram (str): The extracted Instagram handle from the bio.
    instagram_link (str): The extracted Instagram profile link.
    followers_count (int): The extracted followers count.
    """
    cursor = conn.cursor()
    query = """
    UPDATE tiktok_videos
    SET user_bio = ?, email = ?, instagram_handle = ?, instagram_profile_link = ?, followers_count = ?
    WHERE username = ?
    """
    cursor.execute(query, (bio, email, instagram, instagram_link, followers_count, username))
    conn.commit()
    print(f"Updated info for {username}.")


def scrape_user_bio_and_followers(driver, username):
    """
    Navigates to a TikTok user's profile and scrapes the bio and followers count.

    Parameters:
    driver: Selenium WebDriver instance.
    username (str): The TikTok username to visit.

    Returns:
    Tuple of (bio_content, followers_count)
    """
    url = f"https://www.tiktok.com/@{username}"
    print(f"Visiting profile: {url}")

    # Navigate to the profile page
    driver.get(url)

    # Simulate human-like scrolling behavior and wait
    driver.execute_script("window.scrollTo(0, 500);")  # Scroll down by 500 pixels
    time.sleep(1.5)  # Stay on the page for 1.5 seconds

    bio_content = None
    followers_count = None

    try:
        # Wait for the user bio element to be visible
        bio_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-e2e="user-bio"]'))
        )
        # Extract the inner HTML of the bio element
        bio_content = bio_element.get_attribute("innerHTML")

        # Wait for the followers count element and extract its content
        followers_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'strong[data-e2e="followers-count"]'))
        )
        followers_count = followers_element.get_attribute("innerHTML")
        followers_count = int(followers_count.replace(",", ""))  # Convert to integer
    except Exception as e:
        print(f"Failed to extract bio or followers for {username}: {e}")

    return bio_content, followers_count


def extract_email_and_instagram(bio):
    """
    Extracts email and Instagram handle from the bio content using regular expressions.

    Parameters:
    bio (str): The bio content to search.

    Returns:
    Tuple of (email, instagram_handle, instagram_link).
    """
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    instagram_pattern = r"(?i)instagram.com/([a-zA-Z0-9._]+)|@([a-zA-Z0-9._]+)"

    # Find the first occurrence of email and Instagram handle in the bio
    email = re.search(email_pattern, bio)
    instagram = re.search(instagram_pattern, bio)

    # Extract matched values
    email = email.group(0) if email else None
    instagram_handle = instagram.group(1) or instagram.group(2) if instagram else None

    # Check for a full Instagram URL if found
    instagram_link = f"https://www.instagram.com/{instagram_handle}/" if instagram_handle else None

    return email, instagram_handle, instagram_link


def main():
    db_file = "tiktok_videos.db"
    usernames = read_usernames_from_db(db_file)
    print(f"Found {len(usernames)} usernames to process.")
    conn = sqlite3.connect(db_file)

    # Check and add missing columns
    check_and_add_columns(conn)

    # Define Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    for username in usernames:
        if not username.strip():
            continue

        bio, followers_count = scrape_user_bio_and_followers(driver, username)

        if bio:
            email, instagram_handle, instagram_link = extract_email_and_instagram(bio)

            # Update the database with the extracted information
            update_user_info(conn, username, bio, email, instagram_handle, instagram_link, followers_count)

        time.sleep(5)

    driver.quit()
    conn.close()
    print("Finished updating all users.")


if __name__ == "__main__":
    main()
