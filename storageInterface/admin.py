from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.shortcuts import render

from storageInterface.models import StorageUser


class UserCreationForm(forms.ModelForm):
    # A form for creating new users.

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = StorageUser
        fields = ('email', 'username', 'quota')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        key = user.set_password(self.cleaned_data["password1"])
        # print(key)
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    #A form for updating users.
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = StorageUser

        fields = ('email', 'quota', 'username', 'password', 'is_admin')


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'quota', 'username', 'is_admin')
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username','quota')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )

    add_fieldsets = (
            (None, {
            'classes': ('wide',),
            'fields': ('email', 'quota', 'username', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


    def save_model(self, request, obj, form, change):
        result = super(UserAdmin, self).save_model(request, obj, form, change)
        temp = obj.getkey()
        if temp:
            messages.add_message(request, messages.WARNING, 'API KEY: '+temp)

# def pass_reset_done(request):
#     temp = request.user.getkey()
#     if temp:
#         messages.add_message(request, messages.WARNING, 'API KEY: ' + temp)
#     return render(request, 'registration/password_change_done.html')

# register the useradmin
admin.site.register(StorageUser, UserAdmin)
# unregister Group model from admin.
admin.site.unregister(Group)