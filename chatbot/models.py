from django.db import models
import uuid
from core.models import OrganizationDetail


# Create your models here.

class ChatSession(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(OrganizationDetail, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    session_name = models.CharField(max_length=100, default="New Chat Session")
    
    def __str__(self):
        return f"{self.session_id} - {self.organization}"
    
class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    message = models.TextField()
    sender = models.CharField(max_length=255)
    is_bot = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    api_key = models.CharField(max_length=255, null=True)
    organization = models.ForeignKey(OrganizationDetail, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.session} - {self.sender}"
class KeyTypeChoices(models.TextChoices):
    CHAT = "chat", "chat"
    INTRANET = "intranet", "intranet"
        
class ApiKey(models.Model):
    key = models.CharField(max_length=100, unique=True)
    key_type = models.CharField(max_length=20, choices=KeyTypeChoices.choices, default=KeyTypeChoices.CHAT)
    created_at = models.DateTimeField(auto_now_add=True)
    has_expired = models.BooleanField(default=False)
    organization = models.ForeignKey(OrganizationDetail, on_delete=models.CASCADE)
    domain = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.key    
    

    
    
        