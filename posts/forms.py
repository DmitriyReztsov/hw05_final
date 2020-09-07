from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Создаем класс формы на базе модели Post
       для добавления в Post новых записей"""
    class Meta:
        model = Post
        fields = ['group', 'text', 'image']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
