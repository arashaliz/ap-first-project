from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.admin import site
urlpatterns = [
    path('', include('app.urls'), name='app'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('admin/', site.urls)
]