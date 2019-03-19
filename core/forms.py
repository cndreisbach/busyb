from django import forms
from core.models import Task, Note


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
        self.label_suffix = None

    class Meta:
        model = Task
        fields = ['description', 'due_on', 'show_on']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'w-100 mv2 pa2 f4'}),
            'due_on': BetterDateInput(attrs={'class': 'w-100 mv2 pa2'}),
            'show_on': BetterDateInput(attrs={'class': 'w-100 mv2 pa2'})
        }


class NoteForm(forms.ModelForm):

    class Meta:
        model = Note
        fields = ['text']
