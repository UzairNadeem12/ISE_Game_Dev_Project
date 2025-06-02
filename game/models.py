from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from pycipher import Caesar, Atbash, Vigenere, Railfence, ColTrans, ADFGVX
import re

# Create your models here.

class GameSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lives = models.IntegerField(default=3)
    current_stage = models.CharField(max_length=50, default='continent')
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    game_history = models.ForeignKey('GameHistory', on_delete=models.SET_NULL, null=True, blank=True)

    STAGES = [
        ('continent', 'Continent'),
        ('country', 'Country'),
        ('region', 'Region'),
        ('city', 'City'),
        ('district', 'District'),
        ('area', 'Area'),
        ('street', 'Street'),
        ('coordinates', 'Coordinates'),
    ]

    def __str__(self):
        return f"{self.user.username}'s game session at {self.created_at}"

class StageHistory(models.Model):
    game_history = models.ForeignKey('GameHistory', on_delete=models.CASCADE, related_name='stages')
    stage = models.CharField(max_length=50)
    encryption_type = models.CharField(max_length=50)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    time_taken = models.DurationField(null=True, blank=True)

    def calculate_time_taken(self):
        if self.end_time:
            self.time_taken = self.end_time - self.start_time
            self.save()

    def __str__(self):
        return f"{self.stage} stage for {self.game_history}"

class GameHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    final_stage = models.CharField(max_length=50, default='continent')
    lives_lost = models.IntegerField(default=0)
    total_time = models.DurationField(null=True, blank=True)
    won = models.BooleanField(default=False)  # True if player won, False if lost, None/incomplete if not finished
    challenge_id = models.CharField(max_length=50, default='1')  # Store which challenge was played

    def calculate_total_time(self):
        if self.end_time:
            self.total_time = self.end_time - self.start_time
            self.save()

    def __str__(self):
        return f"{self.user.username}'s game on {self.start_time.strftime('%Y-%m-%d %H:%M')}"

class Challenge(models.Model):
    stage = models.CharField(max_length=50)
    encrypted_message = models.TextField()
    encryption_type = models.CharField(max_length=50)
    hint = models.TextField()
    tutorial = models.TextField()
    answer = models.CharField(max_length=255)
    difficulty = models.IntegerField(default=1)  # 1-5 scale

    class Meta:
        ordering = ['difficulty']

class GameAdmin(models.Model):
    challenge_no = models.IntegerField(unique=True)
    continent = models.CharField(max_length=250)
    country = models.CharField(max_length=250)
    region = models.CharField(max_length=250)
    city = models.CharField(max_length=250)
    district = models.CharField(max_length=250)
    area = models.CharField(max_length=250)
    street = models.CharField(max_length=250)
    coordinates = models.CharField(max_length=250)
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, help_text="Description of the challenge that will be shown in the selection menu")

    def __str__(self):
        return f"Challenge {self.challenge_no}: {self.continent} - {self.country}"

class GameSetup(models.Model):
    challenge_id = models.CharField(max_length=250)
    stage = models.CharField(max_length=250)
    answer = models.CharField(max_length=250)
    encryption_type = models.CharField(max_length=250)
    hint = models.CharField(max_length=250)
    tutorial = models.CharField(max_length=250)
    difficulty = models.IntegerField()
    encrypt_func = models.CharField(max_length=250)
    encrypted_message = models.CharField(max_length=250)
    game_admin = models.ForeignKey(GameAdmin, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.stage} - {self.encryption_type}"

    class Meta:
        unique_together = ('challenge_id', 'stage')

def decimal_ascii_encrypt(text):
    return ' '.join(str(ord(c)) for c in text)

def caesar_encrypt_shift_13(text):
    return Caesar(key=13).encipher(text)

def atbash_encrypt(text):
    return Atbash().encipher(text)

def vigenere_encrypt_RAT(text):
    return Vigenere(key='RAT').encipher(text)

def rail_fence_encrypt_3(text):
    return Railfence(key=3).encipher(text)

def columnar_transposition_encrypt_RAT(text):
    ct = ColTrans('RAT')
    return ct.encipher(text)

def permuted_matrix_encrypt_2x6(text):
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

def adfgvx_encrypt(text):
    key_square = 'PHQGIUMEAYLNOFDXJKRCVSTZWB0123456789'
    keyword = 'FINAL'
    cipher = ADFGVX(key_square, keyword)
    return cipher.encipher(text)

@receiver(post_save, sender=GameAdmin)
def create_game_setups(sender, instance, created, **kwargs):
    if created:
        # Get the template GameSetup entries (challenge_id = '1')
        template_setups = GameSetup.objects.filter(challenge_id='1')
        
        # Create new GameSetup entries for each stage
        for template in template_setups:
            # Get the corresponding answer from GameAdmin
            answer = getattr(instance, template.stage)
            
            # Get the encryption function
            encrypt_func = globals()[template.encrypt_func]
            
            # Create new GameSetup entry
            GameSetup.objects.create(
                challenge_id=str(instance.challenge_no),
                stage=template.stage,
                answer=answer,
                encryption_type=template.encryption_type,
                hint=template.hint,
                tutorial=template.tutorial,
                difficulty=template.difficulty,
                encrypt_func=template.encrypt_func,
                encrypted_message=encrypt_func(answer),
                game_admin=instance
            )
