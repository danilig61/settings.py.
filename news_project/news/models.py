from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.models import User
from django.db import models
from django.contrib.contenttypes.models import ContentType
from .models import Category
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.template.loader import render_to_string




class CategorySubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'category')

class Category(models.Model):
    name = models.CharField(max_length=100)
    subscribers = models.ManyToManyField(User, related_name='subscribed_categories')

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return self.title

content_type = ContentType.objects.get_for_model(Post)
permission, created = Permission.objects.get_or_create(
    codename='add_post',
    name='Can add post',
    content_type=content_type,
)
permission, change = Permission.objects.get_or_create(
    codename='change_post',
    name='Can change post',
    content_type=content_type,
)

authors_group = Group.objects.get(name='authors')
authors_group.permissions.add(permission, created)
authors_group.permissions.add(permission, change)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()

    def __str__(self):
        return self.user.username


class User(AbstractUser):
    email = models.EmailField(unique=True)
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='news_user_groups',
        related_query_name='news_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='news_user_permissions',
        related_query_name='news_user',
    )

    def __str__(self):
        return self.username

    subscribed_categories = models.ManyToManyField(Category, related_name='subscribers', blank=True)

class Article(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    pub_date = models.DateTimeField('date published')
    content = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self):
        super().clean()
        today = timezone.now().date()
        if Article.objects.filter(author=self.author, created_at__date=today).count() >= 3:
            raise ValidationError('Вы не можете создавать более трех новостей в день.')

    def send_notifications(self):
        subject = self.title
        message = render_to_string('email/article_notification.html', {'article': self})
        recipient_list = [user.email for user in self.category.subscribers.all()]
        send_mail(subject, message, 'ignatevdaniil161@gmail.com', recipient_list, html_message=message)

    def __str__(self):
        return self.title

class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=50)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title

class NewsPermission(Permission):
    class Meta:
        proxy = True
        verbose_name = 'news permission'
        verbose_name_plural = 'news permissions'