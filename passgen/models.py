from django.db import models

class RussianWord(models.Model):
    class PartOfSpeech(models.TextChoices):
        NOUN = 'NOUN', 'Существительное'
        ADJF = 'ADJF', 'Прилагательное'
        VERB = 'VERB', 'Глагол'
        ADVB = 'ADVB', 'Наречие'

    word = models.CharField('Слово (начальная форма)', max_length=100, unique=True, db_index=True)
    pos = models.CharField('Часть речи', max_length=10, choices=PartOfSpeech.choices, db_index=True)
    is_animate = models.BooleanField('Одушевленное', default=False, db_index=True)

    class Meta:
        verbose_name = 'Слово словаря'
        verbose_name_plural = 'Словарь русских слов'

    def __str__(self):
        return f"{self.word} ({self.get_pos_display()})"
