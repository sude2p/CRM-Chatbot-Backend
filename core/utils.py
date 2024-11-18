from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.core.mail import EmailMessage
import os
import pika
import secrets

# from django.conf import settings
from urllib.parse import urlparse
from enum import Enum


class SourceType(Enum):
    """
    Enumeration for different types of users in the system.

    Attributes:
        ADMIN (str): Represents a platform user, typically an administrator.
        USER (str): Represents an organizational user.
    """

    STAFF_USER = "staff_user"
    USER = "org_user"


def decode_jwt_token(token):
    """
    Decodes a JWT token to extract the user ID.

    Args:
        token (str): The JWT token to decode.

    Returns:
        int or dict: The user ID extracted from the token if valid,
                     otherwise a dictionary with an error message.
    """

    try:
        access_token = AccessToken(token)
        user_id = access_token["user_id"]
        return user_id
    except TokenError as e:
        return {"error": str(e)}


class Util:

    @staticmethod
    def send_email(data):
        """
        Sends an email using the provided data.

        Args:
            data (dict): A dictionary containing the email details. Must include:
                - 'subject' (str): The subject of the email.
                - 'body' (str): The body of the email.
                - 'to_email' (str): The recipient's email address.

        Raises:
            ValueError: If any required field is missing or invalid.
        """
        email = EmailMessage(
            subject=data["subject"],
            body=data["body"],
            from_email=os.environ.get("EMAIL_HOST_USER"),
            to=[data["to_email"]],
        )
        email.send(fail_silently=False)
        
def generate_api_key(data):
    return f"{data}-{secrets.token_hex(25)}"   # Generates a 50-character API key (25 bytes -> 50 hex characters)      


# def get_rabbitmq_connection():
#     """
#     Establishes and returns a blocking connection to RabbitMQ.

#     The connection parameters, including host, port, credentials, and virtual host,
#     are retrieved from the Django settings.

#     Returns:
#         pika.BlockingConnection: A connection object to interact with RabbitMQ.

#     Raises:
#         pika.exceptions.AMQPConnectionError: If the connection to RabbitMQ fails.
#     """
#     return pika.BlockingConnection(
#         pika.ConnectionParameters(
#             host=settings.RABBITMQ_HOST,
#             port=settings.RABBITMQ_PORT,
#             credentials=pika.PlainCredentials(
#                 username=settings.RABBITMQ_USER,
#                 password=settings.RABBITMQ_PASSWORD
#             ),
#             virtual_host=settings.RABBITMQ_VHOST
#         )
#     )

# Parse the CloudAMQP URL
# cloudamqp_url = 'amqps://gvimvktu:zDHup1EcU3ZpFkw-3n33HjPKTvq-BJGj@dingo.rmq.cloudamqp.com/gvimvktu'

# url = urlparse(cloudamqp_url)
# params = pika.URLParameters()
# print(f'url for rabbit mq : {url}')

# def get_rabbitmq_connection():
#     return pika.BlockingConnection(
#         pika.ConnectionParameters(
#             host=url.hostname,
#             port=url.port or 5671,  # Default to 5671 for amqps
#             credentials=pika.PlainCredentials(
#                 username=url.username,
#                 password=url.password
#             ),
#             virtual_host=url.path[1:]  # Remove the leading '/'
#         )
#     )

# Parse the CloudAMQP URL
cloudamqp_url = os.environ.get("CLOUDAMPURL")

params = pika.URLParameters(cloudamqp_url)


def get_rabbitmq_connection():
    return pika.BlockingConnection(params)
