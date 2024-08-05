from abc import ABC, abstractmethod
from decouple import config  # noqa
from django.conf import settings
from django.contrib.auth import login
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from datetime import datetime, timedelta
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from apps.account.models import User
from utility.otp_redis.otp_email import CodeGenerator
from django.utils.translation import gettext_lazy as _
import pytz
import redis

"""
Initializes a Redis client to connect to the Redis server.
"""
redis_client = redis.StrictRedis(host=config('REDIS_HOST'), port=config('REDIS_PORT'), db=0)


class StrategyFactory:
    """
    Factory class to retrieve the appropriate strategy based on the request type.
    """

    @staticmethod
    def get_login_strategy(request, serializer):  # noqa
        """
        Returns the login strategy instance based on the request and serializer.
        :param request: The HTTP request object.
        :param serializer: The serializer containing validated data.
        :return: An instance of EmailLoginStrategy.
        """
        return EmailLoginStrategy()

    @staticmethod
    def get_verification_strategy():
        """
        Returns the verification strategy instance.
        :return: An instance of EmailVerificationStrategy.
        """
        return EmailVerificationStrategy()

    @staticmethod
    def get_registration_strategy():
        """
        Returns the user registration strategy instance.
        :return: An instance of UserRegistrationEmailStrategy.
        """
        return UserRegistrationEmailStrategy()

    @staticmethod
    def get_verification_email_new_user_strategy():
        """
        Returns the email verification strategy for new user registration.
        :return: An instance of UserEmailVerificationStrategy.
        """
        return UserEmailVerificationStrategy()


class RegistrationStrategy(ABC):
    """
    Abstract base class for different login or registration strategies.
    """

    MAX_ATTEMPTS = 3
    BLOCK_DURATION = 3600

    @abstractmethod
    def process(self, request, serializer, code, email, user):
        """
        Process the request using the appropriate strategy.
        """
        pass

    def get_ip(self, request):
        """
        Get the IP address from the request.
        """
        return request.META.get('REMOTE_ADDR')

    def is_blocked(self, identifiers, ip_address):  # noqa
        """
        Check if any of the identifiers (e.g., email, phone number) or IP address is blocked.
        """
        return any(redis_client.get(f'block:{identifier}') for identifier in identifiers) or redis_client.get(
            f'block:{ip_address}')

    def increment_failed_attempts(self, identifiers, ip_address):
        """
        Increment the failed attempts count for the identifiers and IP address and set blocking if the threshold
        is reached.
        """
        for identifier in identifiers:
            redis_client.incr(f'attempts:{identifier}')
            if int(redis_client.get(f'attempts:{identifier}')) > self.MAX_ATTEMPTS:
                redis_client.set(f'block:{identifier}', 'blocked', ex=self.BLOCK_DURATION)

        redis_client.incr(f'attempts:{ip_address}')
        if int(redis_client.get(f'attempts:{ip_address}')) > self.MAX_ATTEMPTS:
            redis_client.set(f'block:{ip_address}', 'blocked', ex=self.BLOCK_DURATION)

    def reset_failed_attempts(self, identifiers, ip_address):  # noqa
        """
        Reset failed attempts for the identifiers and IP address.
        """
        for identifier in identifiers:
            redis_client.delete(f'attempts:{identifier}')
            redis_client.delete(f'block:{identifier}')
        redis_client.delete(f'attempts:{ip_address}')
        redis_client.delete(f'block:{ip_address}')


