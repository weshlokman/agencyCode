import re
import pandas as pd
import argparse

def extract_instagram(text):
    """
    Extract Instagram handle from the given text using regex.
    Handles variations like @handle, instagram.com/handle, or "instagram handle_name".
    """
    instagram_pattern = r"(?i)(?:@|https?://(?:www\.)?instagram\.com/|instagram\s)([a-zA-Z0-9._]+)"
    match = re.search(instagram_pattern, text)
    return match.group(1) if match else None

def extract_email(text):
    """
    Extract email address from the given text using regex.
    """
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    match = re.search(email_pattern, text)
    return match.group(0) if match else None

def extract_phone_number(text):
    """
    Extract phone number from the given text using regex.
    Handles multiple formats including international numbers.
    """
    phone_pattern = r"(\+?\d{1,3}[-.\s]??\d{1,4}[-.\s]??\d{1,4}[-.\s]??\d{1,9}|\(\d{2,6}\)\s*\d{3,4}[-.\s]??\d{3,4}|\d{4}[-.\s]??\d{3,4}[-.\s]??\d{3,4})"
    match = re.search(phone_pattern, text)
    return match.group(0) if match else None

def process_file(file_path, min_fans):
    """
    Process the given file (Excel or CSV) to extract Instagram handles, emails, and phone numbers
    from the 'authorMeta.signature' column, filter based on 'authorMeta.fans', and save the result to two new files.
    """
    # Determine if the file is CSV or Excel based on its extension
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        print(f"Unsupported file format. Please provide a '.csv' or '.xlsx' file.")
        return

    # Ensure the necessary columns exist
    if 'authorMeta/signature' not in df.columns or 'authorMeta/fans' not in df.columns:
        print(f"'authorMeta.signature' or 'authorMeta.fans' columns not found in the file.")
        return

    # Filter rows based on the minimum fans count
    df_filtered = df[df['authorMeta/fans'] >= min_fans]
    print(f"Filtered to {len(df_filtered)} rows with at least {min_fans} fans.")

    # Create new columns for the extracted data
    df_filtered['instagram'] = df_filtered['authorMeta/signature'].astype(str).apply(extract_instagram)
    df_filtered['email'] = df_filtered['authorMeta/signature'].astype(str).apply(extract_email)
    df_filtered['phone_number'] = df_filtered['authorMeta/signature'].astype(str).apply(extract_phone_number)

    # Remove duplicate rows based on the 'email' column
    df_filtered = df_filtered.drop_duplicates(subset='email', keep='first')

    # Save the complete filtered data to a new file
    if file_path.endswith('.csv'):
        complete_output_file = file_path.replace(".csv", f"_with_extracted_data_min_fans_{min_fans}.csv")
    elif file_path.endswith('.xlsx'):
        complete_output_file = file_path.replace(".xlsx", f"_with_extracted_data_min_fans_{min_fans}.xlsx")

    if file_path.endswith('.csv'):
        df_filtered.to_csv(complete_output_file, index=False)
    else:
        df_filtered.to_excel(complete_output_file, index=False)

    print(f"Complete data processed and saved to {complete_output_file}")

    # Create a filtered DataFrame containing only rows where 'email' is not null
    df_with_emails = df_filtered[df_filtered['email'].notnull()]

    # Save the filtered data to a new file
    if file_path.endswith('.csv'):
        email_output_file = file_path.replace(".csv", f"_emails_only_min_fans_{min_fans}.csv")
        df_with_emails.to_csv(email_output_file, index=False)
    else:
        email_output_file = file_path.replace(".xlsx", f"_emails_only_min_fans_{min_fans}.xlsx")
        df_with_emails.to_excel(email_output_file, index=False)

    print(f"Rows with emails saved to {email_output_file}")

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Extract Instagram, email, and phone numbers from a specified Excel or CSV file with optional fan filtering.')
    parser.add_argument('file', help='The path to the Excel (.xlsx) or CSV (.csv) file to process.')
    parser.add_argument('--min_fans', type=int, default=0, help='Minimum number of fans required to include a row (default is 0).')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Process the specified file with the given minimum fan count
    process_file(args.file, args.min_fans)
