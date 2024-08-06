import logging
from django.http import JsonResponse
from decouple import config  # noqa
from apps.account.strategy_registration.strategy_factory import redis_client

# Initialize the logger with the current module name.
logger = logging.getLogger(__name__)

# Define the path for the log file.
LOG_FILE_PATH = config('LOG_FILE_PATH', default='./apps/core/info.log')

# Configure logging with the specified log file, log level, and format.
logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)


class LoginRequiredMiddleware:
    """
    Middleware to handle login-required functionality, logging errors,
    providing JSON responses for specific error conditions, and checking for blocked IP addresses.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Handles requests and responses, logging errors, checking for blocked IPs,
        and returning JSON responses for specific error conditions.
        """
        logger.info(f"Request for URL: {request.path}. Method: {request.method}.")

        ip_address = self.get_ip(request)
        if self.is_blocked(ip_address):
            logger.warning(f"Blocked IP address: {ip_address} tried to access {request.path}.")
            return JsonResponse({
                'error': 'Too many unsuccessful attempts from this IP. Try again later after an hour.',
                'status_code': 403
            }, status=403)

        response = self.get_response(request)
        self.log_response(request, response)
        return response

    @staticmethod
    def get_ip(request):
        """
        Get the IP address from the request.
        """
        return request.META.get('REMOTE_ADDR')

    @staticmethod
    def is_blocked(ip_address):
        """
        Check if the IP address is blocked.
        """
        return redis_client.get(f'block:{ip_address}')

    def log_response(self, request, response):  # noqa
        """
        Log the response details.
        """
        logger.info(
            f"Request for URL: {request.path}. Method: {request.method}. "
            f"IP: {self.get_ip(request)}\t"
            f"User: {getattr(request, 'user', 'Anonymous')}. Status Code: {response.status_code}"
        )

    def process_exception(self, request, exception):  # noqa
        """
        Process exceptions and log them.
        """
        logger.error(f"Unexpected error: {exception}", exc_info=True)
        return JsonResponse({
            'error': 'Internal Server Error. Please try again later.',
            'status_code': 500
        }, status=500)
