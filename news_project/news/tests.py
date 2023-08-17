from django.test import TestCase
from django.utils import timezone
from .models import Article

class ArticleTestCase(TestCase):
    def create_articles(self):
        Article.objects.create(title='Новость 1', text='Текст первой новости', published_date=timezone.now())
        Article.objects.create(title='Новость 2', text='Текст второй новости', published_date=timezone.now())
        Article.objects.create(title='Новость 3', text='Текст третьей новости', published_date=timezone.now())
        Article.objects.create(title='Новость 4', text='Текст четвертой новости', published_date=timezone.now())
        Article.objects.create(title='Новость 5', text='Текст пятой новости', published_date=timezone.now())

    def test_articles_are_published(self):
        self.create_articles()
        response = self.client.get('/news/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Новость 1')
        self.assertContains(response, 'Новость 2')
        self.assertContains(response, 'Новость 3')
        self.assertContains(response, 'Новость 4')
        self.assertContains(response, 'Новость 5')