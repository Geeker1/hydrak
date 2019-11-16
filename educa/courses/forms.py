from django import forms
from django.forms.models import inlineformset_factory
from .models import Course, Module



ModuleFormSet = inlineformset_factory(
	Course,
	Module, 
	fields=['title','description'],#the fields to be included in each form in the formset
	extra=2,#the no of empty forms that can be included in thr formset
	can_delete=True# a boolean field to be included for each form to delete it.
	)