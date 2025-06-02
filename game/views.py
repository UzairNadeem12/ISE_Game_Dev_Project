from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import logout
from django.db.models import Q
from .models import GameSession, GameHistory, StageHistory, GameSetup, GameAdmin
from datetime import datetime, timedelta
import json
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def custom_logout(request):
    logout(request)
    return redirect('game:login')

class CustomLoginView(LoginView):
    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse('admin:index')
        return reverse('game:user_profile')

def landing_page(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin:index')
        return redirect('game:user_profile')
    return render(request, 'game/landing.html')

@login_required
def user_profile(request):
    # Update lives_lost for any current incomplete session before showing history
    for session in GameSession.objects.filter(user=request.user, completed=False):
        if session.game_history and not session.game_history.completed:
            session.game_history.lives_lost = 3 - session.lives
            session.game_history.save()
    game_history = GameHistory.objects.filter(user=request.user).order_by('-start_time')
    stage_history = StageHistory.objects.filter(game_history__in=game_history).order_by('game_history__start_time', 'stage')
    return render(request, 'game/user.html', {'game_history': game_history, 'stage_history': stage_history})

def select_challenge(request):
    """View for selecting a challenge before starting the game."""
    if not request.user.is_authenticated:
        return redirect('login')
    challenges = GameAdmin.objects.all().order_by('challenge_no')
    return render(request, 'game/select_challenge.html', {'challenges': challenges})

def game_home(request):
    """View for the game home page."""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get the selected challenge ID from the query parameters
    challenge_id = request.GET.get('challenge', '1')
    
    # Check if the challenge exists
    if not GameSetup.objects.filter(challenge_id=challenge_id).exists():
        messages.error(request, 'Invalid challenge selected.')
        return redirect('game:select_challenge')
    
    # Delete any existing incomplete game sessions for this user
    GameSession.objects.filter(user=request.user, completed=False).delete()
    
    # Always start a new game session at 'continent'
    game_history = GameHistory.objects.create(
        user=request.user,
        challenge_id=challenge_id
    )
    game_session = GameSession.objects.create(
        user=request.user,
        current_stage='continent',
        lives=3,
        game_history=game_history
    )
    StageHistory.objects.create(
        game_history=game_history,
        stage='continent',
        encryption_type=GameSetup.objects.get(challenge_id=challenge_id, stage='continent').encryption_type
    )
    
    # Debug output
    print(f"[DEBUG] challenge_id: {challenge_id}")
    print(f"[DEBUG] current_stage: {game_session.current_stage}")
    exists = GameSetup.objects.filter(challenge_id=challenge_id, stage=game_session.current_stage).exists()
    print(f"[DEBUG] GameSetup exists for this combo: {exists}")
    print(f"[DEBUG] current_challenge: {GameSetup.objects.filter(challenge_id=challenge_id, stage=game_session.current_stage).first()}")
    
    current_challenge = GameSetup.objects.filter(challenge_id=challenge_id, stage=game_session.current_stage).first()
    
    context = {
        'game_session': game_session,
        'current_challenge': current_challenge,
        'challenge_id': challenge_id
    }
    return render(request, 'game/home.html', context)

@login_required
@require_POST
def check_answer(request):
    """View for checking the answer."""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        answer = data.get('answer', '').strip()
        challenge_id = data.get('challenge_id', '1')
        
        # Get the current game session
        game_session = GameSession.objects.get(user=request.user, completed=False)
        
        # Get the current stage's game setup
        current_challenge = GameSetup.objects.get(challenge_id=challenge_id, stage=game_session.current_stage)
        
        # Check if the answer is correct
        if answer.lower() == current_challenge.answer.lower():
            # Update StageHistory for the current stage
            current_stage_history = StageHistory.objects.filter(
                game_history=game_session.game_history,
                stage=game_session.current_stage
            ).first()
            if current_stage_history and not current_stage_history.end_time:
                current_stage_history.end_time = timezone.now()
                current_stage_history.calculate_time_taken()
                current_stage_history.save()
            # Get the next stage
            stages = [stage[0] for stage in GameSession.STAGES]
            current_index = stages.index(game_session.current_stage)
            
            if current_index < len(stages) - 1:
                next_stage = stages[current_index + 1]
                game_session.current_stage = next_stage
                game_session.save()
                
                # Get the next stage's game setup
                next_challenge = GameSetup.objects.get(challenge_id=challenge_id, stage=next_stage)
                
                # Create stage history for the next stage
                StageHistory.objects.create(
                    game_history=game_session.game_history,
                    stage=next_stage,
                    encryption_type=next_challenge.encryption_type
                )
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Correct answer! Moving to next stage.',
                    'next_stage': next_stage,
                    'next_challenge': {
                        'encrypted_message': next_challenge.encrypted_message,
                        'encryption_type': next_challenge.encryption_type,
                        'tutorial': next_challenge.tutorial,
                        'hint': next_challenge.hint,
                        'difficulty': next_challenge.difficulty
                    }
                })
            else:
                # Game completed
                game_session.completed = True
                game_session.save()
                
                # Update StageHistory for the last stage
                current_stage_history = StageHistory.objects.filter(
                    game_history=game_session.game_history,
                    stage=game_session.current_stage
                ).first()
                if current_stage_history and not current_stage_history.end_time:
                    current_stage_history.end_time = timezone.now()
                    current_stage_history.calculate_time_taken()
                    current_stage_history.save()
                
                # Update game history
                game_history = game_session.game_history
                game_history.completed = True
                game_history.end_time = timezone.now()
                game_history.calculate_total_time()
                game_history.won = True
                game_history.lives_lost = 3 - game_session.lives
                game_history.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Congratulations! You have completed the game!',
                    'completed': True,
                    'redirect': reverse('game:game_win')
                })
        else:
            # Wrong answer
            game_session.lives -= 1
            game_session.save()
            
            if game_session.lives <= 0:
                # Game over
                game_session.completed = True
                game_session.save()
                
                # Update game history
                game_history = game_session.game_history
                game_history.completed = True
                game_history.end_time = timezone.now()
                game_history.calculate_total_time()
                game_history.won = False
                game_history.lives_lost = 3
                game_history.save()
                
                return JsonResponse({
                    'status': 'game_over',
                    'message': 'Game Over!',
                    'redirect': reverse('game:game_over')
                })
            
            return JsonResponse({
                'status': 'error',
                'message': 'Wrong answer! Try again.',
                'lives_remaining': game_session.lives
            })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def game_over(request):
    """View for the game over screen."""
    return render(request, 'game/game_over.html')

@login_required
def game_win(request):
    """View for the game win screen."""
    return render(request, 'game/game_win.html')

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ('username', 'password1', 'password2')

def signup(request):
    """View for user registration."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('game:user_profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'game/signup.html', {'form': form})
