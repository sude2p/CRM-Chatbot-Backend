from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import jwt
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
import jwt
from django.conf import settings


class JWTAuthCookieMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """
        This middleware sets the request.user based on the access token from the
        Authorization header or the access_token cookie.

        If the token is valid and contains a user_id, it fetches the corresponding
        CustomUser object and assigns it to request.user.

        If the token is invalid or no token is present, it sets request.user to None.
        """

        access_token = request.COOKIES.get("access_token") or request.headers.get(
            "Authorization", ""
        ).replace("Bearer ", "")

        if access_token:
            print(f"Access Token Cookie: {access_token}")
            request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
            print(f"Authorization Header Set: {request.META.get('HTTP_AUTHORIZATION')}")

            signing_key = settings.SIMPLE_JWT["SIGNING_KEY"]

            try:
                # Decode the JWT token
                decoded_token = jwt.decode(
                    access_token, signing_key, algorithms=["HS256"]
                )
                print(f"Decoded token: {decoded_token}")

                user_id = decoded_token.get("user_id")
                print(f"User ID: {user_id}")

                if user_id:
                    # Get the custom user model
                    User = get_user_model()

                    try:
                        # Fetch the CustomUser object based on the ref_user_id
                        user = User.objects.get(user_ref_id=user_id)
                        request.user = user  # Assign the user object to request.user
                        print(f"User authenticated: {user}")
                        # Explicitly load permissions
                        if hasattr(user, "get_all_permissions"):
                            user_permissions = user.get_all_permissions()
                            print(f"User permissions: {user_permissions}")
                        else:
                            print("User permissions not found.")
                    except User.DoesNotExist:
                        print(f"User with ref_user_id {user_id} does not exist")
                        request.user = (
                            None  # Set request.user to None if user is not found
                        )
                else:
                    request.user = None  # Set request.user to None if user_id is not found in the token

            except jwt.ExpiredSignatureError:
                print("Token has expired")
                request.user = None
            except jwt.InvalidTokenError:
                print("Invalid token")
                request.user = None

        else:
            request.user = None


from django.core.exceptions import PermissionDenied
from core.models import  OrganizationDetail
from chatbot.models import ApiKey

class ApiKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        api_key = request.headers.get("X-API-KEY")
        print(f"API Key: {api_key}") #for debugging

        if not api_key:
            raise PermissionDenied("API Key is missing.")

        try:
            # Fetch API key and the associated organization
            api_key_instance = ApiKey.objects.get(key=api_key, has_expired=False)
            organization_instance = api_key_instance.organization
        except ApiKey.DoesNotExist:
            raise PermissionDenied("Invalid or expired API Key.")

        # Attach organization to request object for further use
        request.organization = organization_instance

        # Proceed with the request
        response = self.get_response(request)
        return response
