from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="House Price Prediction API",
        default_version="v1",
        description="ML-powered House Price Prediction API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [

    path("admin/", admin.site.urls),

    # ML API
    path("api/", include("api.urls")),

    # authentication (Djoser + JWT)
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),

    # Swagger documentation
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="swagger"
    ),

    # ReDoc documentation
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="redoc"
    ),
]