from .models import Blog, Comment, User
from django.utils import timezone

def notifications(request):
    if not request.user.is_authenticated:
        return {}
    user = request.user
    # Get blogs authored by the user
    blogs = Blog.objects.filter(author=user)
    # Get recent comments and likes on user's blogs (excluding self)
    comment_notifs = Comment.objects.filter(blog__in=blogs).exclude(user=user).order_by('-commented_at')[:20]
    like_notifs = []
    for blog in blogs:
        for like in blog.like_set.exclude(user=user).order_by('-id')[:20]:
            like_notifs.append({
                'type': 'like',
                'user': like.user,
                'blog': blog,
                'created_at': like.created_at if hasattr(like, 'created_at') else timezone.now(),
            })
    notifications = []
    for c in comment_notifs:
        notifications.append({
            'type': 'comment',
            'user': c.user,
            'blog': c.blog,
            'created_at': c.commented_at,
        })
    notifications.extend(like_notifs)
    cleared_at = request.session.get('notifications_cleared_at')
    if cleared_at:
        from django.utils.dateparse import parse_datetime
        cleared_dt = parse_datetime(cleared_at)
        notifications = [n for n in notifications if n['created_at'] > cleared_dt]
    notifications = sorted(notifications, key=lambda n: n['created_at'], reverse=True)[:20]
    return {'notifications': notifications}
