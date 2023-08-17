from django.core.paginator import Paginator
from django.db.models import Q
from . import models
from .models import News, Article, Post, UserProfile, Category, CategorySubscription
from .forms import NewsForm, ArticleForm, SignupForm
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.models import Group, User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, DetailView
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model, authenticate, login
from .forms import SignUpForm
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone

def unsubscribe_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    request.user.subscribed_categories.remove(category)
    messages.success(request, f'Вы успешно отписались от категории "{category.name}".')
    return redirect('category_detail', pk=category.pk)

def subscribe_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    request.user.subscribed_categories.add(category)
    messages.success(request, f'Вы успешно подписались на категорию "{category.name}".')
    return redirect('category_detail', pk=category.pk)

def send_weekly_notifications(category):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    new_articles = Article.objects.filter(category=category, created_at__range=[week_ago, today])
    subscribers = category.subscribers.all()
    for subscriber in subscribers:
        subject = f'Новые статьи в категории "{category.name}" за последнюю неделю'
        message = render_to_string('email/weekly_notification.html', {'articles': new_articles})
        send_mail(subject, message, 'ignatevdaniil161@gmail.com', [subscriber.email], html_message=message)

def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            article.send_notifications()
            messages.success(request, 'Статья успешно создана.')
            return redirect('article_detail', pk=article.pk)
    else:
        form = ArticleForm()
    return render(request, 'news/create_article.html', {'form': form})

User = get_user_model()

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_welcome_email(user, request)
            return redirect('activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def send_welcome_email(user, request):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_link = f'{request.scheme}://{request.get_host()}/activate/{uidb64}/{token}/'
    subject = 'Добро пожаловать на наш сайт!'
    message = render_to_string('email/welcome_email.html', {'user': user, 'activation_link': activation_link})
    recipient_list = [user.email]
    send_mail(subject, message, 'ignatevdaniil161@gmail.com', recipient_list, html_message=message)

User = get_user_model()

def activate_account(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'registration/activation_success.html')
    else:
        return render(request, 'registration/activation_failure.html')

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'category_detail.html'

@login_required
def unsubscribe_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    subscription = get_object_or_404(CategorySubscription, user=request.user, category=category)
    subscription.delete()
    messages.success(request, f"You have unsubscribed from {category.name}.")
    return redirect('category_detail', pk=category.id)

@login_required
def subscribe_to_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.subscribers.add(request.user)
    return redirect('category_detail', pk=pk)

class Category(models.Model):
    name = models.CharField(max_length=100)
    subscribers = models.ManyToManyField(User, related_name='subscribed_categories')

    def send_notifications(self, article):
        subject = article.title
        message = render_to_string('email/notification.html', {'article': article, 'category': self})
        recipient_list = [user.email for user in self.subscribers.all()]
        send_mail(subject, message, 'ignatevdaniil161@gmail.com', recipient_list, html_message=message)

class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def test_func(self):
        return self.request.user.groups.filter(name='authors').exists()

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def test_func(self):
        return self.request.user.groups.filter(name='authors').exists()

class UserProfileUpdateView(UpdateView):
    model = UserProfile
    fields = ['first_name', 'last_name', 'email']
    template_name = 'profile.html'
    success_url = reverse_lazy('profile')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            if 'become_author' in request.POST:
                authors_group = Group.objects.get(name='authors')
                user.groups.add(authors_group)
                messages.success(request, 'Your request to become an author has been submitted.')
                return redirect('profile')

            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')

@login_required
class UserProfileUpdateView(UpdateView):
    model = UserProfile
    fields = ['first_name', 'last_name', 'email']
    template_name = 'profile.html'
    success_url = reverse_lazy('profile')

def news_list(request):
    news_list = News.objects.order_by('-published_date')
    paginator = Paginator(news_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news/news_list.html', {'page_obj': page_obj})


def news_detail(request, pk):
    news = get_object_or_404(News, pk=pk)
    return render(request, 'news/news_detail.html', {'news': news})


def news_create(request):
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.published_date = timezone.now()
            news.save()
            return redirect('news_detail', pk=news.pk)
    else:
        form = NewsForm()
    return render(request, 'news/news_form.html', {'form': form})


def news_edit(request, pk):
    news = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        form = NewsForm(request.POST, instance=news)
        if form.is_valid():
            news = form.save(commit=False)
            news.published_date = timezone.now()
            news.save()
            return redirect('news_detail', pk=news.pk)
    else:
        form = NewsForm(instance=news)
    return render(request, 'news/news_form.html', {'form': form})


def news_delete(pk):
    news = get_object_or_404(News, pk=pk)
    news.delete()
    return redirect('news_list')


def news_search(request):
    query = request.GET.get('q')
    if query:
        news_list = News.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        ).distinct()
    else:
        news_list = News.objects.all()
    paginator = Paginator(news_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news/news_search.html', {'page_obj': page_obj, 'query': query})

class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'article_update.html'
    success_url = reverse_lazy('article_list')

class ArticleUpdateView(UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'article_update.html'
    success_url = reverse_lazy('article_list')

class ArticleCreateView(CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'article_create.html'
    success_url = reverse_lazy('article_list')

class ArticleUpdateView(UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'article_update.html'
    success_url = reverse_lazy('article_list')

class SignupView(CreateView):
    template_name = 'registration/signup.html'
    form_class = SignupForm

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        common_group = Group.objects.get(name='common')
        common_group.user_set.add(user)
        return response

class AddAuthorView(View):
    def post(self, request):
        author_group = Group.objects.get(name='authors')
        author_group.user_set.add(request.user)
        return redirect('profile')