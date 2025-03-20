import re

STOP_WORDS = {
    'the', 'and', 'a', 'of', 'to', 'in', 'is', 'it', 'you', 'that', 'on', 'for', 'with', 'as', 'this', 'by', 'at'
}

def tokenize(text):
    """
    Tokenize text into words using a regular expression and filter out stop words and short words.
    """
    words = re.findall(r'\b\w+\b', text.lower())
 
    return [word for word in words if word not in STOP_WORDS and len(word) > 2]


