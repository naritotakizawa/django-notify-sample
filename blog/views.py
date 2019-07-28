import json
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from .forms import EmailForm
from .models import Post, EmailPush, LinePush


def subscribe(request):
    """ブログの購読ページ"""
    form = EmailForm(request.POST or None)
    # メール購読を申し込みした場合
    if request.method == 'POST' and form.is_valid():
        push = form.save()
        context = {
            'token': dumps(push.pk),
        }
        subject = render_to_string('blog/register_notify_subject.txt', context, request)
        message = render_to_string('blog/register_notify_message.txt', context, request)

        from_email = settings.DEFAULT_FROM_EMAIL
        to = [push.email]
        bcc = [settings.DEFAULT_FROM_EMAIL]
        email = EmailMessage(subject, message, from_email, to, bcc)
        email.send()

        return redirect('blog:subscribe_thanks')

    context = {
        'form': form,
    }

    return render(request, 'blog/subscribe.html', context)


def subscribe_thanks(request):
    """メール購読ありがとう、確認メール送ったよページ"""
    return render(request, 'blog/subscribe_thanks.html')


def subscribe_register(request, token):
    """メール購読の確認処理"""
    try:
        user_pk = loads(token, max_age=60*60*24)  # 1日以内

    # 期限切れ
    except SignatureExpired:
        return HttpResponseBadRequest()

    # tokenが間違っている
    except BadSignature:
        return HttpResponseBadRequest()

    # tokenは問題なし
    else:
        try:
            push = EmailPush.objects.get(pk=user_pk)
        except EmailPush.DoesNotExist:
            return HttpResponseBadRequest()
        else:
            if not push.is_active:
                # まだ仮登録で、他に問題なければ本登録とする
                push.is_active = True
                push.save()
                return redirect('blog:subscribe_done')

    return HttpResponseBadRequest()


def subscribe_done(request):
    """メール購読完了"""
    return render(request, 'blog/subscribe_done.html')


class PostIndex(generic.ListView):
    model = Post


class PostDetail(generic.DetailView):
    model = Post


@csrf_exempt
def callback(request):
    """ラインの友達追加時に呼び出され、ラインのIDを登録する。"""
    if request.method == 'POST':
        request_json = json.loads(request.body.decode('utf-8'))
        line_user_id = request_json['events'][0]['source']['userId']
        LinePush.objects.create(user_id=line_user_id)
    return HttpResponse()
