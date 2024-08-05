from kavenegar import KavenegarAPI, APIException, HTTPException
from typing import Optional


def send_otp_code(phone_number: str, code: str, api_key: str, sender: Optional[str] = None) -> None:
    """
    Sends an OTP code to the specified phone number using the Kavenegar API.

    Args:
        phone_number (str): The recipient's phone number.
        code (str): The OTP code to be sent.
        api_key (str): The API key for authenticating with Kavenegar.
        sender (Optional[str]): The sender ID for the SMS. If not provided, defaults to None.
    """
    try:
        api = KavenegarAPI(api_key)
        params = {
            'sender': sender or 'default_sender',
            'receptor': phone_number,
            'message': f"Your verification code: {code}"
        }

        response = api.sms_send(params)
        print(response)
    except APIException as e:
        print(f'API Error: {e}')
    except HTTPException as e:
        print(f'HTTP Error: {e}')
