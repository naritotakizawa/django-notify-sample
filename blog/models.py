from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models
from django.shortcuts import resolve_url
from django.template.loader import render_to_string
from django.utils import timezone
import linebot
from linebot.models import TextSendMessage
import requests


class Post(models.Model):
    title = models.CharField('タイトル', max_length=255)
    text = models.TextField('本文')
    created_at = models.DateTimeField('作成日', default=timezone.now)

    def __str__(self):
        return self.title

    def email_push(self, request):
        """記事をメールで通知"""
        context = {
            'post': self,
        }
        subject = render_to_string('blog/notify_subject.txt', context, request)
        message = render_to_string('blog/notify_message.txt', context, request)

        from_email = settings.DEFAULT_FROM_EMAIL
        bcc = [settings.DEFAULT_FROM_EMAIL]
        for mail_push in EmailPush.objects.filter(is_active=True):
            bcc.append(mail_push.email)
        email = EmailMessage(subject, message, from_email, [], bcc)
        email.send()

    def line_push(self, request):
        """記事をラインで通知"""
        context = {
            'post': self,
        }
        message = render_to_string('blog/notify_message.txt', context, request)
        line_bot_api = linebot.LineBotApi('発行したアクセストークン')
        for push in LinePush.objects.all():
            line_bot_api.push_message(push.user_id, messages=TextSendMessage(text=message))

    def browser_push(self, request):
        """記事をブラウザ通知"""
        data = {
            'app_id': 'あなたのAPP ID',
            'included_segments': ['All'],
            'contents': {'en': self.title},
            'headings': {'en': 'Naritoブログ'},
            'url': resolve_url('blog:detail', pk=self.pk),
        }
        requests.post(
            "https://onesignal.com/api/v1/notifications",
            headers={'Authorization': 'Basic あなたのREST API Key'},
            json=data,
        )


class EmailPush(models.Model):
    """メールでのプッシュ先を表す"""
    email = models.EmailField('メールアドレス', unique=True)
    is_active = models.BooleanField('有効フラグ', default=False)

    def __str__(self):
        return self.email


class LinePush(models.Model):
    """Lineでのプッシュ先を表す"""
    user_id = models.CharField('ユーザーID', max_length=100, unique=True)

    def __str__(self):
        return self.user_id
