from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import CreateView
#  функция reverse_lazy позволяет получить URL по параметру "name" функции path()
from django.urls import reverse_lazy

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("index") #  где login — это параметр "name" в path() - заменил на index
    template_name = "signup.html"
