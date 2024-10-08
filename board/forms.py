from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # 실제 저장받는 필드
        fields = ['post_title', 'post_content']
        widgets = {
            'post_title': forms.TextInput(attrs={'placeholder': '포스트 제목...'}),
            'post_content': forms.Textarea(attrs={'placeholder': '내용 입력...'}),
            # 사용자에게 보이는 필드
        }
        labels = {
            'post_title': '',  
            'post_content': '',
        }


class PostSearchForm(forms.Form):
    search_word = forms.CharField(
        label= '',
        widget=forms.TextInput(attrs={
            'placeholder': '포스트 검색',
            'id': 'search-query'
            })
    )

        
        