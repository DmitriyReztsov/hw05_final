from django.test import TestCase
from django.test import Client
from django.urls import reverse
import time
from django.core.files.uploadedfile import SimpleUploadedFile
import os  # для удаления тестового файла


from .models import User, Post, Group, Follow, Comment


class Profile(TestCase):
    def setUp(self):
        self.client_auth = Client()
        self.user = User.objects.create_user(username="test_user", 
                    email="test_user@krymskiy.com", 
                    password="1234!Q")
        self.group = Group.objects.create(
                    title="test_group", 
                    slug="testgroup", 
                    description="test description"
                    )
        self.client_auth.force_login(self.user)
        self.client_non = Client()

    def check_post(self, post1, post2):
        """ Проверяет соответствие текста, автора и группы постов. """
        self.assertEqual(post1.text, post2.text)
        self.assertEqual(post1.author, post2.author)
        self.assertEqual(post1.group, post2.group)

    def check_urls(self, post1):
        """ Проверяет посты на разных страницах. """
        urls = (
		    reverse("index"),
		    reverse("profile", kwargs={"username": post1.author.username}),
		    reverse("post", kwargs={"username": post1.author.username, "post_id": post1.id,})
	    )
        for url in urls:
            response = self.client_non.get(url)
            if url == reverse("post", kwargs={"username": post1.author.username, "post_id": post1.id,}):
                post_new = response.context['post']
            else:
                paginator = response.context.get('paginator')
                post_new = response.context['page'][0]
                self.assertEqual(paginator.count, 1)
            self.check_post(post1, post_new)

    def test_profile(self):
        """ Тестирует доступность страницы автора. """
        response = self.client_non.get(reverse('profile', 
                    kwargs={"username": self.user.username,}))
        self.assertEqual(response.status_code, 200) 

    def test_new_post_auth(self):
        """ Тестирует возможность создания поста авторизованным пользователем. """
        posts_before = Post.objects.count()  # количество постов до нового поста
        response_access = self.client_auth.get(reverse('new_post'))
        # cоздать новый пост
        response = self.client_auth.post(reverse('new_post'), {
                    'group': self.group.id,
                    'text': "Test text",
                    'author': self.user.id
                    }
                    )
        # количество постов после создания нового поста
        posts_after = Post.objects.count()
        post_new = Post.objects.get(id=1)
        # проверка доступа к странице создания поста
        self.assertEqual(response_access.status_code, 200)
        self.assertEqual(response.status_code, 302)
        # проверка появления нового поста в базе
        self.assertNotEqual(posts_before, posts_after)
        self.check_urls(post_new)

    def test_new_post_anonimus(self):
        """ Тестирует невозможность создания нового поста анонимным пользователем. """
        posts_before = Post.objects.count()
        response = self.client_non.get(reverse('new_post'))
        posts_after = Post.objects.count()
        # проверка редиректа на страницу регистрации при попытке создать 
        # новый пост неавторизованным пользователем
        self.assertRedirects(response, reverse('login')+'?next='+reverse('new_post'))
        self.assertEqual(posts_before, posts_after)

    def test_after_pub(self):
        """ Тестирует публикацию поста на связанных страницах. """
        self.post = Post.objects.create(text="You're talking about things"
                    " I haven't done yet in the past tense. It's driving "
                    "me crazy!", author=self.user)
        self.check_urls(self.post)

    def test_edit_auth(self):
        """ Тестирует возможность авторизованным пользователем 
        отредактировать свой пост.

        """
        self.post = Post.objects.create(text="Test text 1", author=self.user) 
        response = self.client_auth.get(reverse('post_edit', 
                    kwargs={"username": self.user.username, "post_id": self.post.id,}))
        self.assertEqual(response.status_code, 200)
        self.post.text = "Test text 2"
        self.post.save()
        # проверяет отредактированный пост на связанных страницах
        self.check_urls(self.post)

class Server_error(TestCase):
    def setUp(self):
        self.client = Client()

    def test_page_not_found(self):
        response = self.client.get(reverse('profile', kwargs={"username": 'nobody',}))
        self.assertEqual(response.status_code, 404)

