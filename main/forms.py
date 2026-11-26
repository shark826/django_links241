from django import forms
from .models import Districts, Links


class BootstrapMixin:
    """Добавляет класс form-control ко всем полям."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput,)):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")


class LinkForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Links
        fields = [
            "category", "title", "url",
            "scale_link", "description",
        ]