from rest_framework.permissions import DjangoModelPermissions
from rest_framework.permissions import BasePermission


class IsAdminOrOrgUser(BasePermission):
    
    def has_permission(self, request, view):
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Allow access if the user is an admin or staff
        if request.user.is_admin:
            return True
        
        # Deny access by default for other users
        return False
    
    def has_object_permission(self, request, view, obj):
        # If the user is an admin, grant all access
        if request.user.is_admin:
            return True
        
        
        return obj.user == request.user 


class FullDjangoModelPermissions(DjangoModelPermissions):
    
    def __init__(self):
        
        """
        Constructor to initialize the permissions map

        This method initializes the permissions map for the given view. It
        inherits the permissions map from the DjangoModelPermissions class and
        overrides the default permissions map to include the 'view' permission
        for the GET method.

        :return: None
        """
        super().__init__()
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
        self.perms_map['OPTIONS'] = []
        self.perms_map['HEAD'] = []
        self.perms_map['POST'] = ['%(app_label)s.add_%(model_name)s']
        self.perms_map['PUT'] = ['%(app_label)s.change_%(model_name)s']
        self.perms_map['PATCH'] = ['%(app_label)s.change_%(model_name)s']
        self.perms_map['DELETE'] = ['%(app_label)s.delete_%(model_name)s']
        
    def has_permission(self, request, view):
        """
        Checks if the request user has the required permissions to access the given view.

        This method checks if the request user has the required permissions to access the given view.
        It inherits the has_permission method from the DjangoModelPermissions class and overrides the
        default behavior to include the 'view' permission for the GET method.

        :param request: The request object
        :param view: The view object
        :return: True if the user has permission, False otherwise
        """
        user = request.user
        print(f"User: {user}")
        print(f"User permissions: {user.get_all_permissions()}")

        queryset = self._queryset(view)
        perms = self.get_required_permissions(request.method, queryset.model)
        print(f"Required permissions: {perms}")

        has_perm = super().has_permission(request, view)
        print(f"Has permission: {has_perm}")
        return has_perm

    def has_perm(self, perm, obj=None):
        '''
        Checks if the request user has a specific permission.

        This method checks if the request user has a specific permission. If the user is an
        admin, it returns True immediately. Otherwise, it checks if the permission is in the
        set of permissions retrieved by the get_all_permissions method.

        :param perm: The permission to check
        :param obj: The object related to the permission (optional)
        :return: True if the user has the permission, False otherwise
        '''
        if self.is_admin:
            print(f"User {self.email} is admin: has all permissions.")
            return True
        has_permission = perm in self.get_all_permissions()
        print(f"User {self.email} has permission {perm}: {has_permission}")
        return has_permission
