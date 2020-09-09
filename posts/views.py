from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
#  функция reverse_lazy позволяет получить URL по параметру "name" функции path()
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required


from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


"""Функция вывода главной страницы"""
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(request, "index.html", {'page': page, 'paginator': paginator})


"""view-функция для страницы сообщества"""
def group_posts(request, slug):
    """функция get_object_or_404 получает по заданным критериям объект из 
    базы данных или возвращает сообщение об ошибке, если объект не найден.
    Далее получаем посты с общим свойством group через related_name.

    """
    group = get_object_or_404(Group, slug=slug)
    post_list = group.post.all()  # упорядочено по дате в модели
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением    
    return render(request, "group.html", {'group': group, 'page': page, 'paginator': paginator})


""" view-функция для обработки нового поста"""
@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    
    if form.is_valid():
        new_entry = form.save(commit=False)
        new_entry.author = request.user
        new_entry.save()
        return redirect('index')

    return render(request, "new_post.html", {'form': form})


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    #profile_user = User.get.objects(username=username)
    # получаем посты из модели User по related_name 'posts'
    profile_posts = profile_user.posts.all()
    paginator = Paginator(profile_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user, author=profile_user).exists()
    else:
        following = False
    print (request.user)
    return render(request, "profile.html",
                 {"profile_user": profile_user, 
                  'profile_posts': profile_posts, 'page': page,
                   'paginator': paginator, 'following': following}
                 )
 
 
def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    author = get_object_or_404(User, username=username)
    # get number of posts from User model via related name 'posts' 
    quantity_posts = author.posts.all().count
    form = CommentForm(request.POST or None)
    items = post.comment.all()
    return render(request, "post.html", {'author': author, 'post': post, 
                'id': post.id, 'quantity_posts': quantity_posts, 
                'items': items, 'form': form})


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    article = get_object_or_404(Post, pk=post_id, 
                author__username=username) # запрашиваем объект
    """ Проверить, что текущий пользователь — это автор записи. """
    if request.user != author:
        return post_view(request, author, article.id)

    form = PostForm(request.POST or None, files=request.FILES or None, instance=article)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('post', username=author, post_id=article.id)

    return render(
        request, "new_post.html", {'form': form, 'if_edit': True, 
                        'article': article},
    )


def page_not_found(request, exception):
    """ Переменная exception содержит отладочную информацию, 
    выводить её в шаблон пользователской страницы 404 мы не станем.
    
    """
    return render(
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, 
                author__username=username)
    comments = post.comment.all()
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()
            return redirect('post', username=author, post_id=post.id)

    return render(request, "comments.html", {'form': form})


@login_required
def follow_index(request):
    """ Конструкция делает запрос через related_name тех постов, авторы 
    которых попадают в список following пользователя.

    """
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(request, "follow.html", {'page': page, 'paginator': paginator})

@login_required
def profile_follow(request, username):
    if request.user.username != username:
        new_follow = Follow.objects.get_or_create(user=request.user, author=User.objects.get(username=username))
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    un_follow = Follow.objects.get(user=request.user, author=author)
    un_follow.delete()
    return redirect('profile', username=username)
