import secrets
import string
import pymorphy3
from django.db.models import Q
from .models import RussianWord

morph = pymorphy3.MorphAnalyzer()

RU_TO_EN_LAYOUT = str.maketrans(
    "йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,",
    "qwertyuiop[]asdfghjkl;'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?"
)

# Буквы, которые дают спецсимволы в EN-раскладке ([ ] ; ' , .)
FORBIDDEN_FIRST_LETTERS = ('х', 'ъ', 'ж', 'э', 'б', 'ю')


def parse_first(word: str):
    """Возвращает первый (наиболее вероятный) вариант морфологического разбора слова."""
    return next(iter(morph.parse(word)))


def get_random_word(
    pos: str,
    is_animate: bool | None = None,
    exclude_first_letters: tuple[str, ...] = ()
) -> str:
    """Выборка случайного слова из БД с учетом части речи, одушевленности и запрещенных начальных букв."""
    qs = RussianWord.objects.filter(pos=pos)
    if is_animate is not None:
        qs = qs.filter(is_animate=is_animate)

    if exclude_first_letters:
        query = Q()
        for letter in exclude_first_letters:
            query |= Q(word__istartswith=letter)
        qs = qs.exclude(query)

    count = qs.count()
    if count == 0:
        if pos == 'NOUN' and is_animate:
            return 'корова'
        if pos == 'NOUN' and is_animate is False:
            return 'шарик'
        fallbacks = {'ADJF': 'смелый', 'VERB': 'любить', 'ADVB': 'быстро'}
        return fallbacks.get(pos, 'слово')

    return qs[secrets.randbelow(count)].word


def convert_to_en_layout(text: str) -> str:
    """Переводит строку из русской раскладки в английскую."""
    return text.translate(RU_TO_EN_LAYOUT)


def inflect_noun_with_number(noun_raw: str, number: int) -> tuple[str, str]:
    """Согласует существительное с числительным (например, 33 коровы)."""
    parsed = parse_first(noun_raw)
    agreed = parsed.make_agree_with_number(number)
    word_str = agreed.word if agreed else noun_raw

    if number % 10 == 1 and number % 100 != 11:
        verb_num = 'sing'
    else:
        verb_num = 'plur'

    return word_str, verb_num


def generate_vipnet_phrase_and_password(
    word_count: int = 3,
    use_digits: bool = True,
    special_char: str = "",
    capitalize: bool = True,
    prefix_len: int = 4
) -> dict:
    """Генерирует согласованную фразу (3, 4 или 5 слов) и склеенный пароль в EN-раскладке."""
    noun1_exclude = FORBIDDEN_FIRST_LETTERS if word_count == 3 else ()
    adj1_exclude = FORBIDDEN_FIRST_LETTERS if word_count >= 4 else ()

    noun1_raw = get_random_word('NOUN', is_animate=True, exclude_first_letters=noun1_exclude)
    verb_raw = get_random_word('VERB')
    noun2_raw = get_random_word('NOUN', is_animate=False)

    adj1_raw = get_random_word('ADJF', exclude_first_letters=adj1_exclude) if word_count >= 4 else None
    advb_raw = get_random_word('ADVB') if word_count == 5 else None

    n1_parsed = parse_first(noun1_raw)
    n1_gender = n1_parsed.tag.gender or 'masc'

    # 1. Числительное и первое существительное
    lead_number = None
    if use_digits:
        lead_number = secrets.randbelow(90) + 10
        noun1, verb_number = inflect_noun_with_number(noun1_raw, lead_number)
    else:
        noun1 = noun1_raw
        verb_number = n1_parsed.tag.number or 'sing'

    # 2. Первое прилагательное (если 4 или 5 слов)
    adj1 = None
    if adj1_raw:
        adj1_parsed = parse_first(adj1_raw)
        if use_digits:
            if lead_number % 10 == 1 and lead_number % 100 != 11:
                adj_tags = {'nomn', n1_gender, 'sing'}
            else:
                adj_tags = {'nomn', 'plur'}
        else:
            adj_tags = {'nomn', n1_gender, verb_number}

        adj1_inf = adj1_parsed.inflect(adj_tags)
        adj1 = adj1_inf.word if adj1_inf else adj1_raw

    # 3. Глагол (3-е лицо, наст/буд время)
    verb_parsed = parse_first(verb_raw)
    verb_inf = verb_parsed.inflect({'3per', verb_number})
    verb = verb_inf.word if verb_inf else verb_raw

    # 4. Второе существительное (Винительный падеж, неодушевленное)
    n2_parsed = parse_first(noun2_raw)
    n2_target_num = 'plur' if (use_digits and secrets.randbelow(2) == 1) else (n2_parsed.tag.number or 'sing')
    n2_inf = n2_parsed.inflect({'accs', 'inan', n2_target_num})
    if not n2_inf:
        n2_inf = n2_parsed.inflect({'accs', n2_target_num})
    noun2 = n2_inf.word if n2_inf else noun2_raw

    if word_count == 3:
        words = [noun1, verb, noun2]
    elif word_count == 4:
        words = [adj1, noun1, verb, noun2]
    else:
        words = [adj1, noun1, advb_raw, verb, noun2]

    if capitalize and words:
        first_word, *rest_words = words
        words = [first_word.capitalize(), *rest_words]

     # Берём только первый символ на случай, если передали больше
    clean_special = special_char[:1] if special_char else ""
    
    phrase_parts = []
    if lead_number is not None:
        phrase_parts.append(str(lead_number))
    phrase_parts.extend(words)
    full_phrase = " ".join(phrase_parts)
    if special_char:
        full_phrase += special_char

    glued_parts = []
    if lead_number is not None:
        glued_parts.append(str(lead_number))

    for w in words:
        chunk = w[:prefix_len]
        glued_parts.append(convert_to_en_layout(chunk))

    if special_char:
        glued_parts.append(special_char)

    glued_password = "".join(glued_parts)

    return {
        'phrase': full_phrase,
        'password': glued_password
    }


def generate_classic_password(
    length: int = 14,
    use_upper: bool = True,
    use_digits: bool = True,
    use_special: bool = True
) -> dict:
    """Генератор классического пароля."""
    alphabet = string.ascii_lowercase
    if use_upper:
        alphabet += string.ascii_uppercase
    if use_digits:
        alphabet += string.digits
    if use_special:
        alphabet += "!@#$%^&*()-_=+[]{}"

    pwd = ''.join(secrets.choice(alphabet) for _ in range(length))
    return {'phrase': '— (Случайный набор символов)', 'password': pwd}
