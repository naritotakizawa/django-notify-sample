from django.contrib import admin
from .models import Post, EmailPush, LinePush


def notify(modeladmin, request, queryset):
    for post in queryset:
        post.line_push(request)
        post.browser_push(request)
        post.email_push(request)


class PostAdmin(admin.ModelAdmin):
    actions = [notify]


notify.short_description = '通知を送信する'
admin.site.register(Post, PostAdmin)
admin.site.register(EmailPush)
admin.site.register(LinePush)
