from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Movie, Notification, User

@receiver(post_save, sender=Movie)
def create_movie_notification(sender, instance, created, **kwargs):
    if created:
        users = User.objects.all()  # agar faqat premium foydalanuvchilarga bo‘lsin: .filter(is_premium=True)
        for user in users:
            Notification.objects.create(
                user=user,
                message=f"Yangi film qo‘shildi: {instance.title}",
                movie=instance
            )
