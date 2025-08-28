from django.contrib import admin
from .models import User, Blog, Comment, Like, BlogBlock, Save
from .forms import BlogBlockInlineForm

class BlogBlockInline(admin.StackedInline):
    model = BlogBlock
    form = BlogBlockInlineForm
    extra = 0

class BlogAdmin(admin.ModelAdmin):
    inlines = [BlogBlockInline]
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(User)
admin.site.register(Blog, BlogAdmin)
admin.site.register(Comment)
admin.site.register(Save)
admin.site.register(Like)

