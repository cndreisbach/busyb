from django import forms
from core.models import Task


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

    class Meta:
        model = Task
        fields = ['description', 'due_on', 'show_on']
        widgets = {'due_on': BetterDateInput(), 'show_on': BetterDateInput()}
