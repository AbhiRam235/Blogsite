from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import uuid

class User(AbstractUser):
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    ROLE_CHOICES = [
        ('reader', 'Reader'),
        ('writer', 'Writer'),
        ('both', 'Both'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='reader')
    bio = models.TextField()
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


class Blog(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogs')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    cover_image = models.ImageField(upload_to='blog_covers/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    topics = models.JSONField(default=list, blank=True)

    def save(self, *args, **kwargs):
        if self.topics and len(self.topics) > 5:
            self.topics = self.topics[:5]
        if not self.slug:
            self.slug = slugify(f"{self.title}-{uuid.uuid4().hex[:6]}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



class BlogBlock(models.Model):
    blog = models.ForeignKey('Blog', on_delete=models.CASCADE, related_name='blocks')
    block_number = models.PositiveIntegerField()
    
    content_type = models.CharField(max_length=50, choices=[
        ('text', 'Text'),
        ('image', 'Image'),
        ('code', 'Code'),
        ('youtube', 'YouTube')
    ])
    
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='blog_blocks/', blank=True, null=True)

    class Meta:
        ordering = ['block_number']

    def __str__(self):
        return f"Block {self.block_number} of {self.blog.title}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'blog')

class Save(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'blog')

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    comment = models.TextField()
    commented_at = models.DateTimeField(auto_now_add=True)
