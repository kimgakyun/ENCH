from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .models import Profile

class SignUpForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '사용자 이름'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': '이메일'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': '비밀번호'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': '비밀번호 확인'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        # 도움말 텍스트 제거
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ProfileFormPage1(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'gender', 'age', 'phone_number']
        labels = {
            'name': '이름',
            'gender': '성별',
            'age': '나이',
            'phone_number': '연락처',
        }
        widgets = {
            'name': forms.TextInput(attrs={'required': True, 'style': 'width: 100%; box-sizing: border-box;'}),
            'gender': forms.Select(attrs={'required': True, 'style': 'width: 100%; box-sizing: border-box;'}),
            'age': forms.NumberInput(attrs={'required': True, 'style': 'width: 100%; box-sizing: border-box;'}),
            'phone_number': forms.TextInput(attrs={'required': True, 'style': 'width: 100%; box-sizing: border-box;'}),
        }

class ProfileFormPage2(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['height', 'weight', 'medical_history']
        labels = {
            'height': '키',
            'weight': '체중',
            'medical_history': '병력(혈압 알레르기 기타병 등)',
        }
        widgets = {
            'height': forms.NumberInput(attrs={'required': True, 'style': 'width: 100%; box-sizing: border-box;'}),
            'weight': forms.NumberInput(attrs={'required': True, 'style': 'width: 100%; box-sizing: border-box;'}),
            'medical_history': forms.Textarea(attrs={'required': True, 'style': 'width: 100%; box-sizing: border-box;'}),
        }

class ProfileFormPage3(forms.ModelForm):
    ACTIVITY_LEVEL_CHOICES = [
        ('운동 x', '운동 x'),
        ('주 1~2회', '주 1~2회'),
        ('주 3~4회', '주 3~4회'),
        ('주 5~6회', '주 5~6회'),
        ('매일', '매일'),
    ]
    SLEEP_HOURS_CHOICES = [
        ('3~4시간', '3~4시간'),
        ('5~6시간', '5~6시간'),
        ('7~8시간', '7~8시간'),
        ('9~10시간', '9~10시간'),
        ('10시간 이상', '10시간 이상'),
    ]

    activity_level = forms.ChoiceField(choices=ACTIVITY_LEVEL_CHOICES, widget=forms.RadioSelect, label='운동 습관')
    sleep_hours = forms.ChoiceField(choices=SLEEP_HOURS_CHOICES, widget=forms.RadioSelect, label='수면량')

    class Meta:
        model = Profile
        fields = ['dietary_habits', 'activity_level', 'sleep_hours', 'prefer_activity']
        labels = {
            'dietary_habits': '식습관',
            'prefer_activity': '선호 운동',
        }
        widgets = {
            'dietary_habits': forms.Textarea(attrs={'required': True, 'style': 'width: 100%; box-sizing: border-box;'}),
            'prefer_activity': forms.TextInput(attrs={'required': True, 'style': 'width: 100%; box-sizing: border-box;'}),
        }

class ProfileFormPage4(forms.ModelForm):
    GOAL_STRENGTH_CHOICES = [
        ('골격근량 증가', '골격근량 증가'),
        ('골격근량 유지', '골격근량 유지'),
        ('골격근량 저하', '골격근량 저하'),
    ]

    goal_strength = forms.ChoiceField(choices=GOAL_STRENGTH_CHOICES, widget=forms.RadioSelect, label='목표 근력')

    class Meta:
        model = Profile
        fields = ['goal_weight', 'goal_strength', 'goal_deadline']
        labels = {
            'goal_weight': '목표 체중 (Kg)',
            'goal_deadline': '목표 날짜',
        }
        widgets = {
            'goal_weight': forms.NumberInput(attrs={'required': True, 'style': 'width: 100%; box-sizing: border-box;'}),
            'goal_deadline': forms.DateInput(attrs={'type': 'date', 'required': True, 'style': 'width: 100%; box-sizing: border-box;'}),
        }

    def clean_goal_deadline(self):
        goal_deadline = self.cleaned_data.get('goal_deadline')
        today = timezone.now().date()
        min_date = today + timedelta(days=30)

        if goal_deadline < today:
            raise ValidationError('목표 날짜는 현재 날짜 이후여야 합니다. 다시 입력해주세요.')
        if goal_deadline < min_date:
            raise ValidationError('목표 날짜는 최소 현재 날짜로부터 30일 이후여야 합니다. 다시 입력해주세요.')

        return goal_deadline