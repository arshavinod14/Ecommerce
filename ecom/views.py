from django.http import HttpResponseNotFound
from django.shortcuts import render


def handler404(request, exception):
    return HttpResponseNotFound(render(request, '404.html'))