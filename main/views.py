from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from main.models import *
from main.serializers import *
from main.models import User as CustomUser, Movie, Bookmark
from django.db.models import Avg
from django.utils.timezone import now
from datetime import timedelta
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
import json, random
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import tempfile

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomRegisterSerializer
    permission_classes = [AllowAny]

class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class UserRetrieveView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class GenreListView(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]

class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all().prefetch_related("genres", "episodes")
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]

class MovieDetailView(generics.RetrieveAPIView):
    queryset = Movie.objects.all().prefetch_related("genres", "episodes")
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]

# class VideoSourceListView(generics.ListAPIView):
#     queryset = VideoSource.objects.all()
#     serializer_class = VideoSourceSerializer
#     permission_classes = [IsAuthenticated]

class EpisodeListView(generics.ListAPIView):
    serializer_class = EpisodeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        movie_id = self.kwargs.get("movie_id")
        return Episode.objects.filter(movie_id=movie_id)

class RatingListCreateView(generics.ListCreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [AllowAny]
    queryset = Rating.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RatingDetailView(generics.ListAPIView):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]
    queryset = Rating.objects.all()

    def get_queryset(self):
        return Rating.objects.filter(user=self.request.user)

class RatingUpdateView(generics.UpdateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Rating.objects.filter(user=self.request.user)

class RatingDeleteView(generics.DestroyAPIView):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Rating.objects.filter(user=self.request.user)

class BannerListView(generics.ListAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [AllowAny]

class BookmarkListCreateView(generics.ListCreateAPIView):
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Bookmark.objects.filter(user=user)
        return Bookmark.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BookmarkDelete(generics.RetrieveDestroyAPIView):
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Bookmark.objects.filter(user=user)
        return Bookmark.objects.none()


def dashboard_callback(request, context):
    total_users = CustomUser.objects.count()
    premium_users = CustomUser.objects.filter(is_premium=True).count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    total_movies = Movie.objects.count()
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
            "total_bookmarks": total_bookmarks,
        },
        "top_movies": top_movies,
        "user_activity": json.dumps(user_activity),
    })
    return context


OTP_STORE = {}

class SendOTPView(GenericAPIView):
    serializer_class = SendOTPSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = random.randint(100000, 999999)
        OTP_STORE[email] = code

        send_mail(
            subject="Kirish kodi",
            message=f"Sizning kirish kodingiz: {code}",
            from_email="noreply@moviesite.com",
            recipient_list=[email],
        )
        return Response({"message": "Tasdiqlash kodi emailga yuborildi!"}, status=status.HTTP_200_OK)

class VerifyOTPView(GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]
        first_name = serializer.validated_data["first_name"]
        password = serializer.validated_data["password"]

        if OTP_STORE.get(email) != code:
            return Response({"error": "Noto‘g‘ri yoki eskirgan kod"}, status=status.HTTP_400_BAD_REQUEST)

        OTP_STORE.pop(email, None)

        user = User.objects.filter(email=email).first()

        if not user:
            user = User.objects.create(
                email=email,
                username=email,
                first_name=first_name,
                password=make_password(password),
            )
        else:
            if not check_password(password, user.password):
                return Response({"error": "Parol noto‘g‘ri"}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Kirish muvaffaqiyatli!",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)

class RequestPasswordResetView(GenericAPIView):

    permission_classes = [AllowAny]
    serializer_class = RequestPasswordResetSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if not user:
            return Response({"error": "Bu email ro‘yxatdan o‘tmagan."}, status=status.HTTP_404_NOT_FOUND)

        code = random.randint(100000, 999999)
        OTP_STORE[email] = code

        send_mail(
            subject="Parolni tiklash kodi",
            message=f"Sizning parolni tiklash kodingiz: {code}",
            from_email="noreply@moviesite.com",
            recipient_list=[email],
        )

        return Response({"message": "Parolni tiklash kodi emailga yuborildi!"}, status=status.HTTP_200_OK)


class ConfirmPasswordResetView(GenericAPIView):

    permission_classes = [AllowAny]
    serializer_class = ConfirmPasswordResetSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]
        new_password = serializer.validated_data["new_password"]

        if email not in OTP_STORE or str(OTP_STORE[email]) != str(code):
            return Response({"error": "Kod noto‘g‘ri yoki eskirgan."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "Foydalanuvchi topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        user.password = make_password(new_password)
        user.save()
        OTP_STORE.pop(email, None)

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Parol muvaffaqiyatli tiklandi!",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = request.user.notifications.all()
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

class NotificationMarkAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response({"detail": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)

        notif.is_read = True
        notif.save()
        return Response({"detail": "Notification marked as read."}, status=status.HTTP_200_OK)

class NotificationMarkAllAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"detail": "All notifications marked as read."}, status=status.HTTP_200_OK)

@csrf_exempt
def upload_video(request):
    if request.method == 'POST':
        file_obj = request.FILES.get('file')
        if not file_obj:
            return JsonResponse({'error': 'Fayl topilmadi'}, status=400)

        # Vaqtincha saqlash
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            for chunk in file_obj.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            from .tasks import upload_to_bunny_storage
            folder = "videos"
            video_url = upload_to_bunny_storage(tmp_path, filename=file_obj.name, folder=folder)
            return JsonResponse({'video_url': video_url})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Faqat POST ruxsat etiladi'}, status=405)
