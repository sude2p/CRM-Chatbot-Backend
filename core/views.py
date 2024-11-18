import json
from .models import CustomUser, UserDetail, OrganizationDetail, SuscriptionDetail,ApplicationDetail
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group, Permission
from django.http import JsonResponse

# Create your views here.

def handle_platform_user_created(event_data):
  
    
    
    user_id = event_data['userId']
    # Ensure user_id is provided
    if not user_id:
        raise ValueError("user_id is required in event data")
    
    email = event_data['email']
    first_name = event_data.get('firstName')
    last_name = event_data.get('lastName')
    contact_number = event_data['contactNumber']
    is_admin = event_data['isAdmin']
    is_staff = event_data['isStaff'] 
    organization = event_data['organizationId'] if 'organization' in event_data else None
    created_by = event_data['createdBy'] if 'createdBy' in event_data else None
    user_type = event_data['userType']
    print(f"email: {email}")
    print(f'user_type: {user_type}')
    print(f"first_name: {first_name}")
    print(f"last_name: {last_name}")
    print(f"contact_number: {contact_number}")

    
    # Create or update the UserReference entry
    try:
        with transaction.atomic():
            user_reference, created = CustomUser.objects.get_or_create(
                user_ref_id=user_id,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_admin': is_admin,
                    'is_staff': is_staff,
            
            })
            if created:
                # Log the creation if necessary
                print(f"UserReference created: {user_reference}")
                UserDetail.objects.get_or_create(
                            user=user_reference,
                            defaults={
                                'contact_number': contact_number,
                                'user_type': user_type,
                                'organization': organization,
                                'created_by': created_by
                            }
        )
    except Exception as e:
         print(f"An error occurred while creating UserReference: {str(e)}") 


def handle_platform_user_updated(event_data):
    user_id = event_data['userId']
    # Ensure user_id is provided
    if not user_id:
        raise ValueError("user_id is required in event data")
    
    email = event_data['email']
    first_name = event_data.get('firstName')
    last_name = event_data.get('lastName')
    contact_number = event_data['contactNumber']
    is_admin = event_data['isAdmin']
    is_staff = event_data['isStaff']
    organization = event_data['organizationId'] if 'organizationId' in event_data else None
    updated_by = event_data['updatedBy'] if 'updatedBy' in event_data else None
    user_type = event_data['userType']
    # Update the CustomUser and UserDetail entries
    try:
        with transaction.atomic():
            custom_user_reference = CustomUser.objects.filter(user_ref_id=user_id).first()
            if custom_user_reference:
                custom_user_reference.email = email
                custom_user_reference.first_name = first_name
                custom_user_reference.last_name = last_name
                custom_user_reference.is_admin = is_admin
                custom_user_reference.is_staff = is_staff
                custom_user_reference.save()
                print(f"User updated: {custom_user_reference}") #for debugging
                # Update the UserDetail entry
            user_detail = UserDetail.objects.get(user=custom_user_reference)
            if user_detail:
                user_detail.contact_number = contact_number
                user_detail.user_type = user_type
                user_detail.organization = organization
                user_detail.created_by = updated_by
                user_detail.save()
                print(f"UserDetail updated for user: {user_detail}")#for debugging
            else:
                print(f"User with ID {user_id} not found. No update performed.")    
    except Exception as e:
        print(f"An error occurred while updating UserReference: {str(e)}")



def handle_organization_created(event_data):
    
   
    
    organization_id = event_data['orgId']
    user_id = event_data['userId']
    email = event_data['email']
    name = event_data['name']
    created_by = event_data['createdBy']
    
    try:
        with transaction.atomic():
            organization_reference, created = OrganizationDetail.objects.get_create(
                    ref_org_id=organization_id, 
                    defaults={
                    'name': name,
                    'created_by': created_by
                })
            if created:
                print(f"Organization created: {organization_id}, {user_id}, {email}, {name}")
            else:
                print(f"Organization already exists: {organization_id}, {user_id}, {email}, {name}")
                
    except Exception as e:
         print(f"An error occurred while creating UserReference: {str(e)}")      
    
    
    
    if organization_id and user_id:
        with transaction.atomic():
            UserDetail.objects.filter(user=user_id).update(organization=organization_id)
        print(f"Organization created: {organization_id}, {user_id}, {email}, {name}") #for debugging
        
        
        
