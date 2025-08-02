from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, Contact

from django.contrib import admin
from django.utils.html import format_html, mark_safe
from .models import UserProfile

class AccountAdmin(UserAdmin):
    last_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'phone', 'city', 'state', 'country', 'profile_image_tag')
    readonly_fields = ('profile_image_tag',)
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    list_filter = ('state', 'country')

    def email(self, obj):
        return obj.user.email

    def phone(self, obj):
        return obj.user.phone_number

    def profile_image_tag(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.profile_picture.url
            )
        return "No Image"

    profile_image_tag.short_description = 'Profile Picture'

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Contact)

