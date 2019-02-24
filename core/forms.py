from django import forms
from core.models import Task
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Div


class BetterDateInput(forms.DateInput):
    input_type = 'date'


class NewTaskForm(forms.Form):
    task = forms.CharField(
        label='Task',
        max_length=512,
        widget=forms.TextInput(attrs={'placeholder': 'add a new task'}))

    def save(self, **kwargs):
        if self.is_valid():
            task_props = {"description": self.cleaned_data['task']}
            task_props.update(kwargs)
            return Task.objects.create(**task_props)
        return None


class EditTaskForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'pv2 measure'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save task'))
        self.helper.layout = Layout(
            Div(Field('description', css_class="w-100 mv2 pa2"),
                css_class="mv2"),
            Div(Field('due_on', css_class="w-100 mv2 pa2"), css_class="mv2"),
            Div(Field('show_on', css_class="w-100 mv2 pa2"), css_class="mv2"),
        )

    class Meta:
        model = Task
        fields = ['description', 'due_on', 'show_on']
        widgets = {'due_on': BetterDateInput(), 'show_on': BetterDateInput()}
