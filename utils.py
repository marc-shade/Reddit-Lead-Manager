from datetime import datetime
import re

def format_date(date_str: str) -> str:
    """Format date string to readable format"""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.000-04:00")
        return date.strftime("%B %d, %Y")
    except:
        return date_str

def clean_text(text: str) -> str:
    """Clean and format text content"""
    if not isinstance(text, str):
        return ""
    
    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove excessive spaces
    text = re.sub(r' {2,}', ' ', text)
    
    # Strip whitespace
    text = text.strip()
    
    return text
