import csv
from django.http import HttpResponse
from django.shortcuts import render
from .forms import GeneratorForm
from .models import RussianWord
from .services import generate_vipnet_phrase_and_password, generate_classic_password


def index(request):
    results = []
    dict_size = RussianWord.objects.count()

    if request.method == 'POST':
        form = GeneratorForm(request.POST)
        if form.is_valid():
            mode = form.cleaned_data['mode']
            batch_count = form.cleaned_data['batch_count']

            for _ in range(batch_count):
                if mode == 'phrase':
                    item = generate_vipnet_phrase_and_password(
                        word_count=form.cleaned_data['word_count'],
                        use_digits=form.cleaned_data['phrase_digits'],
                        special_char=form.cleaned_data['phrase_special'],
                        capitalize=form.cleaned_data['phrase_capitalize'],
                        prefix_len=form.cleaned_data['prefix_len'],
                    )
                else:
                    item = generate_classic_password(
                        length=form.cleaned_data['length'],
                        use_upper=form.cleaned_data['use_upper'],
                        use_digits=form.cleaned_data['use_digits'],
                        use_special=form.cleaned_data['use_special'],
                    )
                results.append(item)
    else:
        form = GeneratorForm()
        for _ in range(10):
            results.append(generate_vipnet_phrase_and_password())

    # Сохраняем сгенерированный список в сессию для экспорта
    request.session['last_passwords'] = results

    return render(request, 'passgen/index.html', {
        'form': form,
        'results': results,
        'dict_size': dict_size,
    })


def export_passwords(request, file_format: str):
    """Отдает последние сгенерированные пароли в виде CSV или TXT файла."""
    results = request.session.get('last_passwords', [])

    if file_format == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="passwords.csv"'
        # utf-8-sig добавляет BOM, чтобы Excel корректно открывал кириллицу
        response.write('\ufeff')

        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Парольная фраза', 'Пароль (EN-раскладка)'])
        for item in results:
            writer.writerow([item['phrase'], item['password']])
        return response

    # Формат TXT по умолчанию
    response = HttpResponse(content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="passwords.txt"'

    lines = []
    for idx, item in enumerate(results, start=1):
        lines.append(f"{idx}. {item['phrase']}  |  {item['password']}")

    response.write("\n".join(lines))
    return response
