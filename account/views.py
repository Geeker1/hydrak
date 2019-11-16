from django.shortcuts import render,redirect,reverse
from django.views.generic import CreateView,FormView,ListView
from .forms import SignUpForm
from django.contrib.auth.models import User
from django.contrib.auth import login

from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse_lazy
from django import forms





def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            phone = form.cleaned_data['phone']
            user = form.save()
            login(request, user)
            return redirect('manage_course_list')
        else:
            form = SignUpForm()
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form':form})

      
class ProfileUpdate(UpdateView):
	fields = ['email','username']
	model = User
	success_url = reverse_lazy('home')
	template_name = 'courses/update.html'

	def form_valid(self, form):
		form.instance.owner = self.request.user
		form.save()
		return super(ProfileUpdate, self).form_valid(form)