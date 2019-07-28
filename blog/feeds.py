from django.contrib.syndication.views import Feed
from django.shortcuts import resolve_url
from django.urls import reverse_lazy
from .models import Post


class LatestPostFeed(Feed):
    title = "naritoブログ 最新記事"
    link = reverse_lazy('blog:list')
    description = "naritoブログから、記事の最新情報をお届けします。"

    def items(self):
        return Post.objects.order_by('-created_at')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.text[:10]  # 本文の20文字目までをとりあえず説明に。

    def item_link(self, item):
        return resolve_url('blog:detail', pk=item.pk)
