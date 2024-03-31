from django.contrib import admin
from . import models
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import WebsiteUser, Notification


class NotificationInline(admin.TabularInline):
    model = Notification
    extra = 0


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'middle_name', 'last_name', 'email', 'phone_number', 'prn_number', 'college_id_image', 'profile_image')}),
        (_('Permissions'), {'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_verified')  # Add 'is_verified' to list_display
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

admin.site.register(WebsiteUser, UserAdmin)

from .models import UploadedItem

# class UploadedItemAdmin(admin.ModelAdmin):
#     list_display = ('name', 'uploader', 'location')
#     search_fields = ('name', 'uploader__username', 'location')
#     list_filter = ('uploader', 'location')

# admin.site.register(UploadedItem, UploadedItemAdmin)

class AnswerInline(admin.TabularInline):
    model = models.Answer
    extra = 0
    readonly_fields = ['question', 'user', 'answer_text']

class QuestionInline(admin.TabularInline):
    model = models.Question
    extra = 0
    readonly_fields = ['text']

class UploadedItemAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'uploader', 'location', 'claimed')
    search_fields = ('name', 'uploader__username', 'location')
    list_filter = ('uploader', 'location', 'claimed')
    inlines = [QuestionInline, AnswerInline]

admin.site.register(UploadedItem, UploadedItemAdmin)
