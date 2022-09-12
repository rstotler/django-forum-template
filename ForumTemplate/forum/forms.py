from django import forms

class ThreadCreateForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput({'maxlength': 256, 'placeholder': 'Thread Title'}))
    content = forms.CharField(widget=forms.Textarea({'maxlength': 10000, 'rows': 20}))
   
class ThreadEditForm(forms.Form):
    subforumList = forms.ChoiceField(label="Subforum")
    title = forms.CharField(widget=forms.TextInput({'maxlength': 256, 'placeholder': 'Thread Title'}))
    isLocked = forms.ChoiceField(choices=[['1', 'Unlocked'], ['2', 'Locked']], widget=forms.RadioSelect(attrs={'class': 'form-check-inline'}))
   
class PostCreateForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea({'maxlength': 10000, 'rows': 20}))

class PostEditForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea({'maxlength': 10000, 'rows': 20}))
   