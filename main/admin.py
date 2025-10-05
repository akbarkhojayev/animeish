from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin, TabularInline
from unfold.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm
from .models import User as CustomUser, Genre, Movie, VideoSource, Rating, Review, Bookmark, Episode, Banner

admin.site.unregister(Group)

@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Shaxsiy ma’lumotlar', {'fields': ('first_name', 'email', 'is_premium')}),
        ('Faollik', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Muhim sanalar', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_premium', 'is_staff',
                       'is_superuser'),
        }),
    )

    list_display = ("username", "email", "is_premium", "is_staff")
    list_filter = ("is_premium", "is_staff", "is_superuser")
    search_fields = ("username", "email")

@admin.register(Genre)
class GenreAdmin(ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

class VideoSourceInline(TabularInline):
    model = VideoSource
    extra = 1

class EpisodeInline(TabularInline):
    model = Episode
    extra = 1
    fields = ("season", "episode_number", "title", "video_url", "duration", "release_date")
    ordering = ("season", "episode_number")
    show_change_link = True

@admin.register(Movie)
class MovieAdmin(ModelAdmin):
    list_display = (
        "title", "type", "release_year",
        "rating_avg", "rating_count",
        "get_duration", "created_at", "poster_preview"
    )
    list_filter = ("type", "release_year", "genres")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [VideoSourceInline, EpisodeInline]
    filter_horizontal = ("genres",)

    def poster_preview(self, obj):
        if obj.poster:
            return f"<img src='{obj.poster.url}' width='60' height='90' style='object-fit:cover;' />"
        return "❌"
    poster_preview.allow_tags = True
    poster_preview.short_description = "Poster"

    def get_duration(self, obj):
        if obj.type == 'movie':
            return obj.duration
        elif obj.type == 'series':
            from datetime import timedelta
            total = timedelta()
            for ep in obj.episodes.all():
                if ep.duration:
                    total += ep.duration
            return total
    get_duration.short_description = "Duration"


@admin.register(VideoSource)
class VideoSourceAdmin(ModelAdmin):
    list_display = ("movie", "quality", "url")
    list_filter = ("quality",)
    search_fields = ("movie__title",)

@admin.register(Rating)
class RatingAdmin(ModelAdmin):
    list_display = ("user", "movie", "score", "created_at")
    list_filter = ("score", "created_at")
    search_fields = ("user__username", "movie__title")

@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ("user", "movie", "short_body", "created_at")
    search_fields = ("user__username", "movie__title", "body")
    list_filter = ("created_at",)

    def short_body(self, obj):
        return obj.body[:50] + ("..." if len(obj.body) > 50 else "")
    short_body.short_description = "Sharh"

@admin.register(Bookmark)
class BookmarkAdmin(ModelAdmin):
    list_display = ("user", "movie", "created_at")
    search_fields = ("user__username", "movie__title")
    list_filter = ("created_at",)

@admin.register(Banner)
class BannerAdmin(ModelAdmin):
    list_display = ("movie__title",)

