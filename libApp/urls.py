"""
URL configuration for libApp project.

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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from users import views as user_views
from users.views import CustomLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('books.urls')),
    path('register/', user_views.register, name='register', ),
    path('login/', CustomLoginView.as_view(), name='login'),
    path("logout/", user_views.logout_view, name="logout"),
    path('profile/', user_views.profile, name='profile'),
    path('profile-view/', user_views.profile_view, name='profile-view'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
