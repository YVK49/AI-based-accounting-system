import json
import logging
from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ValidationError, PermissionDenied

logger = logging.getLogger(__name__)

class ApiView(View):
    """
    Base view for all API endpoints.
    Handles JSON parsing/response and standard error catching.
    """
    
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except ValidationError as e:
            return self.error_response(getattr(e, 'message', str(e)), status=400)
        except PermissionDenied as e:
            return self.error_response(str(e), status=403)
        except Exception as e:
            logger.exception("Internal Server Error")
            return self.error_response("An unexpected error occurred", status=500)

    def success_response(self, data, status=200):
        return JsonResponse({
            "status": "success",
            "data": data
        }, status=status)

    def error_response(self, message, status=400, errors=None):
        response_data = {
            "status": "error",
            "message": message
        }
        if errors:
            response_data["errors"] = errors
        return JsonResponse(response_data, status=status)

    def get_json_body(self):
        try:
            return json.loads(self.request.body)
        except json.JSONDecodeError:
            raise ValidationError("Invalid JSON body")
