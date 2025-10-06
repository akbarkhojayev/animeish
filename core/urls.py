from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static
from main.views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

schema_view = get_schema_view(
    openapi.Info(
        title="UzMovie API",
        default_version='v1',
        description="UzMovie backend API documentation",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@uzmovie.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/social/', include('allauth.socialaccount.urls')),
    path('send-otp/', SendOTPView.as_view()),
    path('verify-otp/', VerifyOTPView.as_view()),
    path("password-reset/request/", RequestPasswordResetView.as_view(), name="password_reset_request"),
    path("password-reset/confirm/", ConfirmPasswordResetView.as_view(), name="password_reset_confirm"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path("users/register/", UserCreateView.as_view(), name="user-register"),
    path("user/me", UserRetrieveView.as_view(), name="user-retrieve"),
    path("users/me/", UserUpdateView.as_view(), name="user-update"),
    path("genres/", GenreListView.as_view(), name="genre-list"),
    path("movies/", MovieListView.as_view(), name="movie-list"),
    path("videos/", VideoSourceListView.as_view(), name="video-list"),
    path("ratings/", RatingListCreateView.as_view(), name="rating-list"),
    path('ratings/<int:pk>/update/', RatingUpdateView.as_view(), name='rating-update'),
    path('ratings/<int:pk>/delete/', RatingDeleteView.as_view(), name='rating-delete'),
    path("bookmarks/", BookmarkListCreateView.as_view(), name="bookmark-list"),
    path("banners/", BannerListView.as_view(), name="banner-list"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
