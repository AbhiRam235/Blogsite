from django.views.decorators.http import require_POST

from django.urls import reverse

from django.shortcuts import render, get_object_or_404
from .models import Blog, BlogBlock, User
from django.contrib.auth.decorators import login_required
from .forms import EditProfileForm
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from .forms import LoginForm, SignupForm

from .forms import BlogForm, BlogBlockForm
# ...existing code...

from django.http import JsonResponse, HttpResponseBadRequest
# ...existing code...

from django.http import HttpResponseForbidden

# Clear all notifications view

from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Blog, Comment
from django.utils import timezone

from django.contrib.auth.decorators import login_required

@login_required
def clear_notifications(request):
    # Mark all notifications as cleared for the user
    # For simplicity, we use session to track cleared time
    if request.method == 'POST':
        request.session['notifications_cleared_at'] = str(timezone.now())
        request.session.modified = True
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    return HttpResponseRedirect(reverse('home'))

@login_required
def follow_user(request, username):
    target_user = get_object_or_404(User, username=username)
    if request.method == 'POST' and target_user != request.user:
        if target_user in request.user.following.all():
            request.user.following.remove(target_user)
        else:
            request.user.following.add(target_user)
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('user_blogs', username=username)
    return HttpResponseForbidden()

@login_required
def like_blog(request, blog_id):
    if request.method == 'POST':
        blog = get_object_or_404(Blog, id=blog_id)
        like, created = blog.like_set.get_or_create(user=request.user)
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        return JsonResponse({'liked': liked, 'count': blog.like_set.count()})
    return HttpResponseBadRequest()

@login_required
def save_blog(request, blog_id):
    if request.method == 'POST':
        blog = get_object_or_404(Blog, id=blog_id)
        save, created = blog.save_set.get_or_create(user=request.user)
        if not created:
            save.delete()
            saved = False
        else:
            saved = True
        return JsonResponse({'saved': saved, 'count': blog.save_set.count()})
    return HttpResponseBadRequest()

@login_required
def edit_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug, author=request.user)
    blocks = BlogBlock.objects.filter(blog=blog).order_by('block_number')
    if request.method == 'POST':
        blog_form = BlogForm(request.POST, request.FILES, instance=blog)
        if blog_form.is_valid():
            blog_form.save()
            # Update blocks
            for i, block in enumerate(blocks, start=1):
                block_number = request.POST.get(f'block_number_{i}')
                content_type = request.POST.get(f'content_type_{i}')
                content = request.POST.get(f'content_{i}')
                image = request.FILES.get(f'image_{i}')
                if block_number and content_type:
                    block.block_number = block_number
                    block.content_type = content_type
                    block.content = content if content_type != 'image' else ''
                    if content_type == 'image' and image:
                        block.image = image
                    elif content_type != 'image':
                        block.image = None
                    block.save()
            return redirect('blog_detail', slug=blog.slug)
    else:
        blog_form = BlogForm(instance=blog)
    return render(request, 'edit_blog.html', {'blog_form': blog_form, 'blog': blog, 'blocks': blocks})

@login_required
def write_blog(request):
    if request.method == 'POST':
        blog_form = BlogForm(request.POST, request.FILES)
        if blog_form.is_valid():
            blog = blog_form.save(commit=False)
            blog.author = request.user
            blog.save()
            # Handle multiple blocks
            block_count = 0
            while True:
                block_number = request.POST.get(f'block_number_{block_count+1}')
                content_type = request.POST.get(f'content_type_{block_count+1}')
                content = request.POST.get(f'content_{block_count+1}')
                image = request.FILES.get(f'image_{block_count+1}')
                if not block_number or not content_type:
                    break
                block = BlogBlock(
                    blog=blog,
                    block_number=block_number,
                    content_type=content_type,
                    content=content if content_type != 'image' else '',
                    image=image if content_type == 'image' else None
                )
                block.save()
                block_count += 1
            return redirect('blog_detail', slug=blog.slug)
    else:
        blog_form = BlogForm()
    return render(request, 'write_blog.html', {'blog_form': blog_form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('home')

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=user)
    return render(request, 'edit_profile.html', {'form': form, 'user': user})


def home(request):
    query = request.GET.get('q', '').strip()
    blogs_qs = Blog.objects.prefetch_related('blocks').all()
    if query:
        blogs_qs = blogs_qs.filter(title__icontains=query) | blogs_qs.filter(blocks__content__icontains=query)
        blogs_qs = blogs_qs.distinct()
    blogs = blogs_qs

    for blog in blogs:
        text_block = next((block for block in blog.blocks.all() if block.content_type == 'text'), None)
        blog.preview_content = text_block.content if text_block else ""
        blog.like_count = blog.like_set.count()
        blog.save_count = blog.save_set.count()
        blog.comment_count = blog.comment_set.count() if hasattr(blog, 'comment_set') else 0

    return render(request, 'home.html', {'blogs': blogs, 'query': query})


def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    blog_blocks = BlogBlock.objects.filter(blog=blog).order_by('id')
    more_blogs = Blog.objects.filter(author=blog.author).exclude(id=blog.id).order_by('-created_at')[:4]
    for b in more_blogs:
        text_block = next((block for block in b.blocks.all() if block.content_type == 'text'), None)
        b.description = text_block.content if text_block else ""

    # Recommended blogs using recommendations.py
    try:
        from .recommendations import recommend_blogs
        recommended_blogs = recommend_blogs(blog, top_n=4)
    except Exception:
        recommended_blogs = []

    # Handle comment form submission
    if request.method == 'POST' and request.user.is_authenticated:
        comment_text = request.POST.get('comment_content', '').strip()
        if comment_text:
            from .models import Comment
            Comment.objects.create(blog=blog, user=request.user, comment=comment_text)
            return redirect('blog_detail', slug=blog.slug)

    # Get all comments for this blog
    comments = blog.comment_set.select_related('user').order_by('-commented_at')

    return render(request, 'blog.html', {
        'blog': blog,
        'blog_blocks': blog_blocks,
        'more_blogs': more_blogs,
        'comments': comments,
        'recommended_blogs': recommended_blogs,
    })


def user_blogs(request, username):
    author = get_object_or_404(User, username=username)
    followers_count = author.followers.count()
    query = request.GET.get('q', '').strip()
    blogs_qs = Blog.objects.filter(author=author).order_by('-created_at').prefetch_related('blocks')
    if query:
        blogs_qs = blogs_qs.filter(title__icontains=query) | blogs_qs.filter(blocks__content__icontains=query)
        blogs_qs = blogs_qs.distinct()
    blogs = blogs_qs.all()

    for blog in blogs:
        text_block = next((block for block in blog.blocks.all() if block.content_type == 'text'), None)
        blog.preview_content = text_block.content if text_block else ""
    # You can add logic for pinned blogs and about info if needed

    return render(request, 'user_blogs.html', {
        'author': author,
        'blogs': blogs,
        'followers_count': followers_count,
    })


@login_required
def profile(request):
    user = request.user
    user_blogs = Blog.objects.filter(author=user).order_by('-created_at')
    saved_blog_ids = user.save_set.values_list('blog_id', flat=True)
    saved_blogs = Blog.objects.filter(id__in=saved_blog_ids).order_by('-created_at')
    followers = user.followers.all()
    following = user.following.all()
    return render(request, 'profile.html', {
        'user': user,
        'user_blogs': user_blogs,
        'saved_blogs': saved_blogs,
        'followers': followers,
        'following': following,
    })


# Delete blog view
@login_required
@require_POST
def delete_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug, author=request.user)
    blog.delete()
    return redirect('profile')


