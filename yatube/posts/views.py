from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


def get_page_context(queryset, page):
    paginator = Paginator(queryset, settings.POSTS_IN_PAGE)
    page_obj = paginator.get_page(page)
    return page_obj


@cache_page(20, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    posts = Post.objects.select_related('author', 'group')
    context = {
        'page_obj': get_page_context(posts, request.GET.get('page')),
    }
    return render(request, template, context)


def group_post(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    context = {
        'group': group,
        'page_obj': get_page_context(posts, request.GET.get('page')),
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group')
    flag = True if request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=author) else False
    context = {
        'author': author,
        'following': flag,
        'page_obj': get_page_context(posts, request.GET.get('page')),
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = (
        get_object_or_404
        (Post.objects.select_related('author', 'group'), pk=post_id)
    )
    comments = post.comments.select_related('author')
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None,
                    files=request.FILES or None,)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:profile', post.author.username)
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = (
        get_object_or_404
        (Post.objects.select_related('author', 'group'), pk=post_id)
    )
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post,)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.id)
    return render(request, template, {'form': form, 'is_edit': True, })


@login_required
def add_comment(request, post_id):
    post = (
        get_object_or_404
        (Post.objects.select_related('author', 'group'), pk=post_id)
    )
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    authors = request.user.follower.values_list('author', flat=True)
    posts = (Post.objects.filter(
        author__id__in=authors).select_related('author', 'group'))
    context = {
        'page_obj': get_page_context(posts, request.GET.get('page')),
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author).exists()
    if request.user != author and follow is False:
        Follow.objects.create(user=request.user, author=author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    following = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user,
        author=following).delete()
    return redirect('posts:profile', username=username)