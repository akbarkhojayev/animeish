from rest_framework import serializers
from main.models import User, Genre, Movie, Episode, VideoSource, Rating, Review, Bookmark

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "avatar", "bio", "is_premium", "created_at")
        read_only_fields = ("id", "is_premium", "created_at")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data.get("email", "")
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name", "slug"]

class VideoSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoSource
        fields = ["id", "url", "quality", "is_trailer"]

class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = [
            "id", "season", "episode_number", "title", "description",
            "release_date", "video_url","duration"
        ]

class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    videos = VideoSourceSerializer(many=True, read_only=True)
    episodes = EpisodeSerializer(many=True, read_only=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            "id", "title", "slug", "description", "type", "release_year",
            "poster", "rating_avg", "rating_count", "genres",
            "videos", "episodes", "duration"
        ]

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


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        source="movie", queryset=Movie.objects.all(), write_only=True
    )

    class Meta:
        model = Rating
        fields = ["id", "user", "movie_id", "score", "created_at"]

    def validate_score(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Reyting faqat 1 dan 5 gacha bo‘lishi kerak.")
        return value

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        source="movie", queryset=Movie.objects.all(), write_only=True
    )

    class Meta:
        model = Review
        fields = ["id", "user", "movie_id", "body", "created_at"]


class BookmarkSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        source="movie", queryset=Movie.objects.all(), write_only=True
    )

    class Meta:
        model = Bookmark
        fields = ["id", "movie", "movie_id", "created_at"]
