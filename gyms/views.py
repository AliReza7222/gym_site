from django.shortcuts import render
from django.views.generic import TemplateView


class Home(TemplateView):
    template_name = 'gyms/home.html'


class About(TemplateView):
    template_name = 'gyms/about.html'

