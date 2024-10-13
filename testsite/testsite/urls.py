"""
URL configuration for testsite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.views.generic import TemplateView
from users.views import *
from users.swagger import schema_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TasksHome.as_view(), name='home'),
    path("archive", TasksArchive.as_view(), name='archive'),
    #path('search', search_view, name='search'),
    path("add", AddTask.as_view(), name='add_task'),
    path('task/<int:pk>', TasksDetail.as_view(), name='task'),
    path("smart", TasksSmart.as_view(), name='smart'),
    path("important", TasksImportant.as_view(), name='important'),
    path("urgent", TasksUrgent.as_view(), name='urgent'),
    path('api/v1/taskslist/', TasksAPIView.as_view()),
    path("", TemplateView.as_view(template_name='home.html'), name='home'),
    path('users/', include('users.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/v1/taskslist/<int:pk>/', TaskDetailAPIView.as_view()),
    path('api/v1/taskslist/smart/', SmartTasksAPIView.as_view()),
    path('api/v1/taskslist/archive/', ArchiveTasksAPIView.as_view()),
    path('task/<int:pk>/delete/', TaskDeleteView.as_view(), name='delete'),

]
