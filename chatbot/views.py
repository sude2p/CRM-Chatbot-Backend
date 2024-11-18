from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import render
from core.publisher import publish_to_rabbitmq
from .models import ChatSession
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, CreateAPIView, ListAPIView

from .models import ApiKey, ChatMessage,ChatSession
from core.models import OrganizationDetail, SubscriptionDetail
from .serializers import ChatSessionCreateSerializer, ChatMessageSerializer, APIKeyCreateSerializer
from rest_framework import status, filters
from core.permissions import IsAdminOrOrgUser
import logging
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny, IsAuthenticated
from core.renderer import UserRenderer
from django_filters.rest_framework import DjangoFilterBackend
from .decorators import api_key_required, jwt_auth_cookie_required
from django_ratelimit.decorators import ratelimit

# Create your views here.
@method_decorator(jwt_auth_cookie_required, name='dispatch')
# @method_decorator(lambda view: view.request.skip_middleware = True, name='dispatch')
class ApiKeyGenerateView(GenericAPIView):
    renderer_classes = [UserRenderer]
    # permission_classes = [IsAuthenticated, IsAdminOrOrgUser]
    permission_classes = [AllowAny]
    queryset = ApiKey.objects.all()
    serializer_class = APIKeyCreateSerializer
    
    def post(self, request):
        organization_id = request.data.get("organization")
        apikey_type = request.data.get("key_type")
    
        if not organization_id:
            return Response({"error": "Organization ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # organization = OrganizationDetail.objects.get(ref_orgid=organization_id)
            organization = OrganizationDetail.objects.get(ref_org_id=organization_id)
        except OrganizationDetail.DoesNotExist:
            raise ValidationError("Invalid organization reference.")

        try:
            subscription = SubscriptionDetail.objects.get(organization=organization)
        except SubscriptionDetail.DoesNotExist:
            raise ValidationError("No subscription found for this organization.")
        
        if subscription.is_expired:
            raise ValidationError("Subscription is expired. Cannot generate API key.")
        
        serializer = self.get_serializer(data=request.data, context={'organization': organization, 'apikey_type': apikey_type})
        if serializer.is_valid():
            serializer.save()
            publish_to_rabbitmq("API_key_generated",{
                "organizationId": organization.id,
                "subscription_status": subscription.is_expired
            })
            
            return Response({'status': 'success', 'message': 'API key generated successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'status': 'error', 'message': 'Failed to generate API key', 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        
            
class ChatSessionCreateViewSet(GenericAPIView):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionCreateSerializer
    
    filterset_fields = ['organization', 'created_at', 'session_name']
    search_fields = ['session_name', 'organization__name']
    ordering_fields = ['created_at', 'session_name']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.request.method in ["POST"]:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    
    def get_queryset(self):
        organization = self.request.organization
        print(f"organization for queryset :{organization}")
        queryset = ChatSession.objects.filter(organization=organization)
        logging.debug(f"ChatSession queryset: {queryset.query}")
        return queryset
    
    @method_decorator(api_key_required)
    @method_decorator(ratelimit(key="ip", rate="10/m", method="POST", block=False))
    def post(self, request):
        print(request.data) #for debugging
        organization = getattr(request, 'organization', None)
        if organization is None:
            raise ValidationError("Organization not found.")  
            
         # Generate a new session ID
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat_session =serializer.save(organization=organization)
        session_id = chat_session.session_id
        new_session_id = str(session_id)
        
        publish_to_rabbitmq("chat_session_created",{
            "sessionId": new_session_id,
            "organization": organization.id
            
        })
        
        return Response({
            "status": "success",
            "message": "Session created successfully",
            "data": serializer.data
            
        }, status=status.HTTP_201_CREATED)
    
    @method_decorator(jwt_auth_cookie_required)
    @method_decorator(api_key_required)
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk:
            # If 'pk' is provided, filter by the primary key (id)
            object = self.get_queryset().get(id=pk).first()
            if not object:
                return Response({'status': 'error', 'message': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(object)
            return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        
                 
class ChatMessageView(GenericAPIView):
    
    renderer_classes = [UserRenderer]
    serializer_class = ChatMessageSerializer
    
    def get_queryset(self):
        organization = self.request.organization
        queryset = ChatMessage.objects.filter(organization=organization)
        return queryset
    
   
    def get_permissions(self):
        if self.request.method in ["POST"]:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @method_decorator(api_key_required)   
    def post(self, request, *args, **kwargs):
        organization = request.organization
        session_id = request.data.get("session_id")
        try:
            session = ChatSession.objects.get(organization=organization, session_id=session_id)
        except ChatSession.DoesNotExist:
            return Response({"error": "Session not found."}, status=status.HTTP_404_NOT_FOUND)
        if not organization:
            return Response({"error": "Organization ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, context={'session': session, 'organization': organization})
        if serializer.is_valid():
            chat_message = serializer.save()
            publish_to_rabbitmq("chat_message_created",{
                "messageId": chat_message.id,
                "organization": organization.id
            })
              
                
            
            return Response({"status": "success", "message": "Message sent successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    @method_decorator(jwt_auth_cookie_required)
    @method_decorator(api_key_required)    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        pk=kwargs.get('pk')
        if pk:
            # If 'pk' is provided, filter by the primary key (id)
            object = queryset.get(id=pk)
            if not object:
                return Response({'status': 'error', 'message': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(object)
            return Response({'status': 'success','message': 'Message fetched successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            serializer = self.get_serializer(queryset, many=True)    
            return Response({'status': 'success','message': 'Message fetched successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
      
    def delete(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk:
            try:
                # Use get_object_or_404 or get_object() to find the instance
                obj = self.get_object()  # Automatically fetches the object using pk from the URL
                obj.delete()  # Delete the object
                publish_to_rabbitmq("chat_message_deleted",{
                    "organization": obj.organization.id,
                    "chatmessageId": obj.id
                })
                
                return Response({'status': 'success', 'message': 'Message deleted successfully'}, 
                                status=status.HTTP_204_NO_CONTENT)
            except Http404:
                return Response({'status': 'error', 'message': 'Message not found'}, 
                                status=status.HTTP_404_NOT_FOUND)
    
        return Response({'status': 'error', 'message': 'Invalid request. pk not provided.'}, 
                    status=status.HTTP_400_BAD_REQUEST)
        
        
          
              
        
    

    
   
                       
    
    
    