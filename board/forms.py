from django import forms
from .models import Thread, Reply

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title']


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content', 'image', 'video']

class ThreadForm(forms.ModelForm):
    icon = forms.FileField(required=False)

    class Meta:
        model = Thread
        fields = ['title', 'content', 'tags']  # ★ icon を外す
        labels = {
            'title': 'タイトル',
            'content': '内容',
            'tags': 'タグ',
        }
        widgets = {
            'tags': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = False