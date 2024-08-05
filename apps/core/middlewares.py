import logging
from django.http import JsonResponse
from decouple import config  # noqa

"""Initialize the logger with the current module name."""
logger = logging.getLogger(__name__)

"""Define the path for the log file."""
LOG_FILE_PATH = config('LOG_FILE_PATH', default='./apps/core/info.log')
print(f"Log file path: {LOG_FILE_PATH}")
"""Configure logging with the specified log file, log level, and format."""
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='a')


class LoginRequiredMiddleware:
    """
    Middleware to handle login-required functionality, logging errors,
    and providing JSON responses for specific error conditions.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Handles requests and responses, logging errors and returning JSON responses
        for specific error conditions.
        """
        logger.info(f"Request for URL: {request.path}. Method: {request.method}.")

        response = None
        try:
            response = self.get_response(request)
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return JsonResponse({
                'error': 'Internal Server Error. Please try again later.',
                'status_code': 500
            }, status=500)

        logger.info(
            f"Request for URL: {request.path}. Method: {request.method}. "
            f"User: {getattr(request, 'user', 'Anonymous')}. Status Code: {response.status_code}")

        return response
