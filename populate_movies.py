from main.models import Genre, Movie, Episode
from datetime import timedelta, date

# ======================
# Genre yaratish
# ======================
genres = ["Action", "Comedy", "Drama", "Sci-Fi"]
genre_objs = []
for g in genres:
    obj, created = Genre.objects.get_or_create(name=g)
    genre_objs.append(obj)

# ======================
# Film yaratish
# ======================
movie1 = Movie.objects.create(
    title="Test Movie 1",
    description="Bu test uchun film 1.",
    type="movie",
    release_year=2023,
    duration=timedelta(minutes=120)
)
movie1.genres.set(genre_objs[:2])

movie2 = Movie.objects.create(
    title="Test Movie 2",
    description="Bu test uchun film 2.",
    type="movie",
    release_year=2024,
    duration=timedelta(minutes=95)
)
movie2.genres.set(genre_objs[1:3])

# ======================
# Serial yaratish
# ======================
series1 = Movie.objects.create(
    title="Test Series 1",
    description="Bu test uchun serial 1.",
    type="series",
    release_year=2022
)
series1.genres.set(genre_objs[:3])

# Episode qo‘shish
Episode.objects.create(
    movie=series1,
    season=1,
    episode_number=1,
    title="Episode 1",
    description="Birinchi epizod",
    release_date=date(2022, 1, 1),
    duration=timedelta(minutes=45)
)

Episode.objects.create(
    movie=series1,
    season=1,
    episode_number=2,
    title="Episode 2",
    description="Ikkinchi epizod",
    release_date=date(2022, 1, 8),
    duration=timedelta(minutes=50)
)

Episode.objects.create(
    movie=series1,
    season=2,
    episode_number=1,
    title="Episode 1",
    description="Ikkinchi mavsum birinchi epizod",
    release_date=date(2023, 2, 1),
    duration=timedelta(minutes=55)
)

print("Test ma’lumotlar qo‘shildi!")
