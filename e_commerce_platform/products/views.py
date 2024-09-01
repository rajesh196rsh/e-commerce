from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponse
from .upload_data import upload_data, extract_and_clean_product_data
from .utils import generate_summary
from . import constants


class UploadData(APIView):
    """
        Upload data
    """
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


class SummaryReport(APIView):
    """
        Generate summary
    """
    def get(self, request):
        try:
            summary = generate_summary()
            response = HttpResponse(summary.getvalue(), content_type="text/csv")
            response["Content-Disposition"] = "attachment; filename=summary_report.csv"
        except Exception as e:
            print(constants.SUMMARY_REPORT_FAILURE_MESSAGE)
            print(e)
            return JsonResponse(
                {"error": constants.SUMMARY_REPORT_FAILURE_MESSAGE},
                status=500
            )

        return response
