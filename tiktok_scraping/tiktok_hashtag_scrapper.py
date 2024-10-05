import time
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc


def slow_mouse_move_and_click(driver, element):
    """
    Moves the mouse slowly to the element and clicks it.
    Parameters:
    driver: Selenium WebDriver instance
    element: WebElement to move to and click
    """
    actions = ActionChains(driver)
    actions.move_to_element(element)
    actions.pause(1)  # Pause for a second to simulate a slower move
    actions.click().perform()
    print("Moved to the element slowly and clicked.")


def login_to_tiktok(driver, email, password):
    """
    Logs into TikTok using the provided email and password.
    Parameters:
    driver: Selenium WebDriver instance
    email (str): The email to use for login
    password (str): The password to use for login
    """
    driver.get("https://www.tiktok.com")

    # Click on the login button
    try:
        login_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "header-login-button")))
        slow_mouse_move_and_click(driver, login_button)  # Use slow mouse move and click
        print("Clicked on the login button.")
    except Exception as e:
        print(f"Failed to click on the login button: {e}")
        return

    time.sleep(3)

    # Click on "Use phone / email / username" option
    try:
        use_email_option = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='link' and contains(., 'Use phone / email / username')]"))
        )
        time.sleep(3)
        slow_mouse_move_and_click(driver, use_email_option)  # Use slow mouse move and click
        print("Selected 'Use phone / email / username'.")
    except Exception as e:
        print(f"Failed to select 'Use phone / email / username': {e}")
        return

    time.sleep(3)

    # Click on "Log in with email or username"
    try:
        login_with_email = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Log in with email or username"))
        )
        slow_mouse_move_and_click(driver, login_with_email)  # Use slow mouse move and click
        print("Clicked on 'Log in with email or username'.")
    except Exception as e:
        print(f"Failed to click on 'Log in with email or username': {e}")
        return

    time.sleep(3)

    # Enter email/username and password
    try:
        email_field = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.NAME, "username"))
        )
        email_field.send_keys(email)
        print("Entered email.")
        time.sleep(3)
        password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_field.send_keys(password)
        print("Entered password.")
        time.sleep(3)
        # Click the "Log in" button
        login_button = driver.find_element(By.CSS_SELECTOR, "button[data-e2e='login-button']")
        slow_mouse_move_and_click(driver, login_button)  # Use slow mouse move and click
        print("Clicked the final 'Log in' button.")

        time.sleep(5)  # Wait for login to process
    except Exception as e:
        print(f"Failed during the login process: {e}")


def scrape_tiktok_selenium(hashtag, num_videos=1000, conn=None):
    """
    Scrapes TikTok data for a given hashtag using Selenium and inserts into SQLite database.
    Parameters:
    hashtag (str): The hashtag to search for
    num_videos (int): The number of videos to scrape (default is 1000)
    conn: SQLite database connection object
    """
    # Login credentials
    username = "lokman.91168@outlook.com"
    password = "zidane123@"

    # Define Chrome options (No headless mode)
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("enable-automation")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    # Initialize WebDriver with ChromeDriver Manager (ensures the right driver is used)
    driver = uc.Chrome(options=chrome_options)

    # Perform login
    login_to_tiktok(driver, username, password)
    time.sleep(5)
    print("Continuing script after login.")

    # Navigate to the TikTok hashtag page
    url = f"https://www.tiktok.com/tag/{hashtag}/"
    driver.get(url)

    # Wait for the page to load using explicit wait
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except Exception as e:
        print(f"Page did not load correctly: {e}")
        driver.quit()
        return None

    # Scroll to load more videos until the desired number is reached
    videos = []
    last_video_count = 0  # Track the number of videos before each scroll
    scroll_attempts = 0  # Track the number of consecutive scrolls without new content

    while len(videos) < num_videos:
        # Scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for new content to load
        try:
            WebDriverWait(driver, 5).until(
                lambda driver: len(driver.find_elements(By.CSS_SELECTOR, 'div[class="css-x6y88p-DivItemContainerV2 e19c29qe17"]')) > last_video_count
            )
        except:
            pass

        # Get the currently visible video elements
        videos = driver.find_elements(By.CSS_SELECTOR, 'div[class="css-x6y88p-DivItemContainerV2 e19c29qe17"]')

        # Check if new videos were loaded
        if len(videos) == last_video_count:
            scroll_attempts += 1
        else:
            scroll_attempts = 0  # Reset scroll attempts if new content is loaded

        # Update the last video count to the current count
        last_video_count = len(videos)

        # If no new content is loaded after 5 attempts, break the loop
        if scroll_attempts > 5:
            print("No more content loaded after 5 attempts. Ending scroll.")
            break

        print(f"Videos found so far: {len(videos)}")

    # Process each video and extract data
    for i, video in enumerate(videos[:num_videos]):
        video_data = {}
        try:
            username_element = video.find_element(By.CSS_SELECTOR, 'a[href*="/@"]')
            video_data['username'] = username_element.text

            video_link_element = video.find_element(By.TAG_NAME, 'a')
            video_data['profile_link'] = video_link_element.get_attribute('href')

            img_element = video.find_element(By.TAG_NAME, 'img')
            video_data['video_caption'] = img_element.get_attribute('alt')

            # Insert data into SQLite database with the hashtag
            if conn:
                insert_to_db(conn, video_data, hashtag)
        except Exception as e:
            print(f"Error extracting data for video {i}: {e}")

    # Close the browser
    driver.quit()
    print(f"Total Videos Collected: {len(videos)}")


def insert_to_db(conn, video_data, hashtag):
    query = """
    INSERT OR IGNORE INTO tiktok_videos_1 (username, profile_link, video_caption, hashtag)
    VALUES (?, ?, ?, ?)
    """
    try:
        conn.execute(query, (video_data['username'], video_data['profile_link'], video_data['video_caption'], hashtag))
        conn.commit()
        print(f"Inserted video by {video_data['username']} into the database with hashtag '{hashtag}'.")
    except Exception as e:
        print(f"Failed to insert data into database: {e}")


def create_table(conn):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS tiktok_videos_1 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        profile_link TEXT,
        video_caption TEXT,
        hashtag TEXT
    )
    """
    try:
        conn.execute(create_table_query)
        conn.commit()
        print(f"Table 'tiktok_videos' created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")


def main():
    db_file = "tiktok_videos.db"
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to database: {db_file}")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return

    create_table(conn)

    # Define a list of hashtags to scrape
    hashtags = ["muslim"]

    # Scrape TikTok videos for each hashtag
    for hashtag in hashtags:
        print(f"Scraping videos for hashtag: {hashtag}")
        scrape_tiktok_selenium(hashtag, num_videos=1000, conn=conn)

    conn.close()


if __name__ == "__main__":
    main()
