from django.shortcuts import render

# Create your views here.
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import Category, Links, Districts


class DistrictsListView(ListView):
    model = Districts
    template_name = "main/districts_list.html"
    context_object_name = "districts"

    def get_queryset(self):
        qs = (
            Districts.objects
            .order_by("id")
        )
        
        return qs


class LinksListView(ListView):
    model = Category
    template_name = "main/links_list.html"
    context_object_name = "categories"  # Переименовали для понятности

    def get_queryset(self):
        # Одним запросом берем категории и сразу же "предзагружаем" 
        # связанные ссылки, отсортированные по весу (scale_link)
        from django.db.models import Prefetch
        from .models import Links

        return Category.objects.prefetch_related(
            Prefetch(
                'links', 
                queryset=Links.objects.order_by('-scale_link', 'title')
            )
        )


class LinksDetailView(ListView):
    pass

class LinksCreateView(ListView):
    pass

class LinksUpdateView(ListView):
    pass

class LinksDeleteView(ListView):
    pass

