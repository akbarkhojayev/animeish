from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import Movie, Rating, Episode, Genre

# Custom User modelini olish
User = get_user_model()

def dashboard_callback(request, context):
    """
    Jazzmin uchun dashboard callback funksiyasi
    """
    print("🎯 Dashboard callback CHAQRILDI!")
    print(f"📋 Request path: {request.path}")
    print(f"📋 Context keys oldin: {list(context.keys())}")

    # Asosiy statistikalar
    total_movies = Movie.objects.count()
    total_users = User.objects.count()
    total_episodes = Episode.objects.count()
    total_genres = Genre.objects.count()

    print(f"📊 Statistika hisoblandi:")
    print(f"  - Jami filmlar: {total_movies}")
    print(f"  - Jami foydalanuvchilar: {total_users}")
    print(f"  - Jami epizodlar: {total_episodes}")
    print(f"  - Jami janrlar: {total_genres}")

    # So'nggi 30 kun ichida qo'shilgan filmlar
    last_30_days = timezone.now() - timedelta(days=30)
    recent_movies = Movie.objects.filter(created_at__gte=last_30_days).count()

    # O'rtacha reyting
    avg_rating = Rating.objects.aggregate(Avg('score'))['score__avg'] or 0

    # Eng ko'p reytingga ega filmlar
    top_movies = Movie.objects.annotate(
        ratings_count=Count('ratings')
    ).filter(ratings_count__gt=0).order_by('-ratings_count')[:5]

    # Eng ko'p ko'rilgan janrlar
    top_genres = Genre.objects.annotate(
        movie_count=Count('movies')
    ).order_by('-movie_count')[:10]

    updated_context = {
        'total_movies': total_movies,
        'total_users': total_users,
        'total_episodes': total_episodes,
        'total_genres': total_genres,
        'recent_movies': recent_movies,
        'avg_rating': round(avg_rating, 1),
        'top_movies': top_movies,
        'top_genres': top_genres,
    }

    print(f"📋 Context yaratildi: {list(updated_context.keys())}")
    print(f"📋 Qiymatlar: total_movies={total_movies}, total_users={total_users}")

    context.update(updated_context)

def dashboard_context(request):
    """
    Django context processor - har bir template uchun dashboard ma'lumotlarini qo'shadi
    """
    # Faqat admin sahifalar uchun
    if request.path.startswith('/admin/'):
        context = {}

        # Asosiy statistikalar
        total_movies = Movie.objects.count()
        total_users = User.objects.count()
        total_episodes = Episode.objects.count()
        total_genres = Genre.objects.count()

        # So'nggi 30 kun ichida qo'shilgan filmlar
        last_30_days = timezone.now() - timedelta(days=30)
        recent_movies = Movie.objects.filter(created_at__gte=last_30_days).count()

        # O'rtacha reyting
        avg_rating = Rating.objects.aggregate(Avg('score'))['score__avg'] or 0

        # Eng ko'p reytingga ega filmlar
        top_movies = Movie.objects.annotate(
            ratings_count=Count('ratings')
        ).filter(ratings_count__gt=0).order_by('-ratings_count')[:5]

        # Eng ko'p ko'rilgan janrlar
        top_genres = Genre.objects.annotate(
            movie_count=Count('movies')
        ).order_by('-movie_count')[:10]

        context.update({
            'total_movies': total_movies,
            'total_users': total_users,
            'total_episodes': total_episodes,
            'total_genres': total_genres,
            'recent_movies': recent_movies,
            'avg_rating': round(avg_rating, 1),
            'top_movies': top_movies,
            'top_genres': top_genres,
        })

        return context

    return {}