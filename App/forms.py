from django import forms
from django.forms import fields
from django.forms import widgets
from .models import Comment, Paper, Profile
from django.contrib.auth.models import User


class SearchForm(forms.Form):
    query = forms.CharField()
    choice = forms.ChoiceField(
        choices=(('title', 'Title'), ('key words', 'Key Words'),
                 ('author', 'Author'), ('category', 'Category'),
                 ('time', 'Time')),
        initial=1,
        widget=widgets.RadioSelect,
    )


class PaperForm(forms.ModelForm):
    class Meta:
        # 表单对应的模型
        model = Paper
        # 指定表单需要显示的字段
        fields = ('title', 'abstract', 'category')


class CommentForm(forms.ModelForm):
    class Meta:
        # 表单对应的模型
        model = Comment
        # 指定表单需要显示的字段
        fields = ('body', )


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password',
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('student_id',)