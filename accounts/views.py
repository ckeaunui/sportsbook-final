from django.shortcuts import render, redirect
import requests
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.http import HttpResponse
from django.forms import formset_factory
from datetime import datetime, timedelta
from django.http import HttpResponseRedirect
from django.views.generic import View
import operator

import json

from .models import *
from .forms import *

from .decorators import unauthenticated_user, allowed_users, admin_only


API_KEY = '93bfd6ad9c04dac5206f2584c80d9125'
API_BASE_URL = "https://api.the-odds-api.com/"
SPORTS_URL = f"{API_BASE_URL}v4/sports/?apiKey={API_KEY}"


@admin_only
def registerPage(request):
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            group = Group.objects.get(name='customer')
            user.groups.add(group)
            user = authenticate(request, username=username, password=password)
            return redirect('dashboard')
    context = {'form': form}
    return render(request, 'accounts/register.html', context)


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Replace with actual users name
            if username == 'admin':
                return redirect('dashboard')
            else:
                return redirect('sports', sport_group='American Football')
    context = {}
    return render(request, 'accounts/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@admin_only
def dashboard(request):
    response = requests.get(SPORTS_URL)
    tokens_used = response.headers['X-Requests-Used']
    total_tokens = int(response.headers['X-Requests-Used']) + int(float(response.headers['X-Requests-Remaining']))
    customers = Customer.objects.all()
    orders = Order.objects.all()
    pending_bets = orders.filter(status='Pending')
    pending_total = 0
    for pending in pending_bets:
        pending_total += pending.wager
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
    context = {
        'customers': customers, 
        'orders': orders, 
        'pending_bets': pending_bets, 
        'tokens_used': tokens_used, 
        'total_tokens': total_tokens, 
        'form': form,
        'pending_total': pending_total,
    }
    return render(request, 'accounts/dashboard.html', context) 


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer', 'admin'])
def sports(request, sport_group):
    response = requests.get(SPORTS_URL)
    sports = response.json()
    leagues = []
    load_league = None
    for sport in sports:
        if sport['group'] == sport_group and not sport['has_outrights']:
            leagues.append(sport)
    if len(leagues) > 0:
        load_league = leagues[0]['key']
        return redirect('load_table', sport_group=sport_group, league_key=load_league, bet_type='straight')
    context = {'leagues': leagues, 'sport_group': sport_group}
    return render(request, 'accounts/sports.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer', 'admin'])
def userPage(request):
    group = None
    if request.user.groups.exists():
        group = request.user.groups.all()[0].name
    if group == "customer":
        customer = request.user.customer
        orders = Order.objects.filter(status='Pending')
        user_orders = orders.filter(customer=customer)
        context = {'user_orders': user_orders}
        return render(request, 'accounts/profile.html', context)
    elif group == "admin":
        return redirect('dashboard')
    else:
        return redirect('login')


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer', 'admin'])
def casino(request):
    context = {}
    return render(request, 'accounts/casino.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer', 'admin'])
def roulette(request):
    customer = request.user.customer
    customer.balance = round(customer.balance, 2)
    customer.credit = round(customer.credit, 2)
    context = {'customer': customer}
    return render(request, 'accounts/roulette.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer', 'admin'])
def blackjack(request):
    customer = request.user.customer
    customer.balance = round(customer.balance, 2)
    customer.credit = round(customer.credit, 2)
    context = {'customer': customer}
    return render(request, 'accounts/blackjack.html', context)


@admin_only
def delete_user(request, username):
    user = User.objects.filter(username=username)
    user.delete()
    return redirect('dashboard')


@admin_only
def edit_user(request, pk):
    customer = Customer.objects.get(id=pk)
    form = EditUserForm(instance=customer)
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    context = {'form': form}
    return render(request, 'accounts/edit_user.html', context)


@admin_only
def edit_order(request, pk):
    order = Order.objects.get(id=pk)
    customer = Customer.objects.get(pk=order.customer.id)
    old = order.status
    form = OrderForm(instance=order)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            if old == 'Pending':
                # remove wager amount from pending
                customer.pending -= order.wager
            elif old == 'Wager Won':
                # Remove to_win from balance
                customer.balance -= order.to_win
            elif old == 'Wager Lost':
                # add wager to balance
                customer.balance += order.wager  
                customer.freeplay -= 0.2 * order.wager
            elif old == 'Draw':
                if order.payment_method == 'Credit':
                    customer.balance -= order.wager
                elif order.payment_method == 'Freeplay':
                    customer.freeplay -= order.wager
            
            if order.status == 'Pending':
                # add wager to pending
                customer.pending += order.wager
            elif order.status == 'Wager Won':
                # Add to_win to balance
                customer.balance += order.to_win
            elif order.status == 'Wager Lost':
                customer.freeplay += 0.2 * order.wager
            elif order.status == 'Draw':
                if order.payment_method == 'Credit':
                    customer.balance += order.wager
                elif order.payment_method == 'Freeplay':
                    customer.freeplay += order.wager
            customer.balance = round(customer.balance, 2)
            customer.freeplay = round(customer.freeplay, 2)
            customer.pending = round(customer.pending, 2)
            form.save()
            customer.save()
            return redirect('dashboard')
    context = {'form': form, 'order': order}
    return render(request, 'accounts/edit_order.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer', 'admin'])
