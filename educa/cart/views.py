from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from courses.models import Course
from django.contrib import messages
from .cart import Cart
from .forms import CartAddProductForm
from django.core.urlresolvers import reverse



@require_POST
def cart_add(request, product_id):
    data = dict()
    cart = Cart(request)
    product = get_object_or_404(Course, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
        	quantity=cd['quantity'],
        	update_quantity=cd['update'])

    return redirect('home')


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Course, id=product_id)
    cart.remove(product)
    return redirect('courses:course_detail')


def cart_detail(request):
	cart = Cart(request)
	return render(request, 'cart/detail.html', {'cart': cart})