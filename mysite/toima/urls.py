from django.urls import path

from . import views

app_name = "toima"
urlpatterns = [
    path("", views.home, name="home"),
    path("sendRequest/",
         views.sendRequest, name="sendRequest"),
    path("answerRequest/<int:cr_id>",
         views.answerRequest, name="answerRequest"),
    path("readAnswer/<int:cr_id>",
         views.readAnswer, name="readAnswer"),
    path('administration/', views.administration, name='administration'),
    path('administration/<int:user_id>',
         views.administrationState, name='administrationState'),
    path('messaging/<int:us_id>',
         views.messaging, name='messaging'),
    path('messaging/<str:us_id>/send',
         views.messagingSend, name='messagingSend'),
]