class Img_chek(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test_user", 
                    email="test_user@krymskiy.com", 
                    password="1234!Q")
        self.group = Group.objects.create(
                    title="test_group", 
                    slug="testgroup", 
                    description="test description"
                    )
        self.client.force_login(self.user)
    
    def check_urls2(self, post1):
        urls = (
		    reverse('index'),
		    reverse('profile', kwargs={"username": post1.author.username}),
            reverse('group', kwargs={"slug": post1.group.slug}),
            reverse('post', 
                    kwargs={"username": post1.author.username, 
                    "post_id": post1.id,}),
	    )
        for url in urls:
            response = self.client.get(url)
            print (url, response)
            self.assertContains(response, '<img')

    def test_img_exist(self):
        """ Тестирует наличие загруженной картинки. """
        # бинарный код картинки
        byte_im = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x002'
            b'\x00\x00\x002\x08\x06\x00\x00\x00\x1e?\x88\xb1\x00'
            b'\x00\x00WIDATx\x9c\xed\xcf\x01\r\xc00\x0c\xc0\xb0~'
            b'\xfc9\xf7$.-\xbal\x04\xc9\xb33;?pn\x07|\xc5H\x8d\x91'
            b'\x1a#5Fj\x8c\xd4\x18\xa91Rc\xa4\xc6H\x8d\x91\x1a#5Fj'
            b'\x8c\xd4\x18\xa91Rc\xa4\xc6H\x8d\x91\x1a#5Fj\x8c\xd4'
            b'\x18\xa91Rc\xa4\xe6\x05\x07\xb1\x02b\x9eT\xf9\xdf\x00'
            b'\x00\x00\x00IEND\xaeB`\x82'
            )
        # создание файла картинки
        img = SimpleUploadedFile(
            name='test_image.png',
            content=byte_im,
            content_type='image/gif',
        )
        self.post = self.client.post(reverse('new_post'), 
                    {'author': self.user.id, 
                    'text': 'post with image', 
                    'group': self.group.id, 
                    'image': img}, follow=True)
        self.post_new = Post.objects.get(id=1)
        self.check_urls2(self.post_new)

    def test_non_img(self):
        img = SimpleUploadedFile(
            name='txt file.txt',
            content=b'abc',
            content_type='text/plain',
        )
        response = self.client.post(reverse('new_post'), 
                    {'author': self.user.id, 
                    'text': 'post with image', 
                    'group': self.group.id, 
                    'image': img}, follow=True)
        self.assertFormError(response, 'form', 'image', 
                    errors="Загрузите правильное изображение. "
                    "Файл, который вы загрузили, поврежден или "
                    "не является изображением.")

    def tearDown(self):
        os.remove('media/posts/test_image.png')


class CacheTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test_user", 
                    email="test_user@krymskiy.com", 
                    password="1234!Q")
        self.post = Post.objects.create(text="Just to be for cache", author=self.user)

    def test_cache(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, self.post.text)
        post2 = Post.objects.create(text="Just to be for cache - 2", author=self.user)
        response2 = self.client.get(reverse('index'))
        self.assertNotContains(response2, post2.text)
        time.sleep(22)
        response3 = self.client.get(reverse('index'))
        self.assertContains(response, self.post.text)
        self.assertNotContains(response2, post2.text)


class FollowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test_user", 
                    email="test_user@krymskiy.com", 
                    password="1234!Q")
        self.user2 = User.objects.create_user(username="follow_user",
                    password="4321!Q")
        self.user2post = Post.objects.create(text="Interesting text", 
                    author=self.user2)
        self.client.force_login(self.user)

    def test_follow_unfollow_auth(self):
        response = self.client.post(reverse('profile_follow', kwargs={
            'username': self.user2,
            }))
        follow_item = Follow.objects.get(user=self.user)
        check_BD = Follow.objects.filter(user=self.user).exists()
        self.assertTrue(check_BD)
        self.assertEqual(follow_item.author.username, self.user2.username)
        response = self.client.post(reverse('profile_unfollow', kwargs={
            'username': self.user2,
            }))
        check_BD = Follow.objects.filter(user=self.user).exists()
        self.assertFalse(check_BD)
    
    def test_new_follow_entry(self):
        self.client.post(reverse('profile_follow', kwargs={
            'username': self.user2,
            }))
        response = self.client.post(reverse('follow_index'))
        paginator = response.context.get('paginator')
        self.assertEqual(paginator.count, 1) # check that a post exists
        post_new = response.context['page'][0]
        self.assertEqual(self.user2post.text, post_new.text)
        self.assertEqual(self.user2post.author, post_new.author)
        user3 = User.objects.create_user(username="not_follow_user",
                    password="4321!Q")
        self.client.logout()
        self.client.force_login(user3)
        response = self.client.post(reverse('follow_index'))
        paginator = response.context.get('paginator')
        self.assertEqual(paginator.count, 0)


class CommentTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="test_user", 
                    email="test_user@krymskiy.com", 
                    password="1234!Q")
        self.user2 = User.objects.create_user(username="post_user",
                    password="4321!Q")
        self.user2post = Post.objects.create(text="Interesting text", 
                    author=self.user2)
        self.client.force_login(self.user)

    def test_auth_comment(self):
        comments_before = Comment.objects.filter(post=self.user2post).count()
        response = self.client.post(reverse('add_comment', kwargs={
                        'username': self.user2.username, 
                        'post_id': self.user2post.id,}), 
                        {'post': self.user2post.id, 
                        'author': self.user.id, 
                        'text': "Test comment"
                        })
        comments_after = Comment.objects.filter(post=self.user2post).count()
        comment_new = Comment.objects.get(id=1)
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(comments_before, comments_after)
        response = self.client.get(reverse('post', kwargs={'username': self.user2.username, 'post_id': self.user2post.id,}))
        self.assertContains(response, self.user2post.text)

    def test_anonimus_comment(self):
        comments_before = Comment.objects.filter(post=self.user2post).count()
        self.client.logout()
        response = self.client.post(reverse('add_comment', kwargs={
                    'username': self.user2.username, 
                    'post_id': self.user2post.id,}), 
                    {'post': self.user2post.id, 
                    'author': self.user.id, 
                    'text': "Test comment"
                    })
        comments_after = Comment.objects.filter(post=self.user2post).count()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(comments_before, comments_after)
