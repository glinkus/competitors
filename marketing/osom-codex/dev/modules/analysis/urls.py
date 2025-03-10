from django.urls import path

from . import views

app_name = "modules.analysis" 

urlpatterns = [
    path("analyse", views.AnalyseView.as_view(), name="analyse"),
]