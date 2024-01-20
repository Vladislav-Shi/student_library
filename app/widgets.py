from django import forms


class TextAreaWidget(forms.widgets.TextInput):
    template_name = 'my_custom_widget.html'
