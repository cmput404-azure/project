import re
from urllib.parse import urlparse
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

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
    list_display = ('username', 'host', 'password', 'is_authenticated')

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
        return obj.user.get('displayName', 'No Name')
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

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(NodeUser, NodeUserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(FollowRequest)
admin.site.register(Follow)
admin.site.register(Inbox)
admin.site.register(InboxItem, InboxItemAdmin)
admin.site.register(SiteConfiguration, SiteConfigurationAdmin)
admin.site.register(Share, ShareAdmin)

