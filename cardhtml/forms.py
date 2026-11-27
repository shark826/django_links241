from django import forms

class CsvUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Выберите CSV файл',
        widget=forms.FileInput(attrs={'accept': '.csv', 'class': 'form-control'})
    )
    valid_from = forms.CharField(
        label='Действует с',
        initial='01.01.2027',
        max_length=20
    )
    valid_to = forms.CharField(
        label='Действует по',
        initial='31.12.2027',
        max_length=20
    )