class PasswordLoginStrategy(RegistrationStrategy):
    def process(self, request, serializer, code=None, email=None, user=None):
        user_data = serializer.validated_data
        email = user_data['email']
        ip_address = self.get_ip(request)
        identifiers = [email]
        self.reset_failed_attempts(identifiers, ip_address)
        if self.is_blocked(identifiers, ip_address):
            return Response(
                {"error": _("There have been many unsuccessful attempts with this IP. Try again later after an hour.")},
                status=status.HTTP_403_FORBIDDEN
            )
        self.increment_failed_attempts(identifiers, ip_address)
        if not User.objects.filter(email=serializer.validated_data['email']).exists():  # noqa
            return Response({"error": _("User with this email or Password dose not exists")},
                            status=status.HTTP_400_BAD_REQUEST)

        request.session['user_login_info'] = {
            'email': email,
        }
        otp = CodeGenerator().generate_and_store_code(email)
        send_mail(
            subject='Verification Code',
            message=f'Your verification code is: {otp}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({"message": _("Code sent to your email")}, status=status.HTTP_201_CREATED)


class PasswordLoginStrategy(RegistrationStrategy):
    pass


class EmailLoginStrategy(RegistrationStrategy):

    def process(self, request, serializer, code=None, email=None, user=None):
        user_data = serializer.validated_data
        email = user_data['email']
        ip_address = self.get_ip(request)
        identifiers = [email]
        self.reset_failed_attempts(identifiers, ip_address)
        if self.is_blocked(identifiers, ip_address):
            return Response(
                {"error": _("There have been many unsuccessful attempts with this IP. Try again later after an hour.")},
                status=status.HTTP_403_FORBIDDEN
            )
        self.increment_failed_attempts(identifiers, ip_address)
        if not User.objects.filter(email=serializer.validated_data['email']).exists():  # noqa
            return Response({"error": _("User with this email or Password dose not exists")},
                            status=status.HTTP_400_BAD_REQUEST)

        request.session['user_login_info'] = {
            'email': email,
        }
        otp = CodeGenerator().generate_and_store_code(email)
        send_mail(
            subject='Verification Code',
            message=f'Your verification code is: {otp}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({"message": _("Code sent to your email")}, status=status.HTTP_201_CREATED)





class UserRegistrationEmailStrategy(RegistrationStrategy):

    def process(self, request, serializer, code=None, email=None, user=None):  # noqa
        """
        Process the user registration request with email verification.
        is_blocked : checks if the user or ip address is blocked for too many failed attempts.
        reset_failed_attempts : resets the failed attempts count for the user or ip address after a successful attempt.
        :param request: The HTTP request object.
        :param serializer: The serializer containing validated data.
        :return: A Response object indicating the status of the email sending.
        """
        user_data = serializer.validated_data
        user_email = user_data['email']
        phone_number = user_data['phone_number']
        ip_address = self.get_ip(request)
        identifiers = [user_email, phone_number]
        if self.is_blocked(identifiers, ip_address):
            return Response(
                {"error": _("There have been many unsuccessful attempts with this IP. Try again later after an hour.")},
                status=status.HTTP_403_FORBIDDEN
            )
        if User.objects.filter(email=user_email).exists():  # noqa
            return Response({"error": _("User with this email already exists")}, status=status.HTTP_400_BAD_REQUEST)

        self.increment_failed_attempts(identifiers, ip_address)
        request.session['user_registration_info'] = {
            'phone_number': phone_number,
            'email': user_email,
            'username': user_data['username'],
            'password': user_data['password'],
        }
        otp = CodeGenerator().generate_and_store_code(user_email)
        send_mail(
            subject='Verification Code',
            message=f'Your verification code is: {otp}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user_email],
            fail_silently=False,
        )
        return Response({"message": _("Code sent to your email")}, status=status.HTTP_201_CREATED)


class EmailVerificationStrategy(RegistrationStrategy):
    """
    Strategy for verifying codes sent via email.
    """

    def process(self, request, code, email, user, serializer=None):  # noqa
        """
        Process the email verification request.
        :param request: The HTTP request object.
        :param code: The verification code entered by the user.
        :param email: The email session key.
        :param user: The user object.
        :return: A Response object indicating the success or failure of the verification.
        """
        user_session = request.session.get('user_login_info')
        email_session = user_session['email']  # noqa
        code_instance = redis_client.get(email_session)  # noqa
        if not code_instance:
            return Response({"error": _("Code is expired")}, status=status.HTTP_400_BAD_REQUEST)

        stored_code = code_instance.decode('utf-8')  # noqa
        current_time = datetime.now(tz=pytz.timezone('Asia/Tehran'))
        expiration_time = current_time + timedelta(minutes=2)

        if code == stored_code and expiration_time > current_time:
            AccessToken.for_user(user=user)
            RefreshToken.for_user(user=user)
            print(AccessToken.for_user(user=user))
            print(RefreshToken.for_user(user=user))
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            self.reset_failed_attempts(email_session, self.get_ip(request))
            redis_client.delete(email_session)
            response = Response({"message": _("Code verified successfully")}, status=status.HTTP_200_OK)
        else:
            response = Response({"error": _("Code is expired or invalid")}, status=status.HTTP_400_BAD_REQUEST)
        return response

    def get_ip(self, request):
        return request.META.get('REMOTE_ADDR')


class UserEmailVerificationStrategy(RegistrationStrategy):
    """
    Strategy for verifying email codes during user registration.
    """

    def process(self, request, code, email, user=None, serializer=None):  # noqa
        """
        Process the email verification request during user registration.
        :param request: The HTTP request object.
        :param code: The verification code entered by the user.
        :param email: The email session key.
        :param user: The user object (optional, used for login if provided).
        :return: A Response object indicating the success or failure of the verification.
        """
        user_session = request.session.get('user_registration_info')
        if not user_session:
            return Response({"error": _("Session expired")}, status=status.HTTP_400_BAD_REQUEST)
        email_session = user_session['email']  # noqa
        code_instance = redis_client.get(email_session)  # noqa
        if not code_instance:
            return Response({"error": _("Code is expired")}, status=status.HTTP_400_BAD_REQUEST)

        stored_code = code_instance.decode('utf-8')  # noqa
        current_time = datetime.now(tz=pytz.timezone('Asia/Tehran'))
        expiration_time = current_time + timedelta(minutes=2)

        if code == stored_code and current_time < expiration_time:
            User.objects.create_user(
                phone_number=user_session['phone_number'],
                email=email_session,
                username=user_session['username'],
                password=user_session['password'],
            )
            user = User.objects.get(email=email_session)
            AccessToken.for_user(user)
            RefreshToken.for_user(user)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            self.reset_failed_attempts(email_session, self.get_ip(request))
            redis_client.delete(email_session)
            response = Response({"message": _("User created and verified successfully")},
                                status=status.HTTP_201_CREATED)
        else:
            response = Response({"error": _("Code is expired or invalid")}, status=status.HTTP_400_BAD_REQUEST)
        return response

    def get_ip(self, request):
        return request.META.get('REMOTE_ADDR')
