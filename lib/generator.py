from random import choices
from string import ascii_letters, digits

def generate_alphanum( length=8):
    return ''.join(choices(ascii_letters + digits, k=length))