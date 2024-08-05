from apps.account.strategy_registration.strategy_factory import StrategyFactory
from apps.account.models import User
from apps.account.serializers import auth
from rest_framework import status, views
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import logout


class Logout(views.APIView):
    """
    API view to handle user logout.
    """

    def setup(self, request, *args, **kwargs):
        """
        Sets up the user authentication status before processing the request.
        - `self.user_authenticated`: Indicates whether the user is authenticated.
        """
        self.user_authenticated = request.user.is_authenticated  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request):  # noqa
        """
        Handles GET requests to log out the authenticated user.
        - Logs out the user and flushes the session if authenticated.
        - Returns a success message or an error if not logged in.
        """
        if self.user_authenticated:
            logout(request)
            request.session.flush()
            response = Response({"message": _("You have been logged out successfully")}, status=status.HTTP_200_OK)
        else:
            response = Response({"error": _("You are not logged in")}, status=status.HTTP_400_BAD_REQUEST)
        return response


class Login(views.APIView):
    """
    API view to handle user login operations.
    """
    serializer_class = auth.LoginSerializer

    def dispatch(self, request, *args, **kwargs):
        """
        Sets the throttle scope based on the request method.
        - Sets 'login_attempt' throttle scope for POST requests.
        """
        if request.method == 'POST':
            self.throttle_scope = 'login_attempt'
        else:
            self.throttle_scope = None  # noqa
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):  # noqa
        """
        Handles POST requests to log in a user.
        - Validates the login serializer.
        - Processes the login strategy and returns the response.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            strategy = StrategyFactory().get_login_strategy(request, serializer)
            response = strategy.process(request, serializer)
        else:
            response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return response


class LoginVerifyCode(views.APIView):
    """
    API view to handle verification of login codes sent to the user via email.
    """
    serializer_class = auth.VerifyCodeSerializer

    def post(self, request):  # noqa
        """
        Handles POST requests for verifying the login code.
        - Validates the verification code serializer.
        - Retrieves user session information and processes the verification strategy.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            user_session = request.session.get('user_login_info')
            if not user_session:
                return Response({"error": _("Session expired")}, status=status.HTTP_400_BAD_REQUEST)
            email_session = user_session['email']
            user = User.objects.filter(email=email_session).first()
            if user:
                strategy = StrategyFactory().get_verification_strategy()
                response = strategy.process(request, code, email_session, user)
            else:
                response = Response({"error": _("User not found")}, status=status.HTTP_404_NOT_FOUND)
            return response
        else:
            response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return response


class UserRegister(views.APIView):
    """
    API view for user registration.
    """
    serializer_class = auth.UserRegistrationSerializer

    def post(self, request):
        """
        Handles POST requests to register a new user.
        - Validates the user registration serializer.
        - Processes the registration strategy and returns the response.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            strategy = StrategyFactory.get_registration_strategy()
            response = strategy.process(request, serializer)
        else:
            response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return response


class UserRegistrationVerifyCode(views.APIView):
    """
    API view for verifying user registration using an OTP code.
    """
    serializer_class = auth.VerifyCodeSerializer

    def dispatch(self, request, *args, **kwargs):
        """
        Sets the throttle scope based on the request method.
        - Sets 'registration_attempt' throttle scope for POST requests.
        """
        if request.method == 'POST':
            self.throttle_scope = 'registration_attempt'
        else:
            self.throttle_scope = None  # noqa
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        """
        Handles POST requests to verify the registration OTP code.
        - Validates the verification code serializer.
        - Retrieves user session information and processes the OTP verification strategy.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            user_session = request.session.get('user_registration_info')

            if not user_session:
                return Response({"error": _("Session expired")}, status=status.HTTP_400_BAD_REQUEST)

            email = user_session.get('email')
            strategy = StrategyFactory.get_verification_email_new_user_strategy()
            response = strategy.process(request, code, email)
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
