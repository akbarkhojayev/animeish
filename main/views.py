from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from main.models import *
from main.serializers import *
from main.models import User as CustomUser, Movie, Review, Bookmark
from django.db.models import Avg
from django.utils.timezone import now
from datetime import timedelta
import json, random
from rest_framework.response import Response
from django.core.mail import send_mail
from rest_framework.generics import GenericAPIView
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomRegisterSerializer
    permission_classes = [AllowAny]

class UserUpdateView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class GenreListView(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]

class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all().prefetch_related("genres", "videos", "episodes")
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]

class MovieDetailView(generics.RetrieveAPIView):
    queryset = Movie.objects.all().prefetch_related("genres", "videos", "episodes")
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]

class VideoSourceListView(generics.ListAPIView):
    queryset = VideoSource.objects.all()
    serializer_class = VideoSourceSerializer
    permission_classes = [IsAuthenticated]

class EpisodeListView(generics.ListAPIView):
    serializer_class = EpisodeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        movie_id = self.kwargs.get("movie_id")
        return Episode.objects.filter(movie_id=movie_id)

class RatingListCreateView(generics.ListCreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BannerListView(generics.ListAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [IsAuthenticated]

class BookmarkListCreateView(generics.ListCreateAPIView):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

def dashboard_callback(request, context):
    total_users = CustomUser.objects.count()
    premium_users = CustomUser.objects.filter(is_premium=True).count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    total_movies = Movie.objects.count()
    total_reviews = Review.objects.count()
    total_bookmarks = Bookmark.objects.count()

    top_movies_qs = (
        Movie.objects
        .annotate(avg_score=Avg('ratings__score'))
        .order_by('-avg_score')[:5]
    )

    top_movies = [
        {"title": movie.title, "avg_rating": round(movie.avg_score or 0, 1)}
        for movie in top_movies_qs
    ]

    today = now().date()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    user_activity = []
    for d in last_7_days:
        count = CustomUser.objects.filter(last_login__date=d).count()
        user_activity.append({"date": d.strftime("%d-%m"), "count": count})

    context.update({
        "stats": {
            "total_users": total_users,
            "premium_users": premium_users,
            "active_users": active_users,
            "total_movies": total_movies,
            "total_reviews": total_reviews,
            "total_bookmarks": total_bookmarks,
        },
        "top_movies": top_movies,
        "user_activity": json.dumps(user_activity),
    })
    return context

OTP_STORE = {}


class SendOTPView(GenericAPIView):
    serializer_class = SendOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = random.randint(100000, 999999)
        OTP_STORE[email] = code

        send_mail(
            subject='Kirish kodi',
            message=f'Sizning kirish kodingiz: {code}',
            from_email='noreply@moviesite.com',
            recipient_list=[email],
        )

        return Response({'message': 'Tasdiqlash kodi emailga yuborildi!'}, status=status.HTTP_200_OK)


class VerifyOTPView(GenericAPIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        password = serializer.validated_data['password']

        if OTP_STORE.get(email) != code:
            return Response({'error': 'Noto‘g‘ri yoki eskirgan kod'}, status=status.HTTP_400_BAD_REQUEST)

        OTP_STORE.pop(email, None)

        user = User.objects.filter(email=email).first()

        if not user:
            user = User.objects.create(
                email=email,
                username=email,
                password=make_password(password),
            )
        else:
            if not check_password(password, user.password):
                return Response({'error': 'Parol noto‘g‘ri'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'Kirish muvaffaqiyatli!',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)