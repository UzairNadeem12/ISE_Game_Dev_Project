from django.contrib import admin
from .models import GameSession, Challenge, GameHistory, GameSetup, GameAdmin

@admin.register(GameSetup)
class GameSetupAdmin(admin.ModelAdmin):
    list_display = ('challenge_id', 'stage', 'encryption_type', 'difficulty')
    list_filter = ('stage', 'encryption_type', 'difficulty')
    search_fields = ('challenge_id', 'stage', 'encryption_type')
    ordering = ('stage', 'difficulty')

@admin.register(GameHistory)
class GameHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_time', 'end_time', 'completed', 'final_stage', 'lives_lost', 'total_time')
    list_filter = ('completed', 'final_stage', 'start_time')
    search_fields = ('user__username', 'final_stage')
    readonly_fields = ('start_time', 'end_time', 'total_time')
    ordering = ('-start_time',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'lives', 'current_stage', 'created_at', 'completed')
    list_filter = ('completed', 'current_stage')
    search_fields = ('user__username', 'current_stage')
    readonly_fields = ('created_at',)
    actions = ['delete_selected']

    def delete_selected(self, request, queryset):
        # Delete the selected game sessions
        for game_session in queryset:
            game_session.delete()
        self.message_user(request, f"Successfully deleted {queryset.count()} game sessions and their associated history.")
    delete_selected.short_description = "Delete selected game sessions and their history"

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('stage', 'encryption_type', 'difficulty')
    list_filter = ('difficulty', 'encryption_type')
    search_fields = ('stage', 'encryption_type', 'answer')

@admin.register(GameAdmin)
class GameAdminAdmin(admin.ModelAdmin):
    list_display = ('challenge_no', 'continent', 'country', 'region', 'city', 'district', 'area', 'street', 'coordinates')
    search_fields = ('challenge_no', 'continent', 'country', 'city')
    ordering = ('challenge_no',)
