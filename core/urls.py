from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from main.views import *

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
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('admin/', admin.site.urls),

    path("api/users/register/", UserCreateView.as_view(), name="user-register"),
    path("api/users/me/", UserUpdateView.as_view(), name="user-update"),
    path("api/genres/", GenreListView.as_view(), name="genre-list"),
    path("api/movies/", MovieListView.as_view(), name="movie-list"),
    path("api/videos/", VideoSourceListView.as_view(), name="video-list"),
    path("api/ratings/", RatingListCreateView.as_view(), name="rating-list"),
    path("api/reviews/", ReviewListCreateView.as_view(), name="review-list"),
    path("api/bookmarks/", BookmarkListCreateView.as_view(), name="bookmark-list"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
