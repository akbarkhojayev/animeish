from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django import forms
from .models import User as CustomUser, Genre, Movie, Rating, Bookmark, Episode, Banner, UserEpisodeProgress, Notification
import tempfile


# Social Accounts
from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
admin.site.unregister(SocialApp)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialToken)

# JWT Token Blacklist
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
admin.site.unregister(OutstandingToken)
admin.site.unregister(BlacklistedToken)

from django.contrib import admin
from rest_framework.authtoken.models import Token

try:
    admin.site.unregister(Token)
except admin.sites.NotRegistered:
    pass

# ---------------------------
# Group adminni olib tashlash
# ---------------------------
admin.site.unregister(Group)

# ---------------------------
# Custom User Admin
# ---------------------------
@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Shaxsiy ma\'lumotlar', {'fields': ('first_name', 'email', 'is_premium')}),
        ('Faollik', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Muhim sanalar', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_premium', 'is_staff', 'is_superuser'),
        }),
    )

    list_display = ("username", "email", "is_premium", "is_staff")
    list_filter = ("is_premium", "is_staff", "is_superuser")
    search_fields = ("username", "email")

# ---------------------------
# Genre Admin
# ---------------------------
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

# ---------------------------
# Episode Inline
# ---------------------------
class EpisodeInlineForm(forms.ModelForm):
    file = forms.FileField(required=False, label="Video fayl")

    class Meta:
        model = Episode
        fields = "__all__"

    def save(self, commit=True):
        instance = super().save(commit=False)
        file_obj = self.cleaned_data.get("file")

        if file_obj:
            # Faylni vaqtincha saqlash
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                for chunk in file_obj.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            # Video yuklash funksiyasini chaqirish
            title = instance.title or f"{instance.movie.title} S{instance.season}E{instance.episode_number}"

            try:
                from .tasks import upload_video
                video_url = upload_video(tmp_path, title)
                instance.video_url = video_url
                print(f"✅ Video muvaffaqiyatli yuklandi: {video_url}")
            except Exception as e:
                # Agar xatolik yuz bersa, batafsil xabar ko'rsatish
                import uuid
                import traceback
                task_id = str(uuid.uuid4())
                error_msg = f"Upload xatolik: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
                instance.video_url = f"❌ {error_msg} (Task ID: {task_id})"
                print(f"❌ Video yuklanishda xatolik: {e}")

        if commit:
            instance.save()
        return instance

class EpisodeInline(admin.StackedInline):
    model = Episode
    form = EpisodeInlineForm
    extra = 1
    ordering = ("season", "episode_number")
    fields = (
        "season",
        "episode_number",
        "title",
        "video_url",
        "file",
        "quality",
        "duration",
        "release_date"
    )

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "release_year", "rating_avg", "rating_count", "created_at", "poster_preview")
    list_filter = ("type", "release_year", "genres")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("genres",)
    inlines = [EpisodeInline]

    def poster_preview(self, obj):
        if obj.poster:
            return format_html(
                "<img src='{}' width='60' height='90' style='object-fit:cover;border-radius:6px;' />",
                obj.poster.url
            )
        return "❌"
    poster_preview.short_description = "Poster"

# ---------------------------
# Rating Admin
# ---------------------------
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("user", "movie", "score", "comment", "created_at")
    list_filter = ("score", "created_at")
    search_fields = ("user__username", "movie__title")

# ---------------------------
# Bookmark Admin
# ---------------------------
@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "movie", "created_at")
    search_fields = ("user__username", "movie__title")
    list_filter = ("created_at",)

# ---------------------------
# Banner Admin
# ---------------------------
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("movie_title",)

    def movie_title(self, obj):
        return obj.movie.title
    movie_title.short_description = "Movie"

# ---------------------------
# UserEpisodeProgress Admin
# ---------------------------
@admin.register(UserEpisodeProgress)
class UserEpisodeProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "episode", "watched_minutes")
    search_fields = ("user__username", "episode__title", "episode__movie__title")
    list_filter = ("watched_minutes",)

# ---------------------------
# Notification Admin
# ---------------------------
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "movie", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "message")
    actions = ["mark_as_read", "mark_as_unread"]

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Belgilangan xabarlarni o'qilgan deb belgilash"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Belgilangan xabarlarni o'qilmagan deb belgilash"