def load_table(request, sport_group, league_key, bet_type):
    # Fetch this leagues game data and save all bets as products
    leagues = []
    sport_title = None
    league_title = None
    has_draw = False
    in_cart = {}
   
    customer = request.user.customer
    cart, _ = Cart.objects.get_or_create(customer=customer)
    for i in CartItem.objects.filter(cart=cart):
        in_cart[i.product.id] = i.wager

    if league_key is not None:
        matches_url = f"{API_BASE_URL}v4/sports/{league_key}/odds?regions=us&oddsFormat=american&dateFormat=unix&markets=spreads,h2h,totals&apiKey={API_KEY}"
        response = requests.get(matches_url)
        matches_data = response.json()
        league_response = requests.get(SPORTS_URL)
        sports = league_response.json()

        for sport in sports:
            if sport['group'] == sport_group and not sport['has_outrights']:
                leagues.append(sport)
                if league_key == sport['key']:
                    league_title = sport['title']
        
        for match in matches_data:  # make the matches
            if len(match['bookmakers']) <= 0:
                continue

            match_id = match['id']
            sport_title = sport['title']
            commence_time = datetime.utcfromtimestamp(int(match['commence_time'])) - timedelta(hours=7, minutes=0) 
            commence_time = commence_time.strftime('%b. %d - %-I:%M %p') 
            match['commence_time'] = commence_time
            team1 = ""
            team2 = ""

            if match['home_team'] < match['away_team']:
                team1 = match['home_team']
                team2 = match['away_team']
            else:
                team1 = match['away_team']
                team2 = match['home_team']

            match_name = team1 + " vs. " + team2
            obj, created = Match.objects.update_or_create(
            match_id=match_id,
                defaults = {
                    'league': league_key,
                    'sport_title': sport_title,
                    'match_name': match_name,
                    'team1': team1,
                    'team2': team2,
                    'commence_time': commence_time
                }
            )

            for market in match['bookmakers'][0]['markets']:
                key = market['key']

                for outcome in market['outcomes']:
                    winner = outcome['name']
                    display_data = ""
                    description = winner + ' '

                    point = None
                    price = outcome['price']
                    if winner == 'Draw':
                        has_draw = True
                    
                    if key == 'spreads':
                        point = outcome['point']
                        if point == 0:
                            continue
                        else:
                            if point >= 0:
                                display_data += '+'
                                description += '+'
                            display_data += str(point) + ' '
                            description += str(point) + ' '
                            if price >= 0:
                                display_data += '+'
                            display_data += str(price)
                            
                    elif key == 'h2h':
                        if winner != 'Draw':
                            description += "Outright "
                        if price >= 0:
                            display_data += '+'
                        display_data += str(price)

                    elif key == 'totals':
                        point = outcome['point']
                        if point == 0:
                            continue
                        else:
                            ou = {'Over': 'O', 'Under': 'U'}
                            display_data = f"{ou[winner]} {point} "
                            description += str(point) + ' '

                            if price > 0:
                                display_data +=  '+' 
                            display_data += str(price)

                    if price > 0:
                        max_wager = round(5000 * 100 / price, 2)
                    else:
                        max_wager = round(5000 * price / -100, 2)

                    Product.objects.update_or_create(
                        match = obj, 
                        key = key,
                        winner = winner,
                        defaults = {
                            'price': price,
                            'display_data': display_data,
                            'description': description,
                            'max_wager': max_wager,
                            'point': point,
                                           
                    })

    leagues = sorted(leagues, key=operator.itemgetter('title'))
    # Gather data to send to view
    matches = Match.objects.filter(league=league_key)
    match_ids = matches.values_list('match_id', flat=True).distinct()
    context = {'matches': matches, 'leagues': leagues, 'match_ids': match_ids, 'sport_title': sport_title, 'sport_group': sport_group, 
               'bet_type': bet_type, 'has_draw': has_draw, 'league_key': league_key, 'league_title': league_title, 'in_cart': in_cart}
    return render(request, 'accounts/load_table.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer', 'admin'])
