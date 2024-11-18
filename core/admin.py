from django.contrib import admin


# Register your models here.
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, UserDetail, OrganizationDetail, SubscriptionDetail
from django.shortcuts import get_object_or_404

class CustomUserAdmin(BaseUserAdmin):
    list_display = ( 'user_ref_id', 'email', 'first_name', 'last_name', 'is_staff', 'is_admin')
    list_filter = ('is_admin', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_admin', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'groups', 'user_permissions'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
    
    

admin.site.register(CustomUser, CustomUserAdmin)


class UserDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'user_type', 'contact_number', 'organization', 'created_by')
    search_fields = ('user__email', 'user_type', 'organization')
    list_filter = ('user_type', 'organization')

admin.site.register(UserDetail, UserDetailAdmin)

class OrganizationDetailAdmin(admin.ModelAdmin):
    list_display = ( 'ref_org_id', 'name', 'created_by')
    search_fields = ('ref_org_id', 'name')
    list_filter = ('name',)

admin.site.register(OrganizationDetail, OrganizationDetailAdmin)
admin.site.register(SubscriptionDetail)