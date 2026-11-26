from django import forms
from django.core.exceptions import ValidationError


class GeneratorForm(forms.Form):
    MODE_CHOICES = [
        ('phrase', 'Парольная фраза (стиль ViPNet)'),
        ('password', 'Классический пароль'),
    ]
    WORD_COUNT_CHOICES = [
        (3, '3 слова (Сущ + Глагол + Сущ)'),
        (4, '4 слова (Прил + Сущ + Глагол + Сущ)'),
        (5, '5 слов (Прил + Сущ + Наречие + Глагол + Сущ)'),
    ]
    PREFIX_LEN_CHOICES = [
        (3, 'Первые 3 буквы каждого слова'),
        (4, 'Первые 4 буквы каждого слова'),
    ]

    mode = forms.ChoiceField(
        label='Режим генерации',
        choices=MODE_CHOICES,
        widget=forms.RadioSelect,
        initial='phrase'
    )
    batch_count = forms.IntegerField(
        label='Количество генерируемых вариантов',
        min_value=1,
        max_value=500,
        initial=15
    )

    # Настройки для парольной фразы
    word_count = forms.TypedChoiceField(
        label='Количество слов во фразе',
        choices=WORD_COUNT_CHOICES,
        coerce=int,
        initial=3
    )
    prefix_len = forms.TypedChoiceField(
        label='Длина склейки из каждого слова',
        choices=PREFIX_LEN_CHOICES,
        coerce=int,
        initial=4
    )
    phrase_digits = forms.BooleanField(
        label='Двузначное число в начале (согласованное с 1-м словом)',
        required=False,
        initial=True
    )
    phrase_special = forms.CharField(
        label='Спецсимвол в конце (1 символ, опционально)',
        max_length=1,
        required=False,
        widget=forms.TextInput(attrs={
            'maxlength': '1',
            'placeholder': '!',
            'style': 'width: 45px; text-align: center; font-weight: bold;'
        })
    )
    phrase_capitalize = forms.BooleanField(
        label='Начинать фразу с заглавной буквы',
        required=False,
        initial=True
    )

    # Настройки для классического пароля
    length = forms.IntegerField(label='Длина пароля', min_value=6, max_value=64, initial=14)
    use_upper = forms.BooleanField(label='Заглавные буквы (A-Z)', required=False, initial=True)
    use_digits = forms.BooleanField(label='Цифры (0-9)', required=False, initial=True)
    use_special = forms.BooleanField(label='Спецсимволы (!@#$%)', required=False, initial=True)

    def clean_phrase_special(self):
        val = self.cleaned_data.get('phrase_special', '')
        if val:
            if val.isalnum() or val.isspace():
                raise ValidationError('Введите один спецсимвол (например: ! @ # $ % & * - _ = +), а не букву или цифру.')
        return val
