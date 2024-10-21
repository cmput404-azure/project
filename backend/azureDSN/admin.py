from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username')
    readonly_fields = ('created_at', 'modified_at')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'display_name', 'github', 'page', 'profile_image', "host")}),
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


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(FollowRequest)
admin.site.register(Follow)
admin.site.register(Inbox)
admin.site.register(InboxItem)

