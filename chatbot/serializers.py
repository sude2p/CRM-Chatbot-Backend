import logging
from rest_framework import serializers
from .models import ChatSession, ChatMessage, ApiKey
from core.utils import generate_api_key
from django.db import transaction



class APIKeyCreateSerializer(serializers.ModelSerializer):
    domain = serializers.URLField(max_length=255, required=True)
    class Meta:
    
        model = ApiKey
        fields = ['organization','key_type','domain']
        read_only_fields = ['key']
    def create(self, validated_data):
        organization = self.context.get('organization')
        domain = validated_data.get('domain')
        
        existing_key = ApiKey.objects.filter(organization=organization,is_expired=False)
        # If existing keys found, set them to expired
        if existing_key.exists():
            for key in existing_key:
                key.has_expired = True
                key.save()
        
                      
        try:
            with transaction.atomic():
                api_key = generate_api_key(validated_data.get('key_type'))
                print(f"Generated API key: {api_key}")  # Generate an API key
                api_key_obj = ApiKey.objects.create(organization=organization, key=api_key, 
                                                has_expired=False,
                                                domain=domain)
                return api_key_obj
        except Exception as e:
            logging.error(f"Error creating API key: {str(e)}")    
        
        
class ChatSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
       
        model = ChatSession
        fields = [ 'session_name', 'created_at']
        read_only_fields = [ 'created_at']
        
    
class ChatMessageSerializer(serializers.ModelSerializer):
    session_id = serializers.UUIDField(required=True)
    class Meta:
        model = ChatMessage
        fields = ['id','session_id', 'message', 'sender', 'is_bot', 'created_at']  
        read_only_fields = ['id', 'created_at'] 
        
    def create(self, validated_data):
        print(f"validated_data: {validated_data}")
        organization = self.context.get('organization')
        session_id = validated_data.get('session_id')
        if not session_id:
            raise serializers.ValidationError("session_id is required.")
        # Look up the session object
        session = ChatSession.objects.filter(session_id=session_id, organization=organization).first()
        if not session:
            raise serializers.ValidationError("Session not found.")
        session = self.context.get('session')
        return ChatMessage.objects.create(organization=organization, session=session, **validated_data)
           
        