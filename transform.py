import pandas as pd


def clean_csv_duplicates(input_path: str, output_path: str) -> None:
    """
    Clean duplicate entries from a CSV file based on the 'name' column.
    
    Args:
        input_path: Path to the input CSV file
        output_path: Path to save the cleaned CSV file
    """
    # Read the original file
    df = pd.read_csv(input_path)
    
    # Remove duplicates keeping the first occurrence
    df_clean = df.drop_duplicates(subset=['name'], keep='first')
    
    # Save to new file
    df_clean.to_csv(output_path, index=False)

def format_phone_numbers(input_path: str, output_path: str) -> None:
    """
    Format phone numbers from a CSV file to the standard format +584123456789.
    Handles multiple numbers separated by slashes, dashes, or commas.
    Removes any non-numeric characters and ensures the number starts with +58.
    
    Args:
        input_path: Path to the input CSV file containing phone numbers
        output_path: Path to save the CSV file with formatted phone numbers
        
    Example:
        Input: "0412-123.45.67 / 0424-987.65.43"
        Output: "+584121234567, +584249876543"
    """
    # Read the CSV file
    df = pd.read_csv(input_path)
    
    # Function to format individual phone numbers
    def format_number(phone):
        if pd.isna(phone):
            return phone
            
        # Split multiple numbers by common separators
        numbers = str(phone).replace('/', ',').replace('-', ',').split(',')
        formatted_numbers = []
        
        for num in numbers:
            # Remove all non-numeric characters
            numbers_only = ''.join(filter(str.isdigit, str(num)))
            
            # Skip if empty after filtering
            if not numbers_only:
                continue
                
            # Remove leading 0 if present
            if numbers_only.startswith('0'):
                numbers_only = numbers_only[1:]
                
            # Add 58 prefix if not present
            if not numbers_only.startswith('58'):
                numbers_only = '58' + numbers_only
                
            formatted_numbers.append('+' + numbers_only)
            
        return ', '.join(formatted_numbers) if formatted_numbers else phone

    # Apply formatting to phone column
    df['phone'] = df['phone'].apply(format_number)
    
    # Save formatted data
    df.to_csv(output_path, index=False)