def handle_organization_updated(event_data):
    organization_id = event_data['orgId']
    user_id = event_data['userId']
    email = event_data['email']
    name = event_data['name']
    created_by = event_data['createdBy']
    
    try:
        with transaction.atomic():
            reference_organization = OrganizationDetail.objects.filter(ref_org_id=organization_id) 
            if reference_organization:
                reference_organization.name = name
                reference_organization.created_by = created_by  
                reference_organization.save()
                print(f"Organization updated: {organization_id}, {user_id}, {email}, {name}")
            else:
                print(f"Organization with ID {organization_id} not found. No update performed.")
                    
    except Exception as e:
        print(f"An error occurred while updating OrganizationDetail: {str(e)}")
        
        # If both organization_id and user_id are provided, update the UserDetail to reflect the organization change
    if organization_id and user_id:
        try:
            with transaction.atomic():
                updated_row = UserDetail.objects.filter(user=user_id).update(organization=organization_id)
                if updated_row > 0 :
                    print(f"UserDetail updated for user {user_id} with organization {organization_id}")
                else:
                    print(f"No UserDetail found for user {user_id} to update.")
        except Exception as e:
            print(f"An error occurred while updating UserDetail organization: {str(e)}")   

def handle_organization_deleted(event_data):
   
    """
    Handles the deletion of an organization by processing the provided event data.
    This function takes in event data containing the organization ID and deletes the corresponding OrganizationDetail entry.
    It also provides an optional example of how to handle cleanup of associated data, such as deleting or updating users associated with the organization.
    Parameters:
        event_data (dict): A dictionary containing the organization ID.
    Returns:
        None
    """
    organization_id = event_data['orgId']
    
    if not organization_id:
        raise ValueError("organization_id is required in event data")
    
    try:
        with transaction.atomic():
            # Retrieve and delete the organization
            organization = OrganizationDetail.objects.get(ref_org_id=organization_id)
            organization.delete()
            print(f"Organization deleted for organization_id: {organization_id}")
            
            # # Optional: If you need to handle cleanup of associated data, do it here
            # # Example: Deleting or updating users associated with this organization
            # UserDetail.objects.filter(organization=organization_id).delete()
            # print(f"Associated users deleted for organization_id: {organization_id}")

    except ObjectDoesNotExist:
        print(f"Organization with ID {organization_id} does not exist")
    except Exception as e:
        print(f"An error occurred while deleting the organization: {str(e)}")

def handle_org_user_created(event_data):
    
    """
    Handles the creation of an organization user by processing the provided event data.
    This function takes in event data containing the user ID, email, first name, last name, contact number, admin status, staff status, organization ID, created by, and user type.
    It creates or updates the corresponding UserReference entry, and also provides an optional example of how to handle cleanup of associated data, such as creating or updating user details associated with the organization.
    Parameters:
        event_data (dict): A dictionary containing the required event data.
    Returns:
        None
    """

    user_id = event_data['userId']
    # Ensure user_id is provided
    if not user_id:
        raise ValueError("user_id is required in event data")
    
    email = event_data['email']
    first_name = event_data['firstName'] 
    last_name = event_data['lastName']
    contact_number = event_data['contactNumber']
    is_admin = event_data['isAdmin']
    is_staff = event_data['isStaff'] 
    organization = event_data['organizationId'] 
    created_by = event_data['createdBy'] 
    user_type = event_data['userType'] 
    # Create or update the UserReference entry
    try:
        with transaction.atomic():
            user_reference, created = CustomUser.objects.get_or_create(
                user_ref_id=user_id,
                defaults={
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'is_admin': is_admin,
            'is_staff': is_staff,
            
            
            })
            if created:
                # Log the creation if necessary
                print(f"UserReference created: {user_reference}")
                UserDetail.objects.update_or_create(
                            user=user_reference,
                            defaults={
                                'contact_number': contact_number,
                                'user_type': user_type,
                                'organization': organization,
                                'created_by': created_by
                            }
        )
    except Exception as e:
         print(f"An error occurred while creating UserReference: {str(e)}") 
         
         
         
