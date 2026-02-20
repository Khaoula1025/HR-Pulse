import re
import pandas as pd
def audit_salary_symbols(df: pd.DataFrame, column_name: str):
    """
    Checks for unexpected symbols in the salary column.
    Expected: '$', 'K', '-', ' ', '(', ')', '.', 'digits'
    Unexpected: 'M', 'B', '€', '£', etc.
    """
    # Regex pattern: find anything that is NOT a digit, $, K, -, space, period, or parenthesis
    # [^ ...] means "NOT these characters"
    unexpected_pattern = r"[^0-9\$Kk\-\s\.\(\)a-zA-Z]" 
    
    # Identify rows with 'M' or 'B' specifically
    million_rows = df[df[column_name].str.contains(r'M', na=False, case=False)]
    billion_rows = df[df[column_name].str.contains(r'B', na=False, case=False)]
    
    # Identify rows with strange non-standard symbols
    strange_symbols = df[df[column_name].str.contains(unexpected_pattern, na=False)]

    print(f"--- Salary Audit Report for '{column_name}' ---")
    print(f"Total Rows: {len(df)}")
    print(f"Rows with 'M' (Millions): {len(million_rows)}")
    print(f"Rows with 'B' (Billions): {len(billion_rows)}")
    print(f"Rows with unexpected symbols: {len(strange_symbols)}")
    
    if not strange_symbols.empty:
        print("\nExamples of strange entries:")
        print(strange_symbols[column_name].head(5).values)
        
    return strange_symbols

# price=audit_salary_symbols(pd.read_csv("backend/data/raw/jobs.csv"), "Salary Estimate")
# print(price)
def parse_salary(salary_str: str) -> float | None:
    """Convert '$137K-$171K (Glassdoor est.)' to 154000.0"""
    if not isinstance(salary_str,str) or salary_str.lower()=='nan':
        return None
    try:
        multiplier=1000 # if k 
        if 'M' in salary_str.upper():
            multiplier=1000000
        # return only digits d+ and if comma exist return does numbers as well 
        numbers = re.findall(r"\d+\.?\d*", salary_str)
        if len(numbers) >= 2:
            return (float(numbers[0]) + float(numbers[1])) * multiplier / 2
        elif len(numbers) == 1:
            return float(numbers[0]) * multiplier
        return None
    except Exception:
         return None

def clean_size(size_str: str) -> float:
    """Convert '1001 to 5000 employees' to midpoint 3000.0"""
    numbers = re.findall(r"\d+", size_str.replace(",", ""))
    if len(numbers) >= 2:
        return (int(numbers[0]) + int(numbers[1])) / 2
    elif "10000+" in size_str:
        return 15000.0
    return 0.0
