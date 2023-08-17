from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from .views import send_weekly_notifications
from django.db.models.signals import m2m_changed
from django.core.mail import send_mail
from .models import Article, News, UserProfile
from django.dispatch import receiver
from .tasks import send_notification


@receiver(m2m_changed, sender=Article.categories.through)
def send_article_notification(sender, instance, action, **kwargs):
    if action == 'post_add':
        subscribers = []
        for category in instance.categories.all():
            subscribers += category.subscribers.all()

        subject = f'New article in categories: {", ".join(category.name for category in instance.categories.all())}'
        message = f'Check out the new article: {instance.title}'
        from_email = 'ignatevdaniil161@gmail.com'
        recipient_list = [subscriber.email for subscriber in subscribers]
        send_mail(subject, message, from_email, recipient_list)

@receiver(post_save, sender=Article)
def send_notifications(sender, instance, created, **kwargs):
    if created:
        send_weekly_notifications(instance.category)
        send_notification.delay(instance.id)

@receiver(post_save, sender=User)
def create_user_profile(instance, created):
    if created:
        UserProfile.objects.create(user=instance)
        group = Group.objects.get(name='authors')
        instance.groups.add(group)

