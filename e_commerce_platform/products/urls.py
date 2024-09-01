from django.urls import path
from .views import UploadData, SummaryReport


urlpatterns = [
    path('upload/data', UploadData.as_view(), name='upload'),
    path('get/summary/report', SummaryReport.as_view(), name='summary_report'),
]