def handle_org_user_updated(event_data):
    user_id = event_data['userId']
    # Ensure user_id is provided
    if not user_id:
        raise ValueError("user_id is required in event data")
    
    email = event_data['email']
    first_name = event_data['firstName'] 
    last_name = event_data['lastName']
    contact_number = event_data['contactNumber']
    is_admin = event_data['isAdmin']
    is_staff = event_data['isStaff'] 
    organization = event_data['organizationId'] 
    created_by = event_data['createdBy'] 
    user_type = event_data['userType']
    
    try:
        with transaction.atomic():
            custom_user_reference = CustomUser.objects.get(user_ref_id=user_id)
            if custom_user_reference:
                custom_user_reference.email = email
                custom_user_reference.first_name = first_name
                custom_user_reference.last_name = last_name
                custom_user_reference.is_admin = is_admin
                custom_user_reference.is_staff = is_staff
                custom_user_reference.save()
                print(f"User updated: {custom_user_reference}")
            else:
                print(f"User not found for user_id: {user_id}")
                # Update the UserDetail entry
            user_detail = UserDetail.objects.get(user=custom_user_reference)
            if user_detail:
                user_detail.contact_number = contact_number
                user_detail.organization = organization
                user_detail.user_type = user_type
                user_detail.created_by = created_by
                user_detail.save()
                print(f"UserDetail updated: {user_detail}")
            else:
                print(f"UserDetail not found for user: {custom_user_reference}")    
    except Exception as e:
        print(f"An error occurred while updating UserReference: {str(e)}")                   
             

def handle_org_user_deleted(event_data):
    """
    Handles the deletion of an organization user by processing the provided event data.
    This function takes in event data containing user ID and deletes the corresponding UserReference entry.
    Additionally, it clears all group memberships for the user and deletes the user.
    If the group has no other users, it also deletes the group and its associated permissions.
    Parameters:
        event_data (dict): A dictionary containing user ID.
    Returns:
        JsonResponse with status code 200 if successful, 404 if user does not exist, or 500 if an error occurs.
    """
    user_id = event_data['userId']
    if not user_id:
        raise ValueError("user_id is required in event data")
    try:
        with transaction.atomic():
            # Fetch the user
            try:
                user = CustomUser.objects.get(ref_user_id=user_id)
            except CustomUser.DoesNotExist:
                return JsonResponse({'error': f"User with ID {user_id} does not exist"}, status=404)
            
            # Get all groups associated with the user
            groups = user.groups.all()

            # Clear all group memberships for the user
            user.groups.clear()

            # Delete the user
            user.delete()

            # Optionally delete groups and permissions if no other users are in those groups
            # for group in groups:
            #     if group.user_set.count() == 0:  # Check if the group has no other users
            #         group.permissions.clear()  # Clear the group's permissions
            #         group.delete()  # Delete the group itself

            print(f"User with ID {user_id} and associated groups and permissions deleted successfully.")
            return JsonResponse({'status': 'User and associated data deleted successfully'}, status=200)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
                          
# from django.views.decorators.csrf import csrf_exempt


