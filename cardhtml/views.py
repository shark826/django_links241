import csv
import io
import zipfile
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from .forms import CsvUploadForm


def generate_cards_view(request):
    if request.method == 'POST':
        form = CsvUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            valid_from = form.cleaned_data['valid_from']
            valid_to = form.cleaned_data['valid_to']

            # Читаем файл и определяем кодировку (UTF-8 или Windows-1251)
            raw_data = csv_file.read()
            try:
                decoded_file = raw_data.decode('utf-8-sig')
            except UnicodeDecodeError:
                decoded_file = raw_data.decode('cp1251')

            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string, delimiter=';')

            # Создаем ZIP-архив в памяти
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for row in reader:
                    # Пропускаем пустые строки
                    if not row.get('login'):
                        continue

                    p1 = row.get('passphrase1', '').strip()
                    p2 = row.get('passphrase2', '').strip()
                    p3 = row.get('passphrase3', '').strip()
                    password = row.get('pass2', '').strip()

                    # Формируем данные для подсветки первых 4 букв каждого слова
                    context = {
                        'valid_from': valid_from,
                        'valid_to': valid_to,
                        'name': row.get('name', '').strip(),
                        'login': row.get('login', '').strip(),
                        'password': password,
                        'numpass': row.get('numpass', '').strip(),
                        'p1_head': p1[:4],
                        'p1_tail': p1[4:],
                        'p2_head': p2[:4],
                        'p2_tail': p2[4:],
                        'p3_head': p3[:4],
                        'p3_tail': p3[4:],
                        'has_exclamation': password.endswith('!'),
                    }

                    html_content = render_to_string('cardhtml/card.html', context)

                    # Имя файла берем из колонки filename (или из логина, если колонка пуста)
                    kab = row.get('kab', '').strip()
                    filename = row.get('filename', '').strip()

                    # Если колонка filename пустая, берем часть логина до @
                    if not filename:
                        filename = context['login'].split('@')

                    # Формируем итоговое имя: если кабинет указан -> "101kab_013AkhmetovaGR", иначе просто "013AkhmetovaGR"
                    if kab:
                        base_filename = f"{kab}kab_{filename}"
                    else:
                        base_filename = filename

                    # Очищаем от недопустимых символов
                    safe_filename = "".join(c for c in base_filename if c.isalnum() or c in ('-', '_'))

                    zip_file.writestr(f"{safe_filename}.html", html_content.encode('utf-8'))


            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="password_cards.zip"'
            return response
    else:
        form = CsvUploadForm()

    return render(request, 'cardhtml/upload.html', {'form': form})

