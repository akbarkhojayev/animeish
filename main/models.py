from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Avg
from django.utils.text import slugify

class User(AbstractUser):
    first_name = models.CharField()
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Movie(models.Model):
    MOVIE = 'movie'
    SERIES = 'series'
    TYPE_CHOICES = [
        (MOVIE, 'Movie'),
        (SERIES, 'Series'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=MOVIE)
    release_year = models.PositiveIntegerField(blank=True, null=True)
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    genres = models.ManyToManyField(Genre, related_name='movies', blank=True)
    rating_avg = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def average_rating(self):
        avg = self.ratings.aggregate(Avg('score'))['score__avg']
        return avg if avg else 0


class Banner(models.Model):
    photo = models.ImageField(upload_to='banners/', blank=True, null=True)
    movie = models.ForeignKey(Movie, related_name='banners', on_delete=models.CASCADE)

    def __str__(self):
        return self.movie.title

class Episode(models.Model):
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="episodes"
    )
    season = models.PositiveIntegerField(default=1)
    episode_number = models.PositiveIntegerField()
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    quality = models.CharField(max_length=50, blank=True)
    release_date = models.DateField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)

    class Meta:
        unique_together = ("movie", "season", "episode_number")
        ordering = ["season", "episode_number"]

    def __str__(self):
        return f"{self.movie.title} S{self.season}E{self.episode_number}"

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    score = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True, null=True)
    is_comment = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')

    def save(self, *args, **kwargs):
        self.is_comment = bool(self.comment and self.comment.strip())
        super().save(*args, **kwargs)

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')

class UserEpisodeProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="episode_progress")
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    watched_minutes = models.PositiveIntegerField(default=0)
    class Meta:
        unique_together = ("user", "episode")

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.message[:30]}"