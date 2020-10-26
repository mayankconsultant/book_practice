from django import template
from ..models import Post
from django.db.models import Count

register = template.Library()


from django.utils.safestring import mark_safe
import markdown

@register.simple_tag(name='most_commented_posts')
def get_most_commented_post(count=2):
    return Post.objects.annotate(total_comments=Count('comments') ).order_by('-total_comments')[:count]


@register.simple_tag
def total_posts(published=0):
    print('Value of published ' + str(published))
    if published >0 :
        print ('published '  + str(Post.published.count()))
        return 'Published ' + str (Post.published.count() )
    else :
        print('Written ' + str(Post.objects.filter(status='draft').count()))
    return 'Written ' + str(Post.objects.filter(status='draft').count())

@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=2,published=True):
    if published:
        latest_posts = Post.published.order_by('-publish')[:count]
    else:
        latest_posts = Post.objects.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))