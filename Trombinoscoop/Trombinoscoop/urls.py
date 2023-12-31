"""
URL configuration for Trombinoscoop project.

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
# -*- coding: utf-8 -*-

from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('welcome/', views.welcome, name='welcome'),    
    #path('', welcome), # au lieu de login   
    #path('', views.welcome, name=''),
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),    
    path('register/', views.register, name='register'),    
    path('addFriend/', views.add_friend, name='add_friend'),    
    path('welcome/showProfile/userToShow=<int:id>/', views.show_profile, name='show_profile'),    
    path('modifyProfile/', views.modify_profile, name='modify_profile'),    
    path('ajax/checkEmailField/', views.ajax_check_email_field, name='ajax_check_email_field'),   
    path('ajax/addFriend/', views.ajax_add_friend, name='ajax_add_friend'),           
    path('ajax/publishMsg/', views.ajax_publish_msg, name='ajax_publish_msg'),           
    path('json/getMessages/', views.json_get_messages, name='json_get_messages'),    
    path('json/getFriends/', views.json_get_friends, name='json_get_friends'),    
]
