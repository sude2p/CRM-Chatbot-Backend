
from django.urls import path, include
from chatbot import views


urlpatterns = [ 
                path('generate-api-key/', views.ApiKeyGenerateView.as_view(), name='generate_api_key'),
                path('create-chat-session/', views.ChatSessionCreateViewSet.as_view(), name='create-chat-session'),
                path('list-chat-session/', views.ChatSessionCreateViewSet.as_view(), name='create-chat-session'),
                path('list-chat-session/<int:pk>/', views.ChatSessionCreateViewSet.as_view(), name='create-chat-session'),
                path('create-chat-message/', views.ChatMessageView.as_view(), name='create-chat-message'),
                path('list-chat-message/', views.ChatMessageView.as_view(), name='list-chat-session'),
                path('list-chat-message/<int:pk>/', views.ChatMessageView.as_view(), name='list-chat-session'),
                
    
    
    
]
