import re
from django.core.management.base import BaseCommand
import pymorphy3
from passgen.models import RussianWord


class Command(BaseCommand):
    help = 'Загружает строго проверенный словарь русских слов (без предсказанных форм и обрывков)'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, required=True, help='Путь к freqrnc2011.csv или .txt')
        parser.add_argument('--limit', type=int, default=7000, help='Лимит слов (по умолчанию 7000)')

    def handle(self, *args, **options):
        morph = pymorphy3.MorphAnalyzer()
        file_path = options['file']
        limit = options['limit']

        RussianWord.objects.all().delete()
        self.stdout.write('Старый словарь очищен.')

        allowed_pos = {'NOUN', 'ADJF', 'VERB', 'ADVB'}
        forbidden_tags = {
            'Name', 'Surn', 'Patr', 'Geox', 'Orgn', 'Trad', 'Abbr',
            'Slng', 'Arch', 'Infr', 'Litr', 'Erro', 'Dist', 'Ques', 'Dmns', 'Prnt'
        }
        stop_words = {
            'убийство', 'смерть', 'война', 'труп', 'кровь', 'пьянство', 'наркотик',
            'тюрьма', 'болезнь', 'рак', 'гроб', 'могила', 'катастрофа', 'взрыв',
            'преступление', 'насилие', 'убить', 'умереть', 'погибнуть', 'болеть',
            'жертва', 'преступник', 'убийца', 'вор', 'бандит', 'враг', 'инвалид'
        }

        raw_words = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('Lemma'):
                    continue
                # Берем строго первое поле (лемму) до табуляции или точки с запятой
                first_col = line.split('\t')[0].split(';')[0].strip().lower()
                if re.fullmatch(r'[а-яё]{4,}', first_col):
                    raw_words.append(first_col)

        existing_words = set()
        to_create = []

        for raw_word in raw_words:
            if len(to_create) >= limit:
                break

            parsed_list = morph.parse(raw_word)
            if not parsed_list:
                continue

            parsed = parsed_list[0]

            # 1. ГЛАВНЫЙ ФИЛЬТР: слово должно быть в официальном словаре OpenCorpora/pymorphy3,
            # а не угадано анализатором по окончанию!
            if not parsed.is_known:
                continue

            pos = parsed.tag.POS
            if pos not in allowed_pos:
                continue

            if any(tag in parsed.tag for tag in forbidden_tags):
                continue

            normal_form = parsed.normal_form.replace('ё', 'е')
            if len(normal_form) < 4 or normal_form in existing_words or normal_form in stop_words:
                continue

            # 2. СТРОГАЯ ПРОВЕРКА ГЛАГОЛОВ
            if pos == 'VERB':
                if 'tran' not in parsed.tag:
                    continue
                if normal_form.endswith(('ся', 'сь')):
                    continue
                if not normal_form.endswith(('ть', 'ти', 'чь')):
                    continue
                # Проверяем, что глагол реально спрягается в 3-е лицо ед. и мн. числа
                v_sing = parsed.inflect({'3per', 'sing'})
                v_plur = parsed.inflect({'3per', 'plur'})
                if not v_sing or not v_plur or len(v_sing.word) < 4 or len(v_plur.word) < 4:
                    continue

            # 3. ПРОВЕРКА СУЩЕСТВИТЕЛЬНЫХ
            is_animate = False
            if pos == 'NOUN':
                if 'Sgtm' in parsed.tag or 'Pltm' in parsed.tag:
                    continue
                # Проверяем, что слово склоняется во множественное число
                n_plur = parsed.inflect({'nomn', 'plur'})
                if not n_plur or len(n_plur.word) < 4:
                    continue
                is_animate = ('anim' in parsed.tag)

            # 4. ПРОВЕРКА ПРИЛАГАТЕЛЬНЫХ
            if pos == 'ADJF':
                if not normal_form.endswith(('ый', 'ий', 'ой')):
                    continue

            existing_words.add(normal_form)
            to_create.append(RussianWord(
                word=normal_form,
                pos=pos,
                is_animate=is_animate
            ))

        RussianWord.objects.bulk_create(to_create, batch_size=2000)

        stats = {
            'Одуш. сущ.': RussianWord.objects.filter(pos='NOUN', is_animate=True).count(),
            'Неодуш. сущ.': RussianWord.objects.filter(pos='NOUN', is_animate=False).count(),
            'Глаголы': RussianWord.objects.filter(pos='VERB').count(),
            'Прил.': RussianWord.objects.filter(pos='ADJF').count(),
            'Наречия': RussianWord.objects.filter(pos='ADVB').count(),
        }
        self.stdout.write(self.style.SUCCESS(
            f'Загружено чистых слов: {len(to_create)}. Статистика: {stats}'
        ))
