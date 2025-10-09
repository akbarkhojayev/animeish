from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count
from .models import Movie, Notification, User, Rating


@receiver(post_save, sender=Movie)
def create_movie_notification(sender, instance, created, **kwargs):
    if created:
        users = User.objects.all()
        for user in users:
            Notification.objects.create(
                user=user,
                message=f"Yangi film qo‘shildi: {instance.title}",
                movie=instance
            )

@receiver([post_save, post_delete], sender=Rating)
def update_movie_rating(sender, instance, **kwargs):
    movie = instance.movie
    agg = movie.ratings.aggregate(
        avg_score=Avg('score'),
        count=Count('id')
    )
    movie.rating_avg = round(agg['avg_score'] or 0, 1)  # 1 xonali songa yaxlitlash
    movie.rating_count = agg['count'] or 0
    movie.save()