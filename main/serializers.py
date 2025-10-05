from rest_framework import serializers
from main.models import User, Genre, Movie, Episode, VideoSource, Rating, Review, Bookmark, Banner


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "username", "is_premium", "created_at")
        read_only_fields = ("id", "is_premium", "created_at")


class CustomRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)
    email = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "first_name", "email", "password", "confirm_password")

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})

        username_or_email = attrs["email"]
        if "@" in username_or_email:
            if User.objects.filter(email=username_or_email).exists():
                raise serializers.ValidationError({"email": "Email already exists"})
        else:
            if User.objects.filter(username=username_or_email).exists():
                raise serializers.ValidationError({"username": "Username already exists"})

        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        username_or_email = validated_data.pop("email")

        if "@" in username_or_email:
            email = username_or_email
            username = email
        else:
            username = username_or_email
            email = None

        user = User(
            first_name=validated_data.get("first_name"),
            username=username,
            email=email
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "username",)
        extra_kwargs = {
            "username": {"required": False},
            "first_name": {"required": False},
        }

    def validate_username(self, value):
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name", "slug"]

class VideoSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoSource
        fields = ["id", "url", "quality"]

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

class BannerSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = Banner
        fields = "__all__"

class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.IntegerField()
    password = serializers.CharField(write_only=True, min_length=6)