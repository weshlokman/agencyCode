import pandas as pd
import argparse

def remove_leads(master_file_path, leads_to_remove_file_path):
    # Load the master file and leads to be removed file into DataFrames
    master_df = pd.read_csv(master_file_path) if master_file_path.endswith('.csv') else pd.read_excel(master_file_path)
    leads_to_remove_df = pd.read_csv(leads_to_remove_file_path) if leads_to_remove_file_path.endswith('.csv') else pd.read_excel(leads_to_remove_file_path)

    # Ensure the relevant columns exist in both files
    if "Public email" not in master_df.columns:
        raise ValueError("The 'Public email' column is not present in the master file.")
    if "Email" not in leads_to_remove_df.columns:
        raise ValueError("The 'Email' column is not present in the leads to be removed file.")

    # Filter out rows from the master file where 'Public email' is in the 'Email' column of leads to be removed
    filtered_master_df = master_df[~master_df['Public email'].isin(leads_to_remove_df['Email'])]

    # Overwrite the master file with the filtered data
    if master_file_path.endswith('.csv'):
        filtered_master_df.to_csv(master_file_path, index=False)
    else:
        filtered_master_df.to_excel(master_file_path, index=False)

    print(f"Master file has been updated: {master_file_path}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Remove leads from master file based on leads_to_be_removed file.")
    parser.add_argument("master_file", help="Path to the master file (CSV or Excel)")
    parser.add_argument("leads_file", help="Path to the leads to be removed file (CSV or Excel)")

    # Parse the arguments
    args = parser.parse_args()

    # Call the remove_leads function with provided arguments
    remove_leads(args.master_file, args.leads_file)

if __name__ == "__main__":
    main()