def handle_role_created(event_data):
    # event_data = json.loads(request.body.decode('utf-8'))  # Load the incoming JSON data

    
    """
    Handles the creation of a role by processing the provided event data.

    This function takes in event data containing user ID, group ID, name, organization ID, and permissions.
    It creates a new group if the group ID does not exist, adds the user to the new group, and updates the group permissions.

    Args:
        event_data (dict): A dictionary containing user ID, group ID, name, organization ID, and permissions.

    Returns:
        JsonResponse with status code 200 if successful, 404 if user or organization does not exist, or 500 if an error occurs.
    """
    user_id = event_data['userId']
    group_id = event_data['groupId']
    name = event_data.get('name', '')
    organization_id = event_data['organization']
    permissions = event_data.get('permissions', [])

    try:
        with transaction.atomic():
            # Fetch the user
            try:
                user = CustomUser.objects.get(user_ref_id=user_id)
            except ObjectDoesNotExist:
                return JsonResponse({'error': f"User with ID {user_id} does not exist"}, status=404)
                
            # Fetch the organization
            try:
                organization = OrganizationDetail.objects.get(ref_org_id=organization_id)
            except ObjectDoesNotExist:
                return JsonResponse({'error': f"Organization with ID {organization_id} does not exist"}, status=404)
            
            # Fetch or create the group
            group, created = Group.objects.get_or_create(id=group_id, defaults={'name': name})
            if created:
                print(f"Created new group with ID {group_id}")

            # Check if the user is already in the group
            if not user.groups.filter(id=group_id).exists():
                # Remove the user from all existing groups
                # user.groups.clear()
                # Add the user to the new group
                user.groups.add(group)

            # Update group permissions
            existing_permissions = set(group.permissions.all())
            new_permissions = set()

            for perm_codename in permissions:
                try:
                    permission = Permission.objects.get(codename=perm_codename)
                    new_permissions.add(permission)
                except Permission.DoesNotExist:
                    print(f"Permission {perm_codename} does not exist")

            # Update the permissions for the group
            if existing_permissions != new_permissions:
                group.permissions.set(new_permissions)
                print(f"Updated group ID {group_id} for user ID {user_id} with permissions {permissions}")

        return JsonResponse({'status': 'Role and permissions updated successfully'}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

# {
#     "userId": 1,
#     "groupId": 3,
#     "name": "Manager",
#     "organization": 2,
#     "permissions": ["add_contact", "view_contact", "change_contact", "delete_contact"]
# }


def handle_suscription_created(event_data):
    # event_data = json.loads(request.body.decode('utf-8'))  # Load the incoming JSON data  
    subscription_id = event_data.get('subscription_id')
    organization_id = event_data.get('organization_id')
    suscription_created = event_data.get('suscription_created')
    suscription_end = event_data.get('suscription_end')
    suscription_is_expired = event_data.get('suscription_is_expired')
    
    if not organization_id:
        raise ValueError("organization_id is required for suscription")
    try:
        with transaction.atomic():
            subscritpion, created = SuscriptionDetail.objects.get_or_create( ref_suscription_id=subscription_id, defaults={
                'organization': organization_id,
                'suscription_created': suscription_created,
                'suscription_end': suscription_end,
                'is_expired': suscription_is_expired
            } )
            subscritpion.save()
            
            if created:
                print(f"Created new suscription for {organization_id} with ID {subscription_id}")
    except Exception as e:
        print(f"Error creating suscription: {str(e)}")      
    

def handle_chat_service_enabled(event_data):
    app_id = event_data.get('app_id')
    organization = event_data.get('organization')
    chat_enabled = event_data.get('chat_enabled')
    
    if not app_id:
        raise ValueError("app_id is required for chatenable")
    try:
        with transaction.atomic():
            app, created = ApplicationDetail.objects.get_or_create( ref_app_id=app_id, defaults={
                organization: organization,
                chat_enabled: chat_enabled
            })
            
            app.save()
            if created:
                print(f"Created new app for {organization} with ID {app_id}")
    except Exception as e:
        print(f"Error creating applicationdetail: {str(e)}")        