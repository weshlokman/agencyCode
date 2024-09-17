import os
import pandas as pd
import re
import argparse

# Function to check if a row contains Arabic letters
def contains_arabic(text):
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(arabic_pattern.search(text))

# Function to check if the text contains keywords from a list (case insensitive)
def contains_keywords(text, keywords):
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in keywords)

# Modified function to exclude rows where "Is business" is "YES"
def clean_and_combine_from_folder_exclude_business(folder_path, keywords_file, output_file):
    combined_df = pd.DataFrame()

    # Load keywords from text file and convert to lowercase for case-insensitive matching
    with open(keywords_file, 'r') as file:
        keywords = [line.strip().lower() for line in file.readlines()]
    
    # Loop through all Excel files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.xlsx'):
            file_path = os.path.join(folder_path, file_name)
            df = pd.read_excel(file_path)

            # Filter out rows where "Is business" is "YES"
            df = df[df['Is business'] != 'YES']

            # Duplicate rows for multiple emails in the "Public email" column
            df = df.assign(Public_email=df['Public email'].str.split(',')).explode('Public_email')

            # Clean the rows based on criteria: contains Arabic or contains keywords
            df_cleaned = df[df.apply(lambda row: contains_arabic(str(row['Biography'])) or contains_keywords(str(row['Biography']), keywords), axis=1)]

            combined_df = pd.concat([combined_df, df_cleaned], ignore_index=True)

    # Remove duplicates
    combined_df.drop_duplicates(inplace=True)

    # Output the cleaned and combined file
    combined_df.to_excel(output_file, index=False)

# Main function to handle command-line arguments
def main():
    parser = argparse.ArgumentParser(description="Clean and combine Excel files.")
    parser.add_argument('folder', help="Folder containing Excel files")
    parser.add_argument('keywords', help="Path to keywords text file")
    parser.add_argument('output', help="Output Excel file name")

    args = parser.parse_args()

    # Call the clean and combine function with business exclusion
    clean_and_combine_from_folder_exclude_business(args.folder, args.keywords, args.output)

if __name__ == "__main__":
    main()
