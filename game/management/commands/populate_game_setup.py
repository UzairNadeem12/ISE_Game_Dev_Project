from django.core.management.base import BaseCommand
from game.models import GameSetup
from pycipher import Caesar, Atbash, Vigenere, Railfence, ColTrans, ADFGVX
import re

class Command(BaseCommand):
    help = 'Populates the GameSetup table with initial data'

    def decimal_ascii_encrypt(self, text):
        return ' '.join(str(ord(c)) for c in text)

    def caesar_encrypt_shift_13(self, text):
        return Caesar(key=13).encipher(text)

    def atbash_encrypt(self, text):
        return Atbash().encipher(text)

    def vigenere_encrypt_RAT(self, text):
        return Vigenere(key='RAT').encipher(text)

    def rail_fence_encrypt_3(self, text):
        return Railfence(key=3).encipher(text)

    def columnar_transposition_encrypt_RAT(self, text):
        # Create ColTrans instance with the key
        ct = ColTrans('RAT')
        return ct.encipher(text)

    def permuted_matrix_encrypt_2x6(self, text):
        text = re.sub(r'\s+', '', text)
        result = ''
        
        # Process text in chunks of 12 characters
        for i in range(0, len(text), 12):
            chunk = text[i:i+12]
            # Pad the last chunk if needed
            if len(chunk) < 12:
                chunk += 'X' * (12 - len(chunk))
            
            # Create 2x6 matrix for this chunk
            matrix = [chunk[i:i+6] for i in range(0, len(chunk), 6)]
            matrix = [matrix[1], matrix[0]]  # Row permutation [2,1]
            
            # Apply column permutation [3,1,5,2,6,4] - reading down columns
            for col_idx in [2, 0, 4, 1, 5, 3]:  # [3,1,5,2,6,4] adjusted for 0-based indexing
                for row in matrix:
                    result += row[col_idx]
        
        return result

    def adfgvx_encrypt(self, text):
        # Function expects all-letter input (like 'DHHEFFXBCEBBX')
        key_square = 'PHQGIUMEAYLNOFDXJKRCVSTZWB0123456789'
        keyword = 'FINAL'
        cipher = ADFGVX(key_square, keyword)
        return cipher.encipher(text)

    def handle(self, *args, **kwargs):
        game_setups = [
            {
                'challenge_id': '1',
                'stage': 'continent',
                'answer': 'Europe',
                'encryption_type': 'Decimal ASCII',
                'hint': 'Convert each number to its ASCII character',
                'tutorial': 'ASCII codes can be represented in decimal. Each number corresponds to a character. For example, 65 is the ASCII code for A, 66 for B, and so on.',
                'difficulty': 1,
                'encrypt_func': 'decimal_ascii_encrypt',
                'encrypted_message': self.decimal_ascii_encrypt('Europe')
            },
            {
                'challenge_id': '1',
                'stage': 'country',
                'answer': 'France',
                'encryption_type': 'Caesar Cipher (Shift + 13)',
                'hint': 'Each letter is shifted thirteen positions forward in the alphabet',
                'tutorial': 'In a Caesar cipher, each letter in the plaintext is shifted a certain number of positions down the alphabet. For example, with a shift of 2, A becomes C, B becomes D, and so on.',
                'difficulty': 2,
                'encrypt_func': 'caesar_encrypt_shift_13',
                'encrypted_message': self.caesar_encrypt_shift_13('France')
            },
            {
                'challenge_id': '1',
                'stage': 'region',
                'answer': 'North',
                'encryption_type': 'Atbash Cipher',
                'hint': 'Each letter is mapped to its reverse in the alphabet (A=Z, B=Y...)',
                'tutorial': 'The Atbash cipher is a substitution cipher where each letter is mapped to its reverse in the alphabet. For example, A becomes Z, B becomes Y, and so on.',
                'difficulty': 2,
                'encrypt_func': 'atbash_encrypt',
                'encrypted_message': self.atbash_encrypt('North')
            },
            {
                'challenge_id': '1',
                'stage': 'city',
                'answer': 'Paris',
                'encryption_type': 'Vigenère Cipher (key: RAT)',
                'hint': 'Each letter is shifted according to a keyword',
                'tutorial': 'The Vigenère cipher uses a keyword to determine the shift for each letter. The keyword is repeated to match the length of the message. Each letter in the keyword determines how many positions to shift the corresponding letter in the message.',
                'difficulty': 3,
                'encrypt_func': 'vigenere_encrypt_RAT',
                'encrypted_message': self.vigenere_encrypt_RAT('Paris')
            },
            {
                'challenge_id': '1',
                'stage': 'district',
                'answer': 'Le Marais',
                'encryption_type': 'Rail Fence Cipher (3 rails)',
                'hint': 'The text is arranged in a zigzag pattern on 3 rails and read off horizontally',
                'tutorial': 'In a Rail Fence cipher, the text is written in a zigzag pattern across 3 rails (rows) and then read off row by row. For example, "HELLO" with 3 rails becomes:\nH   O\nE L\nL\nWhich is then read as "HOELL"',
                'difficulty': 3,
                'encrypt_func': 'rail_fence_encrypt_3',
                'encrypted_message': self.rail_fence_encrypt_3('Le Marais')
            },
            {
                'challenge_id': '1',
                'stage': 'area',
                'answer': 'Marais',
                'encryption_type': 'Columnar Transposition (key: RAT)',
                'hint': 'The text is written in columns under the key word RAT, then read off based on alphabetical order of the key letters',
                'tutorial': 'In a Columnar Transposition cipher, the text is written under a keyword (RAT) and read off in columns based on the alphabetical order of the key letters. For example, with RAT:\nR A T\nh e l\nl l o\nThe columns are read in order A(1), R(2), T(3), giving: "elhlol"',
                'difficulty': 4,
                'encrypt_func': 'columnar_transposition_encrypt_RAT',
                'encrypted_message': self.columnar_transposition_encrypt_RAT('Marais')
            },
            {
                'challenge_id': '1',
                'stage': 'street',
                'answer': 'Rue de Rivoli',
                'encryption_type': 'Matrix Transposition (2x6 matrix with permutations)',
                'hint': 'The text is processed in chunks of 12 characters. Each chunk is arranged in a 2x6 matrix, rows are swapped [2,1], and columns are reordered [3,1,5,2,6,4]. Read down each column in the new order.',
                'tutorial': 'This cipher works in three steps:\n\n1. Text Preparation:\n   - Remove all spaces\n   - Split text into chunks of 12 characters\n   - If the last chunk is shorter than 12 characters, pad it with X\n\n2. For each 12-character chunk:\n   - Arrange it in a 2x6 matrix (2 rows, 6 columns)\n   - Example for "HELLOWORLDXX":\n     ```\n     H E L L O W\n     O R L D X X\n     ```\n\n3. Apply Permutations:\n   a) Row Permutation [2,1]:\n      - Swap the rows\n      - Result:\n      ```\n      O R L D X X\n      H E L L O W\n      ```\n   b) Column Permutation [3,1,5,2,6,4]:\n      - Read columns in this order: 3rd, 1st, 5th, 2nd, 6th, 4th\n      - For each column, read from top to bottom\n      - Example reading order:\n      ```\n      O R L D X X\n      H E L L O W\n      ↓ ↓ ↓ ↓ ↓ ↓\n      3 1 5 2 6 4\n      ```\n\n4. Final Result:\n   - Combine all processed chunks in order\n   - No spaces between chunks',
                'difficulty': 4,
                'encrypt_func': 'permuted_matrix_encrypt_2x6',
                'encrypted_message': self.permuted_matrix_encrypt_2x6('Rue de Rivoli')
            },
            {
                'challenge_id': '1',
                'stage': 'coordinates',
                'answer': 'DHHEFFXBCEBBX',
                'encryption_type': 'ADFGVX Cipher',
                'hint': 'First convert numbers to letters (A=1, B=2, etc.), then use the ADFGVX cipher with key square "PHQGIUMEAYLNOFDXJKRCVSTZWB0123456789" and keyword "FINAL".',
                'tutorial': 'This challenge uses a two-step process:\n\n1. First Conversion (Numbers to Letters):\n   - Convert each digit to its corresponding letter (A=1, B=2, etc.)\n   - Replace N and E with X\n   - Example: "488566N23522E" becomes "DHHEFFXBCEBBX"\n   - IMPORTANT: Your final answer should be in this letter-converted format\n   - For example, if your coordinates are "485N23E", you should input "DHEXBCX"\n\n2. ADFGVX Cipher:\n   a) Key Square (6x6):\n      ```\n      P H Q G I U\n      M E A Y L N\n      O F D X J K\n      R C V S T Z\n      W B 0 1 2 3\n      4 5 6 7 8 9\n      ```\n   b) Keyword: "FINAL"\n\n3. Encryption Process:\n   a) For each character in the converted text:\n      - Find its position in the key square\n      - Replace it with two letters:\n        * First letter: row label (A,D,F,G,V,X)\n        * Second letter: column label (A,D,F,G,V,X)\n   b) Arrange the resulting pairs under the keyword "FINAL"\n   c) Read columns in alphabetical order of the keyword letters\n\n4. Example:\n   - Converted text: "DHHEFFXBCEBBX"\n   - Each character is replaced by two letters from A,D,F,G,V,X\n   - These pairs are arranged under FINAL\n   - Columns are read in order: A(1),F(2),I(3),L(4),N(5)\n\nRemember: When you solve this challenge, you should input your answer in the letter-converted format (like "DHHEFFXBCEBBX"), not the original coordinates or the ADFGVX encrypted text.',
                'difficulty': 5,
                'encrypt_func': 'adfgvx_encrypt',
                'encrypted_message': self.adfgvx_encrypt('DHHEFFXBCEBBX')  # Input is already in letter format
            }
        ]

        # Clear existing data
        GameSetup.objects.all().delete()

        # Create new entries
        for setup in game_setups:
            GameSetup.objects.create(**setup)

        self.stdout.write(self.style.SUCCESS('Successfully populated GameSetup table')) 