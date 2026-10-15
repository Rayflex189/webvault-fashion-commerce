from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    path('run-webhook/', views.run_campaigns_webhook, name='run_webhook'),
]
