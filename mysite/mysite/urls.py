from django.urls import include, path
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('login/', LoginView.as_view(template_name='toima/login.html')),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    path("", include("toima.urls")),
]
