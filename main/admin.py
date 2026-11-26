from django.contrib import admin

# Register your models here.
from .models import Category, Links, Districts

admin.site.register(Category)
#admin.site.register(Links)
admin.site.register(Districts)

@admin.register(Links)
class LinksAdmin(admin.ModelAdmin):
    list_display = ('category', 'title', 'url')
    ordering = ["category", "scale_link", "title"]