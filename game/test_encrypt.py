import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'v6.settings')
django.setup()

from game.models import permuted_matrix_encrypt_2x6

def test_permuted_matrix():
    test_input = "HELLO WORLD"
    result = permuted_matrix_encrypt_2x6(test_input)
    print(f"Input: {test_input}")
    print(f"Output: {result}")
    print(f"Expected: LLOHXORXEWDL")
    print(f"Match: {result == 'LLOHXORXEWDL'}")

if __name__ == "__main__":
    test_permuted_matrix() 