import pandas as pd

def load_excel_file(file_path):
    """Load an Excel file into a pandas DataFrame."""
    return pd.read_excel(file_path)

def extract_data(df, columns_to_extract):
    """Extract specified columns from the DataFrame and return a list of dictionaries."""
    extracted_data = []

    for _, row in df[columns_to_extract].iterrows():
        row_dict = {col.lower(): row[col] for col in columns_to_extract}  # Convert keys to lowercase

        # Rename 'protein %' to 'protein'
        if 'protein %' in row_dict:
            row_dict['protein'] = row_dict.pop('protein %')

        extracted_data.append(row_dict)

    return extracted_data

def print_extracted_data(extracted_data):
    """Print the extracted data in a structured format."""
    for count, row in enumerate(extracted_data, start=1):
        print(f"Row {count}: {row}")

def main():
    # File path to the Excel file
    file_path = '../SampleInputs/Pulse database for projects 4 .xlsx'  # Update this to your file path

    # Columns to extract from the DataFrame
    columns_to_extract = ['SAMPLE', 'PROTEIN %', 'PDCAAS', 'IVPDCAAS']

    # Load the Excel file
    df = load_excel_file(file_path)

    # Extract the required data
    extracted_data = extract_data(df, columns_to_extract)

    # Print the extracted data
    print_extracted_data(extracted_data)

# Entry point for the script
if __name__ == "__main__":
    main()