def checkout(request):
    # OrderItem.objects.all().delete()
    context = {}
    if request.method == 'POST':
        customer = request.user.customer
        cart = Cart.objects.get(customer=customer)
        cart_items = CartItem.objects.filter(cart=cart)
        straight_items = cart_items.filter(wager_type='Straight')
        parlay_items = cart_items.filter(wager_type='Parlay')

        straight_data = []
        parlay_data = []

        for item in straight_items:
            date = item.product.match.commence_time
            game = item.product.match.match_name
            outcome = item.product.winner
            price = item.product.price
            wager = item.wager
            cart_item_id = item.id
            max_wager = 0
            description_suffix = item.product.point
            if item.product.key == 'h2h':
                if item.product.winner != 'Draw':
                    description_suffix = 'Wins Outright'
            else:
                description_suffix = item.product.point

            
            if price > 0:
                max_wager = round(5000 * 100 / price, 2)
            else:
                max_wager = round(5000 * price / -100, 2)
            row_data = {'date': date, 'game': game, 'outcome': outcome, 'price': price, 'wager': wager, 'cart_item_id': cart_item_id, 'max_wager': max_wager, 'description_suffix': description_suffix}
            straight_data.append(row_data)

        parlay_odds = 1
        for item in parlay_items:
            date = item.product.match.commence_time
            game = item.product.match.match_name
            outcome = item.product.winner
            price = item.product.price
            cart_item_id = item.id
            description_suffix = ""
            if item.product.key == 'h2h':
                if item.product.winner != 'Draw':
                    description_suffix = 'Wins Outright'
            else:
                description_suffix = item.product.point

            if price > 0:
                parlay_odds *= 1 + price / 100
            else:
                parlay_odds *= 1 + -100 / price
            
            row_data = {'date': date, 'game': game, 'outcome': outcome, 'price': price, 'cart_item_id': cart_item_id, 'description_suffix': description_suffix}
            parlay_data.append(row_data)
        parlay_odds -= 1
        parlay_price = round(parlay_odds * 100)
        parlay_max_wager = 100
        if parlay_odds != 0:
            parlay_max_wager = round(5000 * 100 / parlay_odds) / 100

        context = {'straight_data': straight_data, 'parlay_data': parlay_data, 'parlay_price': parlay_price, 'parlay_max_wager': parlay_max_wager, 'customer': customer}
        return render(request, 'accounts/checkout.html', context)
    return render(request, 'accounts/profile.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer', 'admin'])
def order_placed(request, pk):
    order = Order.objects.get(pk=pk)
    context = {'order': order}
    return render(request, 'accounts/order_placed.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer', 'admin'])
def add_to_cart(request):
    # Order.objects.all().delete()
    customer = request.user.customer
    if request.method == 'POST':
        cart = Cart.objects.get(customer=customer)
        bet_type = request.POST.get('bet_type', 'None')
        product = None
        cart_item = None
        if bet_type == 'straight':
            wager = request.POST.get('value', 'None')
            name = request.POST.get('name', 'None')
            if 'bet-id:' in name:
                bet_id = name.replace('bet-id:', '')
                product = Product.objects.get(pk=bet_id)
                if wager == '' or None:
                    cart_item = CartItem.objects.get(cart=cart, product=product, wager_type='Straight')
                    cart_item.delete()
                else:
                    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, wager_type='Straight')
                    cart_item.wager =float(wager)
                    cart_item.save()
        elif bet_type == 'parlay':
            product_id = request.POST.get('value', 'None')
            product = Product.objects.get(pk=product_id)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, wager_type='Parlay')

            if created:
                cart_item.save()
                # Check if a conflicting bet is in the cart, and deactivate it
                for i in CartItem.objects.filter(cart=cart):
                    if i.wager_type == 'Parlay':
                        if i == cart_item:
                            continue

                        if (cart_item.product.key == 'h2h' or cart_item.product.key == 'spreads'):
                            print('check1')
                            if i.product.match == product.match and (i.product.key == 'h2h' or i.product.key == 'spreads') and (product.key == 'h2h' or product.key == 'spreads'):
                                print('p1')
                                i.delete()

                        elif cart_item.product.key == 'totals':
                            print('check2')
                            if i.product.match == product.match and i.product.key == 'totals' and product.key == 'totals':
                                print('p2')
                                i.delete()
            else:
                cart_item.delete()
        return HttpResponse(status=200)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer', 'admin'])
