from . import views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('<str:username>/blogs/', views.user_blogs, name='user_blogs'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('write/', views.write_blog, name='write_blog'),
    path('blog/<slug:slug>/edit/', views.edit_blog, name='edit_blog'),
    path('blog/<slug:slug>/delete/', views.delete_blog, name='delete_blog'),
    path('blog/<int:blog_id>/like/', views.like_blog, name='like_blog'),
    path('blog/<int:blog_id>/save/', views.save_blog, name='save_blog'),
    path('user/<str:username>/follow/', views.follow_user, name='follow_user'),
    path('notifications/clear/', views.clear_notifications, name='clear_notifications'),
]