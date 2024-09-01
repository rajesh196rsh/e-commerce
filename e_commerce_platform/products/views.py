from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponse
import csv
from io import StringIO
from .upload_data import upload_data, extract_and_clean_product_data
from . import constants


class UploadData(APIView):

    def post(self, request):
        response_status = status.HTTP_400_BAD_REQUEST
        res = {
            "success": False,
            "message": constants.DATA_UPLOAD_FAILURE_MESSAGE
        }
        try:
            data = request.data
            csv_path = data["csv_path"]
            data_df = extract_and_clean_product_data(csv_path)
            upload_data(data_df)
            response_status = status.HTTP_200_OK
            res = {
                "success": True,
                "message": constants.DATA_UPLOAD_SUCCESSFUL_MESSAGE
            }
        except Exception as e:
            return Response(e)

        return Response(res, status=response_status)
