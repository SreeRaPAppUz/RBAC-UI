"""
URL configuration for RBAC project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('users_list', views.users_list, name='users_list'),
    path('AddUser', views.AddUser, name='AddUser'),
    path('Delete/<int:user_id>', views.Delete, name='Delete'),
    path('update_user_role/<int:user_id>', views.update_user_role, name='update_user_role'),
    path('Permission', views.Permission, name='Permission'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
