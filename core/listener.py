# core/listener.py
import json
from .utils import get_rabbitmq_connection
from chatbot.views import handle_api_key_generated
from core.views import (handle_platform_user_created , handle_organization_created, handle_org_user_created,
                         handle_org_user_deleted, handle_platform_user_updated,handle_organization_updated,
                         handle_org_user_updated, handle_organization_deleted, handle_suscription_created, 
                         handle_chat_service_enabled)


def callback(ch, method, properties, body):
    message = json.loads(body)
    event_type = message['eventType']
    data = message['data']
    
    print(f"Received event: {event_type}")
    print(f"Data: {data}")

    # Process the message here
    if event_type == 'platform_user_created':
        handle_platform_user_created(data)
        
    elif event_type == 'platform_user_updated': 
        handle_platform_user_updated(data) 
        
    elif event_type == 'organization_created':
        handle_organization_created(data)
        
    elif event_type == 'organization_updated':
        handle_organization_updated(data)
        
    elif event_type == 'organization_deleted':
        handle_organization_deleted(data)    
        
    elif event_type == 'org_user_created':
        handle_org_user_created(data)   
    
    elif event_type == 'org_user_updated':
        handle_org_user_updated(data)     
        
    elif event_type == 'org_user_deleted':
        handle_org_user_deleted(data)     
                  
    elif event_type == 'suscription_created':
        handle_suscription_created(data)
        
    elif event_type == 'chat_service_enabled':
        handle_chat_service_enabled(data) 
    elif event_type == 'api_key_generated':
        handle_api_key_generated(data)      
      
        
        
    

def start_listener():
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    
    # Declare the fanout exchange
    channel.exchange_declare(exchange='CRM_EVENTS_EXCHANGE', exchange_type='fanout')
    
    # Declare a queue and bind it to the exchange
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='CRM_EVENTS_EXCHANGE', queue=queue_name)
    
    print('Waiting for messages. To exit press CTRL+C')

    # Set up the consumer
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    
    # Start consuming
    channel.start_consuming()