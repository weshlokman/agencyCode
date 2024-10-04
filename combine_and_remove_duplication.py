import os
import pandas as pd

def combine_files(input_folder, output_file):
    """
    Combine all Excel and CSV files from the specified folder into a single file,
    ensuring that rows with duplicate 'Public email' values are not added.
    Only rows with a non-null 'Public email' are included.

    Parameters:
    - input_folder (str): Path to the folder containing the files.
    - output_file (str): Name of the output file to save the combined content.
    """
    # List to hold dataframes
    all_dataframes = []

    # Loop through each file in the specified folder
    for root, _, files in os.walk(input_folder):
        for filename in files:
            file_path = os.path.join(root, filename)

            # Process Excel files
            if filename.endswith(".xlsx") or filename.endswith(".xls"):
                print(f"Processing Excel file: {file_path}")
                try:
                    df = pd.read_excel(file_path)
                    all_dataframes.append(df)
                except Exception as e:
                    print(f"Failed to read {file_path}: {e}")

            # Process CSV files
            elif filename.endswith(".csv"):
                print(f"Processing CSV file: {file_path}")
                try:
                    df = pd.read_csv(file_path)
                    all_dataframes.append(df)
                except Exception as e:
                    print(f"Failed to read {file_path}: {e}")

    if all_dataframes:
        # Concatenate all dataframes into one, aligning columns
        combined_df = pd.concat(all_dataframes, ignore_index=True, sort=False)

        # Ensure 'Public email' column is present and drop rows without it
        if 'Public email' not in combined_df.columns:
            print("Column 'Public email' not found in the files. Unable to proceed with deduplication.")
            return

        # Filter out rows where 'Public email' is NaN or empty
        combined_df = combined_df[combined_df['Public email'].notnull() & (combined_df['Public email'].astype(str) != '')]

        # Remove rows where 'Public email' is duplicated (keeping the first occurrence)
        combined_df.drop_duplicates(subset=['Public email'], inplace=True)

        # Write the combined dataframe to an Excel file
        combined_df.to_excel(output_file, index=False)
        print(f"Combined file saved to: {output_file}")
    else:
        print("No valid files found in the folder.")

# Example usage
input_folder = "data"  # Replace with your folder path
output_file = "all_leads_from_muslim_campaigns_filtered.xlsx"  # Replace with your desired output file name

combine_files(input_folder, output_file)
