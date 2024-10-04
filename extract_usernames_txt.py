import sqlite3


def get_usernames_with_null_emails(db_file):
    """
    Retrieves usernames from the 'tiktok_videos' table where the email is NULL.

    Parameters:
    db_file (str): Path to the SQLite database file.

    Returns:
    List of usernames with NULL emails.
    """
    # Connect to the database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Execute the query to get usernames where email is NULL
    cursor.execute("SELECT username FROM tiktok_videos_1 WHERE email IS NULL")

    # Fetch all results and extract usernames into a list
    usernames = [row[0] for row in cursor.fetchall()]

    # Close the connection
    conn.close()
    return usernames


def write_usernames_to_file(usernames, output_file):
    """
    Writes the list of usernames to a text file.

    Parameters:
    usernames (list): List of usernames.
    output_file (str): The file path to save the usernames.
    """
    with open(output_file, 'w') as f:
        for username in usernames:
            f.write(f"{username}\n")
    print(f"Usernames successfully written to {output_file}")


def main():
    db_file = "tiktok_videos.db"  # Path to your SQLite database file
    output_file = "null_emails_usernames.txt"  # File to save the usernames

    # Retrieve usernames with NULL emails
    usernames = get_usernames_with_null_emails(db_file)
    print(f"Found {len(usernames)} usernames where email is NULL.")

    # Write usernames to a text file
    write_usernames_to_file(usernames, output_file)


if __name__ == "__main__":
    main()
