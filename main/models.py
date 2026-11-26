from django.db import models

# Create your models here.

class Category(models.Model):
    cat_title = models.CharField("Категория ссылки", max_length=150, unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["id"]

    def __str__(self):
        return self.cat_title

class Links(models.Model):

    category = models.ForeignKey(Category, on_delete=models.PROTECT,
                                   verbose_name="Категория", related_name="links")
    title = models.CharField("Название ссылки", max_length=150, unique=True)
    url = models.CharField("URL ссылки", max_length=255 )
    scale_link = models.SmallIntegerField ("Вес ссылки", default=0)
    description = models.TextField()
    created_at = models.DateTimeField("Дата добавления", auto_now_add=True)

    class Meta:
        verbose_name = "Ссылка"
        verbose_name_plural = "Ссылки"
        ordering = ["category", "scale_link", "title"]

    def __str__(self):
        return f"{self.title} {self.url}"

class Districts(models.Model):

    code = models.CharField ("Код района", max_length=3)
    dname = models.CharField ("Название района", max_length=100)
    subnet = models.CharField ("Подсеть", max_length=13)
    telef = models.CharField ("вн туелефон", max_length=12)
    address = models.CharField ("Адрес КС", max_length=150)

    class Meta:
        verbose_name = "Район"
        verbose_name_plural = "Районы"
        ordering = ["id"]

    def __str__(self):
        return f"{self.code} {self.dname}"