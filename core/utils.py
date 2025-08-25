import random
import string


def generate_verification_code(length=6):
    """
    Generate random verification code.
    
    Args:
        length: Length of verification code (default: 6)
        
    Returns:
        Random string of digits
    """
    return ''.join(random.choices(string.digits, k=length))


def generate_random_string(length=10):
    """
    Generate random string.
    
    Args:
        length: Length of random string (default: 10)
        
    Returns:
        Random string of letters and digits
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length)) 