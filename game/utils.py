from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from pycipher import Caesar as CaesarCipher
from pycipher import Rot13
from pycipher import Vigenere as VigenereCipher
from pycipher import Atbash as AtbashCipher
from pycipher import Railfence
from pycipher import ColTrans
from pycipher import Gronsfeld
from pycipher import ADFGVX
import base64
import os
import codecs
import math

def rot13_encrypt(text):
    """
    Implements ROT13 encryption using pycipher
    """
    cipher = Rot13()
    return cipher.encipher(text)

def caesar_encrypt(text, shift=1):
    """
    Implements Caesar cipher using pycipher
    """
    cipher = CaesarCipher(key=shift)
    return cipher.encipher(text)

def binary_ascii_encrypt(text):
    """
    Converts text to binary ASCII representation using built-in functions
    """
    return ' '.join(format(ord(char), '08b') for char in text)

def decimal_ascii_encrypt(text):
    """
    Converts text to decimal ASCII representation
    """
    return ' '.join(str(ord(char)) for char in text)

def number_to_letter_encrypt(text):
    """
    Converts text to number representation (A=1, B=2, etc.)
    """
    return ' '.join(str(ord(char.upper()) - ord('A') + 1) for char in text if char.isalpha())

def atbash_encrypt(text):
    """
    Implements Atbash cipher using pycipher
    """
    cipher = AtbashCipher()
    return cipher.encipher(text)

def vigenere_encrypt(text, key):
    """
    Implements Vigenère cipher using pycipher
    """
    cipher = VigenereCipher(key)
    return cipher.encipher(text)

def morse_code_encrypt(text):
    """
    Converts text to Morse code using a dictionary
    """
    MORSE_CODE_DICT = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
        'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--',
        '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
        '9': '----.', '0': '-----', ' ': ' ', '.': '.-.-.-', ',': '--..--',
        '°': '---', 'N': '-.', 'E': '.'
    }
    return ' '.join(MORSE_CODE_DICT.get(char.upper(), char) for char in text)

def rail_fence_encrypt(text, rails=3):
    """
    Implements Rail Fence cipher using pycipher
    """
    cipher = Railfence(rails)
    return cipher.encipher(text)

def columnar_transposition_encrypt(text, key):
    """
    Implements Columnar Transposition cipher using pycipher
    Args:
        text: The text to encrypt
        key: The keyword used to determine the column order
    """
    cipher = ColTrans(key)
    return cipher.encipher(text)

def permuted_matrix_encrypt(text, row_perm, col_perm):
    """
    Implements Matrix Transposition with row and column permutations
    Args:
        text: The text to encrypt
        row_perm: List of integers representing row permutation (1-based)
        col_perm: List of integers representing column permutation (1-based)
    Example:
        text = "HELLO"
        row_perm = [2,1]  # 2nd row becomes 1st, 1st row becomes 2nd
        col_perm = [3,1,2]  # 3rd col becomes 1st, 1st becomes 2nd, 2nd becomes 3rd
    """
    # Remove spaces
    text = text.replace(" ", "")
    rows = len(row_perm)
    cols = len(col_perm)
    chunk_size = rows * cols
    result = ''
    
    # Process text in chunks
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i+chunk_size]
        # Pad the last chunk if needed
        if len(chunk) < chunk_size:
            chunk = chunk + 'X' * (chunk_size - len(chunk))
        
        # Create matrix for this chunk
        matrix = []
        for j in range(0, len(chunk), cols):
            matrix.append(list(chunk[j:j + cols]))
        
        # Apply row permutation
        new_matrix = []
        for r in row_perm:
            new_matrix.append(matrix[r-1])  # -1 because permutation is 1-based
        
        # Apply column permutation and read result
        for c in col_perm:
            for r in range(rows):
                result += new_matrix[r][c-1]  # -1 because permutation is 1-based
    
    return result

def binary_columnar_encrypt(text):
    """
    Implements a composite encryption:
    1. Converts numbers to binary while preserving special characters
    2. Applies columnar transposition using pycipher's ColTrans with keyword 'FINAL'
    Special characters and spaces are preserved, with spaces converted to '_'
    """
    # Convert numbers to binary while preserving other characters
    binary_text = ''
    i = 0
    while i < len(text):
        if text[i].isdigit():
            # Handle multi-digit numbers
            num = ''
            while i < len(text) and text[i].isdigit():
                num += text[i]
                i += 1
            # Convert number to 8-bit binary and remove '0b' prefix
            binary = bin(int(num))[2:].zfill(8)
            binary_text += binary
        elif text[i] == ' ':
            # Replace spaces with underscore for visibility
            binary_text += '_'
            i += 1
        else:
            binary_text += text[i]
            i += 1
    
    # Apply columnar transposition using pycipher
    cipher = ColTrans('FINAL')
    return cipher.encipher(binary_text)

def test_gronsfeld():
    """
    Test function to see how Gronsfeld handles special characters
    """
    cipher = Gronsfeld([5, 4, 7, 9, 8])  # Example key using numbers
    test_text = "48.8566° N, 2.3522° E"
    encrypted = cipher.encipher(test_text)
    decrypted = cipher.decipher(encrypted)
    print("Original:", test_text)
    print("Encrypted:", encrypted)
    print("Decrypted:", decrypted)
    return encrypted

def adfgvx_encrypt(text):
    """
    Implements ADFGVX cipher using pycipher.
    Uses a 6x6 key square for A-Z and 0-9, and a keyword for transposition.
    """
    # Key square containing a-z and 0-9 (36 characters total)
    key_square = 'PHQGIUMEAYLNOFDXJKRCVSTZWB0123456789'

    # Check length
    print("Length of key_square:", len(key_square))  # Must be 36
    print("Unique characters:", len(set(key_square)))  # Must be 36

    plaintext = '488566N23522E'.upper()

    # Check which characters are NOT in the key_square
    missing = [char for char in plaintext if char not in key_square]
    print("Characters NOT in key_square:", missing)

    # Keyword for the columnar transposition part
    keyword = 'FINAL'
    
    cipher = ADFGVX(key_square, keyword)
    return cipher.encipher(text)

def test_adfgvx():
    """
    Test function to debug ADFGVX cipher output
    """
    text = '488566N23522E'
    key_square = 'ABCDEF0123456789GHIJKLMNOPQRSTUVWXYZ'
    keyword = 'FINAL'
    
    cipher = ADFGVX(key_square, keyword)
    encrypted = cipher.encipher(text)
    print("Original text:", text)
    print("Key square:", key_square)
    print("Keyword:", keyword)
    print("Encrypted (len=%d):" % len(encrypted), encrypted)
    print("Encrypted bytes:", [ord(c) for c in encrypted])
    return encrypted 