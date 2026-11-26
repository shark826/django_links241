from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.LinksListView.as_view(), name="home"),

    # Ссылки
    path("links/", views.LinksListView.as_view(), name="links_list"),
    path("links/<int:pk>/", views.LinksDetailView.as_view(), name="links_detail"),
    path("links/add/", views.LinksCreateView.as_view(), name="links_add"),
    path("links/<int:pk>/edit/", views.LinksUpdateView.as_view(), name="links_edit"),
    path("links/<int:pk>/delete/", views.LinksDeleteView.as_view(), name="links_delete"),

    # Районы
    path("districts/", views.DistrictsListView.as_view(), name="districts_list"),
]