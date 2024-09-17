import os
import pandas as pd

def combine_excel_files(input_folder, output_file):
    # List to hold dataframes
    all_dataframes = []

    # Loop through each file in the specified folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(input_folder, filename)
            print(f"Processing file: {file_path}")

            # Read the Excel file into a dataframe
            df = pd.read_excel(file_path)

            # Append the dataframe to the list
            all_dataframes.append(df)
    
    if all_dataframes:
        # Concatenate all dataframes into one
        combined_df = pd.concat(all_dataframes, ignore_index=True)

        # Remove duplicate rows
        combined_df.drop_duplicates(inplace=True)

        # Write the combined dataframe to an Excel file
        combined_df.to_excel(output_file, index=False)
        print(f"Combined file saved to: {output_file}")
    else:
        print("No Excel files found in the folder.")

# Example usage
input_folder = "data"  # Replace with your folder path
output_file = "combined_output_health.xlsx"  # Replace with your desired output file name

combine_excel_files(input_folder, output_file)
