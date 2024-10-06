"""
URL configuration for chartreuse_admin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularSwaggerView,
)

schema_view = get_schema_view(
   openapi.Info(
      title="Chartreuse API",
      default_version='v1',
      description="This is the API documentation for the Chartreuse project.",
   ),
   public=True,
)

urlpatterns = [
    path("chartreuse/", include("chartreuse.urls")),
    path('auth/', include('django.contrib.auth.urls')),
    path("admin/", admin.site.urls),
    path('chartreuse/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('chartreuse/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
