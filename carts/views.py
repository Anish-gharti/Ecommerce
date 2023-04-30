from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from django.http import HttpResponse
from .models import Cart, CartItem
# Create your views here.

def _cart_id(request):
    session_key = request.session.session_key
    if not session_key:
        session_key = request.session.create()
    return session_key      

def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []
    if request.method == "POST":
        for item in request.POST:
            key = item
            value = request.POST[key]
            
            try:
                variation = Variation.objects.get(variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass    
     
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()


    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.quantity+= 1
        cart_item.save()
    
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=1,
        )
        cart_item.save()

    return redirect('cart')

def remove_from_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')    
  

def delete_cart_item(request, product_id):   
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)     
    cart_item.delete() 
    return redirect('cart')



def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = 0.02 * total
        grand_total = total + tax    
    except Cart.DoesNotExist:
        pass
    context = {
        'grand_total': grand_total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'total':total,
    }        
    return render(request, 'store/cart.html', context)