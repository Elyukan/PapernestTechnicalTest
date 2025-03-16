from django.urls import path
from .views import NetworkCoverageView

urlpatterns = [
    path("coverage/", NetworkCoverageView.as_view()),
]
