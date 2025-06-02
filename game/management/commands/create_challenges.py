from django.core.management.base import BaseCommand
from game.models import Challenge
from game.utils import (
    caesar_encrypt,
    binary_ascii_encrypt,
    rot13_encrypt,
    decimal_ascii_encrypt,
    number_to_letter_encrypt,
    atbash_encrypt,
    vigenere_encrypt,
    morse_code_encrypt,
    rail_fence_encrypt,
    columnar_transposition_encrypt,
    permuted_matrix_encrypt,
    binary_columnar_encrypt,
    adfgvx_encrypt
)

class Command(BaseCommand):
    help = 'Creates sample challenges for the treasure hunt game'

    def handle(self, *args, **kwargs):
        # First, delete all existing challenges
        Challenge.objects.all().delete()
        
        # Define the challenges with their answers
        challenges = [
            {
                'stage': 'continent',
                'answer': 'Europe',
                'encryption_type': 'Decimal ASCII',
                'hint': 'Convert each number to its ASCII character',
                'tutorial': 'ASCII codes can be represented in decimal. Each number corresponds to a character. For example, 65 is the ASCII code for A, 66 for B, and so on.',
                'difficulty': 1,
                'encrypt_func': decimal_ascii_encrypt
            },
            {
                'stage': 'country',
                'answer': 'France',
                'encryption_type': 'Caesar Cipher (Shift + 13)',
                'hint': 'Each letter is shifted thirteen positions forward in the alphabet',
                'tutorial': 'In a Caesar cipher, each letter in the plaintext is shifted a certain number of positions down the alphabet. For example, with a shift of 2, A becomes C, B becomes D, and so on.',
                'difficulty': 2,
                'encrypt_func': lambda x: caesar_encrypt(x, shift=13)
            },
            {
                'stage': 'region',
                'answer': 'North',
                'encryption_type': 'Atbash Cipher',
                'hint': 'Each letter is mapped to its reverse in the alphabet (A=Z, B=Y...)',
                'tutorial': 'The Atbash cipher is a substitution cipher where each letter is mapped to its reverse in the alphabet. For example, A becomes Z, B becomes Y, and so on.',
                'difficulty': 2,
                'encrypt_func': atbash_encrypt
            },
            {
                'stage': 'city',
                'answer': 'Paris',
                'encryption_type': 'Vigenère Cipher (key: RAT)',
                'hint': 'Each letter is shifted according to a keyword',
                'tutorial': 'The Vigenère cipher uses a keyword to determine the shift for each letter. The keyword is repeated to match the length of the message. Each letter in the keyword determines how many positions to shift the corresponding letter in the message.',
                'difficulty': 3,
                'encrypt_func': lambda x: vigenere_encrypt(x, 'RAT')
            },
            {
                'stage': 'district',
                'answer': 'Le Marais',
                'encryption_type': 'Rail Fence Cipher (3 rails)',
                'hint': 'The text is arranged in a zigzag pattern on 3 rails and read off horizontally',
                'tutorial': 'In a Rail Fence cipher, the text is written in a zigzag pattern across 3 rails (rows) and then read off row by row. For example, "HELLO" with 3 rails becomes:\nH   O\nE L\nL\nWhich is then read as "HOELL"',
                'difficulty': 3,
                'encrypt_func': lambda x: rail_fence_encrypt(x, rails=3)
            },
            {
                'stage': 'area',
                'answer': 'Marais',
                'encryption_type': 'Columnar Transposition (key: RAT)',
                'hint': 'The text is written in columns under the key word RAT, then read off based on alphabetical order of the key letters',
                'tutorial': 'In a Columnar Transposition cipher, the text is written under a keyword (RAT) and read off in columns based on the alphabetical order of the key letters. For example, with RAT:\nR A T\nh e l\nl l o\nThe columns are read in order A(1), R(2), T(3), giving: "elhlol"',
                'difficulty': 4,
                'encrypt_func': lambda x: columnar_transposition_encrypt(x, 'RAT')
            },
            {
                'stage': 'street',
                'answer': 'Rue de Rivoli',
                'encryption_type': 'Matrix Transposition (2x6 matrix with permutations)',
                'hint': 'To decrypt: The text was encrypted using a 2x6 matrix with row permutation [2,1] and column permutation [3,1,5,2,6,4]. Arrange the encrypted text in a matrix and reverse these permutations to reveal the answer.',
                'tutorial': 'In this cipher:\n1. Remove spaces from the encrypted text\n2. Arrange the text in a 2x6 matrix\n3. For example, "HELLO WORLD" would become:\n```\nH E L L O W\nO R L D X X\n```\n4. Apply row permutation [2,1] (second row becomes first)\n5. Apply column permutation [3,1,5,2,6,4]\n6. Read down the columns to get the result',
                'difficulty': 4,
                'encrypt_func': lambda x: permuted_matrix_encrypt(x, [2,1], [3,1,5,2,6,4])
            },
            {
                'stage': 'coordinates',
                'answer': 'DHHEFFXBCEBBX',  # 488566N23522E converted using the special key
                'encryption_type': 'ADFGVX Cipher',
                'hint': 'The coordinates were first converted using this special key: A=1, B=2, C=3, etc., but N and E are both represented as X. For example, "485N23E" becomes "DHEXBCX". The encrypted text was created by applying the ADFGVX cipher to this converted text.',
                'tutorial': 'This challenge uses the ADFGVX cipher with a special letter conversion first:\n1. The original coordinates were converted using this key:\n   - A=1, B=2, C=3, D=4, E=5, F=6, G=7, H=8, I=9, J=10, K=11, L=12, M=13\n   - N and E are both represented as X\n   For example:\n   - "485N23E" becomes "DHEXBCX"\n   - "488566N23522E" becomes "DHHEFFXBCEBBX"\n2. Then, this converted text was encrypted using the ADFGVX cipher:\n   - Each character is replaced by two letters (from A,D,F,G,V,X) based on its position in the key square\n   - The resulting pairs are arranged under the keyword FINAL and read off in columns based on alphabetical order (A=1,F=2,I=3,L=4,N=5)\nTo decrypt:\n1. Arrange the ciphertext under FINAL\n2. Read rows to get the pairs of letters\n3. Use the key square to convert pairs back to original characters\n4. The result will be the converted text using our special key (where N and E are X)',
                'difficulty': 5,
                'encrypt_func': adfgvx_encrypt
            }
        ]

        # Create new challenges
        for challenge_data in challenges:
            # Generate encrypted message using the corresponding encryption function
            encrypted_message = challenge_data['encrypt_func'](challenge_data['answer'])
            
            # Debug output for coordinates stage
            if challenge_data['stage'] == 'coordinates':
                print(f"Debug - Coordinates stage:")
                print(f"Original text: {challenge_data['answer']}")
                print(f"Encrypted message (len={len(encrypted_message)}): {encrypted_message}")
                print(f"Encrypted bytes: {[ord(c) for c in encrypted_message]}")
            
            # Remove the encryption function from the data before saving
            challenge_data = {k: v for k, v in challenge_data.items() if k != 'encrypt_func'}
            challenge_data['encrypted_message'] = encrypted_message
            
            # Create new challenge
            Challenge.objects.create(**challenge_data)

        self.stdout.write(self.style.SUCCESS('Successfully created sample challenges with new encrypted messages')) 