def remove_from_cart(request):
    pk = request.POST.get('id', 'None')
    cart_item = CartItem.objects.get(pk=pk)
    cart_item.delete()
    return HttpResponse(status=200)
    

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer', 'admin'])
def edit_wager(request):
    print("Updating...")
    if request.method == 'POST':
        pk = request.POST.get('id', 'None')
        wager = request.POST.get('wager', 'None')
        print('pk:', pk)
        print('wager:', wager)
        cart_item = CartItem.objects.get(pk=pk)
        cart_item.wager = float(wager)
        cart_item.save()
        return HttpResponse(status=200)


def prop_clicked(request):
    if request.method == 'GET':
        return HttpResponse(status=200)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer', 'admin'])
def place_order(request):
    customer = request.user.customer
    cart = Cart.objects.get(customer=customer)
    cart_items = CartItem.objects.filter(cart=cart)
    payment_method = request.POST.get('payment-method')
    straight_items = cart_items.filter(wager_type='Straight')
    parlay_items = cart_items.filter(wager_type='Parlay')

    # Place an order for each cart item labeled straight
    for cart_item in straight_items:
        product = cart_item.product
        wager = float(cart_item.wager)
        description = product.description
        price = product.price
        name = product.match.match_name
        to_win = 0
        if price > 0:
            to_win = round(int(price) / 100 * float(wager), 2)
        else:
            to_win = round(-100 /int(price) * float(wager), 2)
        order_item, _ = OrderItem.objects.get_or_create(product=product, price=price)
        order_item.save()
        
        order = Order.objects.create(customer=customer, name=name, description=description, wager=wager, to_win=to_win, status='Pending', price=price, payment_method=payment_method)
        order.products.add(order_item)
        order.save()

        cart_item.delete()
        customer_obj = Customer.objects.get(pk=customer.id)

        # Update balance on confirmed screen
        if payment_method == 'Credit':
            customer.balance -= float(wager)
            customer_obj.balance -= float(wager)

        elif payment_method == 'Freeplay':
            customer.freeplay -= float(wager)
            customer_obj.freeplay -= float(wager)

        customer.pending += float(wager)
        customer.pending = round(customer.pending, 2)
        customer.balance = round(customer.balance, 2)
        customer.freeplay = round(customer.freeplay, 2)

        # Update balance in customer object
        customer_obj.pending += float(wager)
        customer_obj.pending = round(customer_obj.pending, 2)
        customer_obj.save()
    
    if len(parlay_items) > 0:
        # Place one order with products and description containing each parlay cartitems information
        wager = float(request.POST.get('parlay-wager', 'None'))
        order = Order.objects.create(customer=customer, status='Pending', wager=wager)
        odds = 1
        description = ""

        for cart_item in parlay_items:
            product = cart_item.product
            to_win = 0
            order_item, _ = OrderItem.objects.get_or_create(product=product, price=product.price)
            order_item.save()
            if order_item.price > 0:
                odds *= order_item.price / 100
            else:
                odds *= 1 + -100 / order_item.price
            description += order_item.product.match.match_name  + ': ' + order_item.product.description + '\n---\n'
            order.products.add(order_item)
            cart_item.delete()
        
        # Add data to order and save it
        if odds >= 2:
            price = (odds - 1) * 100
        else:
            price = -100 / (odds - 1)
        price = round(price)

        to_win = 0
        if price > 0:
            to_win = round(int(price) / 100 * float(wager), 2)
        else:
            to_win = round(-100 /int(price) * float(wager), 2)

        order.price = price
        order.description = description
        order.name = str(len(parlay_items)) + ' leg parlay'
        order.payment_method = payment_method
        order.to_win = round(to_win, 2)
        order.save()

        customer_obj = Customer.objects.get(pk=customer.id)

        # Update balance on confirmed screen
        if payment_method == 'Credit':
            customer.balance -= float(wager)
            customer_obj.balance -= float(wager)

        elif payment_method == 'Freeplay':
            customer.freeplay -= float(wager)
            customer_obj.freeplay -= float(wager)

        customer.pending += float(wager)
        customer.pending = round(customer.pending, 2)
        customer.balance = round(customer.balance, 2)
        customer.freeplay = round(customer.freeplay, 2)

        # Update balance in customer object
        customer_obj.pending += float(wager)
        customer_obj.pending = round(customer_obj.pending, 2)
        customer_obj.save()
    context = {}
    return render(request, 'accounts/place_order.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer', 'admin'])
def place_wager(request):
    if request.method == 'POST':
        wager = request.POST.get('amount', 'None')
        customer = request.user.customer
        customer.balance -= float(wager)
        customer.balance = round(customer.balance, 2)
        customer.save()
        return HttpResponse(status=200)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer', 'admin'])
def add_to_balance(request):
    amount = request.POST.get('amount', 'None')
    customer = request.user.customer
    customer.balance += float(amount)
    customer.balance = round(customer.balance, 2)
    customer.save()
    return HttpResponse(status=200)

