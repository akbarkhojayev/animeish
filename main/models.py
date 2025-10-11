from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Avg
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    first_name = models.CharField(max_length=150, verbose_name=_("Ism"))
    is_premium = models.BooleanField(default=False, verbose_name=_("Premium"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Yaratilgan vaqt"))

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _("Foydalanuvchi")
        verbose_name_plural = _("Foydalanuvchilar")

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Nom"))
    slug = models.SlugField(max_length=120, unique=True, blank=True, verbose_name=_("Slug"))

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

    title = models.CharField(max_length=255, verbose_name=_("Sarlavha"))
    slug = models.SlugField(max_length=300, unique=True, blank=True, verbose_name=_("Slug"))
    description = models.TextField(blank=True, verbose_name=_("Tavsif"))
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=MOVIE, verbose_name=_("Turi"))
    release_year = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("Chiqish yili"))
    poster = models.ImageField(upload_to='posters/', blank=True, null=True, verbose_name=_("Poster"))
    genres = models.ManyToManyField(Genre, related_name='movies', blank=True, verbose_name=_("Janrlar"))
    rating_avg = models.FloatField(default=0.0, verbose_name=_("O'rtacha reyting"))
    rating_count = models.PositiveIntegerField(default=0, verbose_name=_("Reytinglar soni"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Yaratilgan vaqt"))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Film")
        verbose_name_plural = _("Filmlar")

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
    photo = models.ImageField(upload_to='banners/', blank=True, null=True, verbose_name=_("Rasm"))
    movie = models.ForeignKey(Movie, related_name='banners', on_delete=models.CASCADE, verbose_name=_("Film"))

    def __str__(self):
        return self.movie.title

    class Meta:
        verbose_name = _("Banner")
        verbose_name_plural = _("Bannerlar")

class Episode(models.Model):
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="episodes",
        verbose_name=_("Film")
    )
    season = models.PositiveIntegerField(default=1, verbose_name=_("Mavsum"))
    episode_number = models.PositiveIntegerField(verbose_name=_("Epizod raqami"))
    title = models.CharField(max_length=255, blank=True, verbose_name=_("Sarlavha"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Tavsif"))
    video_url = models.CharField(max_length=500, blank=True, null=True, verbose_name=_("Video URL"))
    quality = models.CharField(max_length=50, blank=True, verbose_name=_("Sifat"))
    release_date = models.DateField(blank=True, null=True, verbose_name=_("Chiqish sanasi"))
    duration = models.DurationField(blank=True, null=True, verbose_name=_("Davomiyligi"))

    class Meta:
        unique_together = ("movie", "season", "episode_number")
        ordering = ["season", "episode_number"]
        verbose_name = _("Epizod")
        verbose_name_plural = _("Epizodlar")

    def __str__(self):
        return f"{self.movie.title} S{self.season}E{self.episode_number}"

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings', verbose_name=_("Foydalanuvchi"))
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings', verbose_name=_("Film"))
    score = models.PositiveSmallIntegerField(verbose_name=_("Baholash"))
    comment = models.TextField(blank=True, null=True, verbose_name=_("Izoh"))
    is_comment = models.BooleanField(default=False, verbose_name=_("Izoh mavjud"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Yaratilgan vaqt"))

    class Meta:
        unique_together = ('user', 'movie')
        verbose_name = _("Reyting")
        verbose_name_plural = _("Reytinglar")

    def save(self, *args, **kwargs):
        self.is_comment = bool(self.comment and self.comment.strip())
        super().save(*args, **kwargs)

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks', verbose_name=_("Foydalanuvchi"))
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='bookmarks', verbose_name=_("Film"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Yaratilgan vaqt"))

    class Meta:
        unique_together = ('user', 'movie')
        verbose_name = _("Saqlangan")
        verbose_name_plural = _("Saqlanganlar")

class UserEpisodeProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="episode_progress", verbose_name=_("Foydalanuvchi"))
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, verbose_name=_("Epizod"))
    watched_minutes = models.PositiveIntegerField(default=0, verbose_name=_("Ko'rilgan daqiqalar"))

    class Meta:
        unique_together = ("user", "episode")
        verbose_name = _("Epizod progresi")
        verbose_name_plural = _("Epizod progresslari")

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications", verbose_name=_("Foydalanuvchi"))
    message = models.CharField(max_length=255, verbose_name=_("Xabar"))
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True, verbose_name=_("Film"))
    is_read = models.BooleanField(default=False, verbose_name=_("O'qilgan"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Yaratilgan vaqt"))

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Xabarnoma")
        verbose_name_plural = _("Xabarnomalar")

    def __str__(self):
        return f"{self.user.username} - {self.message[:30]}"