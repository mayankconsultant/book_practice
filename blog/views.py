from django.shortcuts import render, get_object_or_404
from .models import Post, comment
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger

from django.views.generic import    ListView

from .forms import EmailForm, CommentsForm

from taggit.models import Tag

from django.db.models import Count

# Create your views here.


def post_list(request,tag_slug=None):
    object_list =Post.objects.all()
    tag= None
    if tag_slug:
        tag= get_object_or_404(Tag,slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])


    paginator = Paginator(object_list,2)
    page = request.GET.get('page')

    try:
        posts =paginator.page(page)

    except PageNotAnInteger:
        posts=paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    # print(posts.count())
    return render(request,'blog/post/list.html',{'page':page,'posts':posts,'tag':tag})

# class PostListView(ListView):
#     queryset = Post.objects.all()
#     # model = Post
#
#     context_object_name='posts'
#     paginate_by = 2
#     template_name = "blog/post/list.html"

def post_detail(request,year,month,day,post):
    post = get_object_or_404(Post,slug=post,
                                          publish__year=year,
                                          publish__month=month,
                                          publish__day=day)

    # comments = comment.objects.filter(active=True)
    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method =='POST':
        form = CommentsForm(data=request.POST)
        if form.is_valid():
            print('in comments form' )
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        form = CommentsForm()

    post_tags_ids = post.tags.values_list('id', flat=True)

    similar_posts = Post.objects.filter(tags__in=post_tags_ids).exclude(id=post.id)

    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]


    return render(request,'blog/post/detail.html',{'post':post,'comments':comments,'new_comment':new_comment,'form':form,'similar_posts': similar_posts})




def post_share(request,post_id):
    from django.core.mail import send_mail
    post = get_object_or_404(Post,id=post_id,status='published')
    sent = False
    if request.method =='POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"

            send_mail(subject, message, 'mayank.atyourwork@gmail.com',
                      [cd['to']])
            sent = True


    else :
        form = EmailForm()

    context = {'post': post, 'form': form, 'sent': sent}
    return render(request,'blog/post/share.html',context)