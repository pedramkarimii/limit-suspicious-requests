from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

"""Define URL patterns for the entire application."""
urlpatterns = [
    path("", include("apps.account.urls")),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]

"""Check if the application is in debug mode."""
if settings.DEBUG:
    from django.conf.urls.static import static

    """Add URL pattern for accessing the Django admin site."""
    urlpatterns += (
            [path("admin/", admin.site.urls), path("schema/", SpectacularAPIView.as_view(), name="schema"),
             path("schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
             path("schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui")]
            + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
            + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )

    """Customize Django admin interface titles."""
    admin.site.site_header = 'Achare'
    admin.site.site_title = 'Achare Administration'
    admin.site.index_title = 'Welcome To Achare Administration'
