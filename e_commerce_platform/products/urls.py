from django.urls import path
from .views import UploadData


urlpatterns = [
    path('upload/data', UploadData.as_view(), name='upload'),

]
