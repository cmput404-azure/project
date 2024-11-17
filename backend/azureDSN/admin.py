import re
from urllib.parse import urlparse
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

class ConnectionStatusFilter(admin.SimpleListFilter):
    title = 'Connection Status'
    parameter_name = 'connection_status'

    def lookups(self, request, model_admin):
        return (
            ('connected', 'Connected'),
            ('not_connected', 'Not Connected'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'connected':
            return queryset.filter(is_authenticated=True)
        if self.value() == 'not_connected':
            return queryset.filter(is_authenticated=False)
        return queryset

# Need this for inline editing in Django Admin panel
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ('id', 'require_approval')
    list_editable = ('require_approval',)

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'type', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username', 'type')
    readonly_fields = ('created_at', 'modified_at')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'display_name', 'bio', 'github', 'page', 'profile_image', "host")}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'modified_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

    ordering = ('username',)
    actions = ['approve_users']

    # This function is so that Admins can bulk approve new users
    def approve_users(self, request, queryset):
        queryset.update(is_active=True)
    approve_users.short_description = "Approve selected users"

class NodeUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'password', 'host', 'get_connection_status')
    actions = ['authenticate_nodes', 'deauthenticate_nodes']
    list_filter = (ConnectionStatusFilter,)

    def get_connection_status(self, obj):
        return "ALLOWED" if obj.is_authenticated else "NOT ALLOWED"
    get_connection_status.short_description = "Connection Status"

    def authenticate_nodes(self, request, queryset):
        """
        To authenticate connections (set `is_authenticated=True`).
        Allow activities to be shared from selected nodes.
        """
        queryset.update(is_authenticated=True)
        self.message_user(request, f"{queryset.count()} node(s) have been connected.")
    authenticate_nodes.short_description = "Allow activities from selected nodes"

    def deauthenticate_nodes(self, request, queryset):
        """
        To break/stop connections (set `is_authenticated=False`).
        Disallow activities to be shared from selected nodes.
        """
        queryset.update(is_authenticated=False)
        self.message_user(request, f"{queryset.count()} node(s) have been disconnected.")
    deauthenticate_nodes.short_description = "Reject activities from selected nodes"

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'content_type', 'visibility')
    search_fields = ('title', 'user')
    readonly_fields = ('created_at', 'modified_at')
    list_filter = ('visibility', 'content_type')

class InboxItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'object_id', 'content_type')

class LikeAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'post', 'get_user_display_name')

    def get_user_display_name(self, obj):
        # Safely access display_name within user JSON field
        return obj.user.get('displayName', 'No Name')
    get_user_display_name.short_description = 'Liked by'

class CommentAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'post', 'get_user_display_name')

    def get_user_display_name(self, obj):
        return obj.user.get('displayName', 'Error: No Name')
    get_user_display_name.short_description = 'Commented by' 

class ShareAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'get_post_host', 'get_post_uuid', 'get_local_receiver')

    def get_user(self, obj):
        return obj.user
    get_user.short_description = "Local Sharer"

    def get_post_host(self, obj):
        # Parse and return the host from the post URL
        parsed_url = urlparse(obj.post)
        return f"{parsed_url.scheme}://{parsed_url.netloc}"
    get_post_host.short_description = 'Post Origin'
    
    def get_post_uuid(self, obj):
        # Extract and return the UUID from the post URL
        match = re.search(r'posts/([a-f0-9-]+)', obj.post)
        return match.group(1) if match else "No UUID"
    get_post_uuid.short_description = 'Shared Post UUID'

    def get_local_receiver(self, obj):
        return obj.receiver
    get_local_receiver.short_description = "Local Receiver"

class FollowRequestAdmin(admin.ModelAdmin):
    list_display = ('get_request_target', 'get_request_sender', 'get_request_origin')

    def get_request_target(self, obj):
        return obj.object
    get_request_target.short_description = "Request Sent To"

    def get_request_sender(self, obj):
        return obj.actor.get('displayName', 'Error: No Name')
    get_request_sender.short_description = "Sent by"
    
    def get_request_origin(self, obj):
        return obj.actor.get('host', 'Error: No Host')
    get_request_origin.short_description = 'Request Origin'

class FollowAdmin(admin.ModelAdmin):
    list_display = ('get_followee', 'get_follower', 'get_followee_origin', 'get_follower_origin')

    def get_followee(self, obj):
        if obj.local_followee:
            return obj.local_followee
        else:
            match = re.search(r'authors/([a-f0-9-]+)', obj.remote_followee)
            return match.group(1) if match else "Error: No UUID"
    get_followee.short_description = "Followee"

    def get_follower(self, obj):
        if obj.local_follower:
            return obj.local_follower
        else:
            match = re.search(r'authors/([a-f0-9-]+)', obj.remote_follower)
            return match.group(1) if match else "Error: No UUID"
    get_follower.short_description = "Follower"

    def get_followee_origin(self, obj):
        if obj.local_followee:
            return "LOCAL"
        else:
            parsed_url = urlparse(obj.remote_followee)
            return f"{parsed_url.scheme}://{parsed_url.netloc}"
    get_followee_origin.short_description = "Followee Origin"

    def get_follower_origin(self, obj):
        if obj.local_follower:
            return "LOCAL"
        else:
            parsed_url = urlparse(obj.remote_follower)
            return f"{parsed_url.scheme}://{parsed_url.netloc}"
    get_follower_origin.short_description = "Follower Origin"

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(NodeUser, NodeUserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(FollowRequest, FollowRequestAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Inbox)
admin.site.register(InboxItem, InboxItemAdmin)
admin.site.register(SiteConfiguration, SiteConfigurationAdmin)
admin.site.register(Share, ShareAdmin)

