from rest_framework import serializers
from main.models import *
from django.db import models

class UserProgressSerializer(serializers.ModelSerializer):
    watched_episodes_count = serializers.SerializerMethodField()
    total_watched_hours = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["watched_episodes_count", "total_watched_hours"]

    def get_watched_episodes_count(self, obj):
        return obj.episode_progress.count()

    def get_total_watched_hours(self, obj):
        total_minutes = obj.episode_progress.aggregate(
            total=models.Sum("watched_minutes")
        )["total"] or 0
        return round(total_minutes / 60, 2)

class UserSerializer(serializers.ModelSerializer):
    progress = UserProgressSerializer(source="*", read_only=True)

    class Meta:
        model = User
        fields = ("id", "first_name", "username", "email", "is_premium", "created_at", "progress")
        read_only_fields = ("id", "is_premium", "created_at", "progress")


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

class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = [
            "id", "season", "episode_number", "title", "description",
            "release_date", "video_url","duration"
        ]

class RatingNestedSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    class Meta:
        model = Rating
        fields = ["id", "user", "first_name","score", "comment","is_comment","created_at"]


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    episodes = EpisodeSerializer(many=True, read_only=True)
    ratings = RatingNestedSerializer(many=True, read_only=True)
    rating_avg = serializers.SerializerMethodField()
    rating_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Movie
        fields = [
            "id", "title", "slug", "description", "type", "release_year",
            "poster", "rating_avg", "rating_count", "genres",
            "episodes", "ratings",
        ]

    def get_rating_avg(self, obj):
        # .1f formatda yaxlitlab float sifatida qaytaradi
        return float(format(obj.rating_avg or 0, ".1f"))


class RatingSerializer(serializers.ModelSerializer):
    user_first_name = serializers.CharField(source="user.first_name", read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        source="movie", queryset=Movie.objects.all(), write_only=True
    )

    class Meta:
        model = Rating
        fields = ["id", "user",'user_first_name',"movie_id", "score", 'comment', "is_comment","created_at"]

    def validate_score(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Reyting faqat 1 dan 5 gacha bo‘lishi kerak.")
        return value

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
    first_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Parollar mos emas!'})
        return attrs

class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ConfirmPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=6)

class NotificationSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source="movie.title", read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "message", "movie_title", "is_read", "created_at"]