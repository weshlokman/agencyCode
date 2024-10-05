import os
import pandas as pd
import re
import argparse
from datetime import datetime


# Function to check if a text contains Arabic letters
def contains_arabic(text):
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(arabic_pattern.search(text))


# Function to check if the text contains any of the keywords (case insensitive)
def contains_keywords(text, keywords):
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in keywords)


# Function to check if any name from names_keywords.txt is contained in 'Full name'
def contains_name(text, names):
    text_lower = text.lower()
    return any(name.lower() in text_lower for name in names)


# Function to clean and combine data from Excel files
def clean_and_combine_from_folder_exclude_business(folder_path, keywords_file, names_file, min_followers, max_followers):
    combined_df = pd.DataFrame()
    business_df = pd.DataFrame()

    # Load keywords from the text file (strip spaces and normalize case)
    with open(keywords_file, 'r') as file:
        keywords = [line.strip().lower() for line in file.readlines()]

    # Load names from the names_keywords.txt file
    with open(names_file, 'r') as file:
        names = [line.strip().lower() for line in file.readlines()]

    # Loop through all Excel files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.xlsx'):
            file_path = os.path.join(folder_path, file_name)
            df = pd.read_excel(file_path)

            # Strip any leading/trailing spaces from column names
            df.columns = df.columns.str.strip()

            # Check if 'Is business' column exists and handle it
            if 'Is business' in df.columns:
                # Separate businesses into their own DataFrame
                business_df = pd.concat([business_df, df[df['Is business'] == 'YES']], ignore_index=True)

                # Filter out rows where "Is business" is "YES" for the main combined file
                df = df[df['Is business'] != 'YES']
            else:
                print(f"'Is business' column not found in {file_name}, skipping business filtering for this file.")

            # Filter rows based on the "Followers count" column
            if 'Followers count' in df.columns:
                df = df[(df['Followers count'] >= min_followers) & (df['Followers count'] <= max_followers)]
            else:
                print(f"'Followers count' column not found in {file_name}, skipping follower filtering for this file.")

            # Split emails and explode into multiple rows
            if 'Public email' in df.columns:
                df['Public email'] = df['Public email'].str.split(',')  # Split emails by comma
                df = df.explode('Public email')  # Duplicate rows for each email
                df['Public email'] = df['Public email'].str.strip()  # Remove any leading/trailing spaces from email

            # Apply cleaning criteria: contains Arabic in 'Full name' or 'Biography',
            # contains keywords in 'Biography', or contains names in 'Full name'
            df_cleaned = df[df.apply(
                lambda row: contains_arabic(str(row.get('Full name', ''))) or
                            contains_arabic(str(row.get('Biography', ''))) or
                            contains_keywords(str(row.get('Biography', '')), keywords) or
                            contains_name(str(row.get('Full name', '')), names),
                axis=1
            )]

            combined_df = pd.concat([combined_df, df_cleaned], ignore_index=True)

    # Remove duplicates from the main combined file
    combined_df.drop_duplicates(inplace=True)

    # Automatically create output file names with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'cleaned_combined_file_{timestamp}.xlsx'
    business_output_file = f'businesses_muslim_{timestamp}.xlsx'

    # Output the cleaned and combined file
    combined_df.to_excel(output_file, index=False)
    print(f"File saved as: {output_file}")

    # Output the business-specific file if there are rows to save
    if not business_df.empty:
        business_df.drop_duplicates(inplace=True)
        business_df.to_excel(business_output_file, index=False)
        print(f"Businesses saved as: {business_output_file}")
    else:
        print("No business rows found.")


# Main function to handle command-line arguments
def main():
    parser = argparse.ArgumentParser(description="Clean and combine Excel files.")
    parser.add_argument('folder', help="Folder containing Excel files")
    parser.add_argument('keywords', help="Path to keywords text file")
    parser.add_argument('names', help="Path to names_keywords.txt file")
    parser.add_argument('--min_followers', type=int, default=22000, help="Minimum number of followers to include")
    parser.add_argument('--max_followers', type=int, default=300000, help="Maximum number of followers to include")

    args = parser.parse_args()

    # Call the clean and combine function with follower count thresholds
    clean_and_combine_from_folder_exclude_business(args.folder, args.keywords, args.names, args.min_followers, args.max_followers)


if __name__ == "__main__":
    main()
