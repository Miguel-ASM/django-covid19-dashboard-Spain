from django.urls import path
from . import views
from .apps import DashboardConfig

app_name = DashboardConfig.name
urlpatterns = [
    path('',views.index,name='index')
]
