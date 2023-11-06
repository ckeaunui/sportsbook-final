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
import time

import json

from .models import *
from .forms import *
from .decorators import unauthenticated_user, allowed_users, admin_only


API_KEY = '93bfd6ad9c04dac5206f2584c80d9125'
API_BASE_URL = "https://api.the-odds-api.com/"
SPORTS_URL = f"{API_BASE_URL}v4/sports/?apiKey={API_KEY}"

prop_market_keys = {
    'NFL': {
        'player_pass_tds': 'Pass Touchdowns (Over/Under)',
        'player_pass_yds': 'Pass Yards (Over/Under)',
        'player_pass_completions': 'Pass Completions (Over/Under)',
        'player_pass_attempts':	'Pass Attempts (Over/Under)',
        'player_pass_interceptions': 'Pass Intercepts (Over/Under)',
        'player_pass_longest_completion': 'Pass Longest Completion (Over/Under)',
        'player_rush_yds': 'Rush Yards (Over/Under)',
        'player_rush_attempts': 'Rush Attempts (Over/Under)',
        'player_rush_longest': 'Longest Rush (Over/Under)',
        'player_receptions': 'Receptions (Over/Under)',
        'player_reception_yds':	'Reception Yards (Over/Under)',
        'player_reception_longest':	'Longest Reception (Over/Under)',
        'player_kicking_points': 'Kicking Points (Over/Under)',
        'player_field_goals': 'Field Goals (Over/Under)',
        'player_tackles_assists': 'Tackles + Assists (Over/Under)',
        'player_1st_td': '1st Touchdown Scorer (Yes/No)',
        'player_last_td': 'Last Touchdown Scorer (Yes/No)',
        'player_anytime_td': 'Anytime Touchdown Scorer (Yes/No)'
        },
    'NCAAF': {
        'player_pass_tds': 'Pass Touchdowns (Over/Under)',
        'player_pass_yds': 'Pass Yards (Over/Under)',
        'player_pass_completions': 'Pass Completions (Over/Under)',
        'player_pass_attempts':	'Pass Attempts (Over/Under)',
        'player_pass_interceptions': 'Pass Intercepts (Over/Under)',
        'player_pass_longest_completion': 'Pass Longest Completion (Over/Under)',
        'player_rush_yds': 'Rush Yards (Over/Under)',
        'player_rush_attempts': 'Rush Attempts (Over/Under)',
        'player_rush_longest': 'Longest Rush (Over/Under)',
        'player_receptions': 'Receptions (Over/Under)',
        'player_reception_yds':	'Reception Yards (Over/Under)',
        'player_reception_longest':	'Longest Reception (Over/Under)',
        'player_kicking_points': 'Kicking Points (Over/Under)',
        'player_field_goals': 'Field Goals (Over/Under)',
        'player_tackles_assists': 'Tackles + Assists (Over/Under)',
        'player_1st_td': '1st Touchdown Scorer (Yes/No)',
        'player_last_td': 'Last Touchdown Scorer (Yes/No)',
        'player_anytime_td': 'Anytime Touchdown Scorer (Yes/No)'
        },
    'NBA': {
        'player_points': 'Points (Over/Under)',
        'player_rebounds': 'Rebounds (Over/Under)',
        'player_assists': 'Assists (Over/Under)',
        'player_threes': 'Threes (Over/Under)',
        'player_double_double': 'Double Double (Yes/No)',
        'player_blocks': 'Blocks (Over/Under)',
        'player_steals': 'Steals (Over/Under)',
        'player_turnovers':	'Turnovers (Over/Under)',
        'player_points_rebounds_assists': 'Points + Rebounds + Assists (Over/Under)',
        'player_points_rebounds': 'Points + Rebounds (Over/Under)',
        'player_points_assists': 'Points + Assists (Over/Under)',
        'player_rebounds_assists': 'Rebounds + Assists (Over/Under)'
        },
    'NCAAB': {
        'player_points': 'Points (Over/Under)',
        'player_rebounds': 'Rebounds (Over/Under)',
        'player_assists': 'Assists (Over/Under)',
        'player_threes': 'Threes (Over/Under)',
        'player_double_double': 'Double Double (Yes/No)',
        'player_blocks': 'Blocks (Over/Under)',
        'player_steals': 'Steals (Over/Under)',
        'player_turnovers':	'Turnovers (Over/Under)',
        'player_points_rebounds_assists': 'Points + Rebounds + Assists (Over/Under)',
        'player_points_rebounds': 'Points + Rebounds (Over/Under)',
        'player_points_assists': 'Points + Assists (Over/Under)',
        'player_rebounds_assists': 'Rebounds + Assists (Over/Under)'
        },
    'WNBA': {
        'player_points': 'Points (Over/Under)',
        'player_rebounds': 'Rebounds (Over/Under)',
        'player_assists': 'Assists (Over/Under)',
        'player_threes': 'Threes (Over/Under)',
        'player_double_double': 'Double Double (Yes/No)',
        'player_blocks': 'Blocks (Over/Under)',
        'player_steals': 'Steals (Over/Under)',
        'player_turnovers':	'Turnovers (Over/Under)',
        'player_points_rebounds_assists': 'Points + Rebounds + Assists (Over/Under)',
        'player_points_rebounds': 'Points + Rebounds (Over/Under)',
        'player_points_assists': 'Points + Assists (Over/Under)',
        'player_rebounds_assists': 'Rebounds + Assists (Over/Under)'
        },
    'MLB': {
        'batter_home_runs':	'Batter home runs (Over/Under)',
        'batter_hits': 'Batter hits (Over/Under)',
        'batter_total_bases': 'Batter total bases (Over/Under)',
        'batter_rbis': 'Batter RBIs (Over/Under)',
        'batter_runs_scored': 'Batter runs scored (Over/Under)',
        'batter_hits_runs_rbis': 'Batter hits + runs + RBIs (Over/Under)',
        'batter_singles': 'Batter singles (Over/Under)',
        'batter_doubles': 'Batter doubles (Over/Under)',
        'batter_triples': 'Batter triples (Over/Under)',
        'batter_walks':	'Batter walks (Over/Under)',
        'batter_strikeouts': 'Batter strikeouts (Over/Under)',
        'batter_stolen_bases': 'Batter stolen bases (Over/Under)',
        'pitcher_strikeouts': 'Pitcher strikeouts (Over/Under)',
        'pitcher_record_a_win':	'Pitcher to record a win (Yes/No)',
        'pitcher_hits_allowed':	'Pitcher hits allowed (Over/Under)',
        'pitcher_walks': 'Pitcher walks (Over/Under)',
        'pitcher_earned_runs': 'Pitcher earned runs (Over/Under)',
        'pitcher_outs':	'Pitcher outs (Over/Under)'
        },
    'NHL': {
        'player_points': 'Points (Over/Under)',
        'player_power_play_points':	'Power play points (Over/Under)',
        'player_assists': 'Assists (Over/Under)',
        'player_blocked_shots':	'Blocked shots (Over/Under)',
        'player_shots_on_goal':	'Shots on goal (Over/Under)'
    },
    'AFL': {
        'player_disposals': 'Disposals (Over/Under)',
        'player_disposals_over': 'Disposals (Over only)',
        'player_goal_scorer_first': 'First Goal Scorer (Yes/No)',
        'player_goal_scorer_last': 'Last Goal Scorer (Yes/No)',
        'player_goal_scorer_anytime': 'Anytime Goal Scorer (Yes/No)',
        'player_goals_scored_over': 'Goals scored (Over only)'
    }
}

prop_market_key_options = {
    'player_pass_tds': 'Pass Touchdowns',
    'player_pass_yds': 'Pass Yards',
    'player_pass_completions': 'Pass Completions',
    'player_pass_attempts':	'Pass Attempts',
    'player_pass_interceptions': 'Pass Intercepts',
    'player_pass_longest_completion': 'Pass Longest Completion',
    'player_rush_yds': 'Rush Yards',
    'player_rush_attempts': 'Rush Attempts',
    'player_rush_longest': 'Longest Rush',
    'player_receptions': 'Receptions',
    'player_reception_yds':	'Reception Yards',
    'player_reception_longest':	'Longest Reception',
    'player_kicking_points': 'Kicking Points',
    'player_field_goals': 'Field Goals',
    'player_tackles_assists': 'Tackles + Assists',
    'player_1st_td': '1st Touchdown Scorer',
    'player_last_td': 'Last Touchdown Scorer',
    'player_anytime_td': 'Anytime Touchdown Scorer',

    'player_pass_tds': 'Pass Touchdowns',
    'player_pass_yds': 'Pass Yards',
    'player_pass_completions': 'Pass Completions',
    'player_pass_attempts':	'Pass Attempts',
    'player_pass_interceptions': 'Pass Intercepts',
    'player_pass_longest_completion': 'Pass Longest Completion',
    'player_rush_yds': 'Rush Yards',
    'player_rush_attempts': 'Rush Attempts',
    'player_rush_longest': 'Longest Rush',
    'player_receptions': 'Receptions',
    'player_reception_yds':	'Reception Yards',
    'player_reception_longest':	'Longest Reception',
    'player_kicking_points': 'Kicking Points',
    'player_field_goals': 'Field Goals',
    'player_tackles_assists': 'Tackles + Assists',
    'player_1st_td': '1st Touchdown Scorer',
    'player_last_td': 'Last Touchdown Scorer',
    'player_anytime_td': 'Anytime Touchdown Scorer',

    'player_points': 'Points',
    'player_rebounds': 'Rebounds',
    'player_assists': 'Assists',
    'player_threes': 'Threes',
    'player_double_double': 'Double Double',
    'player_blocks': 'Blocks',
    'player_steals': 'Steals',
    'player_turnovers':	'Turnovers',
    'player_points_rebounds_assists': 'Points + Rebounds + Assists',
    'player_points_rebounds': 'Points + Rebounds',
    'player_points_assists': 'Points + Assists',
    'player_rebounds_assists': 'Rebounds + Assists',

    'player_points': 'Points',
    'player_rebounds': 'Rebounds',
    'player_assists': 'Assists',
    'player_threes': 'Threes',
    'player_double_double': 'Double Double',
    'player_blocks': 'Blocks',
    'player_steals': 'Steals',
    'player_turnovers':	'Turnovers',
    'player_points_rebounds_assists': 'Points + Rebounds + Assists',
    'player_points_rebounds': 'Points + Rebounds',
    'player_points_assists': 'Points + Assists',
    'player_rebounds_assists': 'Rebounds + Assists',

    'player_points': 'Points',
    'player_rebounds': 'Rebounds',
    'player_assists': 'Assists',
    'player_threes': 'Threes',
    'player_double_double': 'Double Double',
    'player_blocks': 'Blocks',
    'player_steals': 'Steals',
    'player_turnovers':	'Turnovers',
    'player_points_rebounds_assists': 'Points + Rebounds + Assists',
    'player_points_rebounds': 'Points + Rebounds',
    'player_points_assists': 'Points + Assists',
    'player_rebounds_assists': 'Rebounds + Assists',

    'batter_home_runs':	'Batter home runs',
    'batter_hits': 'Batter hits',
    'batter_total_bases': 'Batter total bases',
    'batter_rbis': 'Batter RBIs',
    'batter_runs_scored': 'Batter runs scored',
    'batter_hits_runs_rbis': 'Batter hits + runs + RBIs',
    'batter_singles': 'Batter singles',
    'batter_doubles': 'Batter doubles',
    'batter_triples': 'Batter triples',
    'batter_walks':	'Batter walks',
    'batter_strikeouts': 'Batter strikeouts',
    'batter_stolen_bases': 'Batter stolen bases',
    'pitcher_strikeouts': 'Pitcher strikeouts',
    'pitcher_record_a_win':	'Pitcher to record a win',
    'pitcher_hits_allowed':	'Pitcher hits allowed',
    'pitcher_walks': 'Pitcher walks',
    'pitcher_earned_runs': 'Pitcher earned runs',
    'pitcher_outs':	'Pitcher outs',

    'player_points': 'Points',
    'player_power_play_points':	'Power play points',
    'player_assists': 'Assists',
    'player_blocked_shots':	'Blocked shots',
    'player_shots_on_goal':	'Shots on goal',

    'player_disposals': 'Disposals',
    'player_disposals_over': 'Disposals',
    'player_goal_scorer_first': 'First Goal Scorer',
    'player_goal_scorer_last': 'Last Goal Scorer',
    'player_goal_scorer_anytime': 'Anytime Goal Scorer',
    'player_goals_scored_over': 'Goals scored',
    
}


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
            return redirect('dashboard', customer_order='user', bet_filter='Pending', scroll_to='users-body')
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
                return redirect('dashboard', customer_order='user', bet_filter='Pending', scroll_to='users-body')
            else:
                return redirect('sports', sport_group='American Football')
    context = {}
    return render(request, 'accounts/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@admin_only
def dashboard(request, customer_order='user', bet_filter='Pending', scroll_to='None'):
    response = requests.get(SPORTS_URL)
    tokens_used = response.headers['X-Requests-Used']
    total_tokens = int(response.headers['X-Requests-Used']) + int(float(response.headers['X-Requests-Remaining']))
    customers = Customer.objects.all()
    orders = Order.objects.all()
    pending_total = 0
    net_total = 0

    lost_bets = orders.filter(status='Wager Lost')
    won_bets = orders.filter(status='Wager Won')
    pending_bets = orders.filter(status='Pending')
    filtered_bets = orders.filter(status=bet_filter)

    for bet in lost_bets:
        if bet.payment_method == 'Credit':
            net_total -= bet.wager
    
    for bet in won_bets:
        net_total += bet.to_win
    net_total = round(net_total, 2)

    for pending in pending_bets:
        pending_total += pending.wager
    pending_total = round(pending_total, 2)
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()

    # Order customers by query
    customers_sorted = customers.order_by(customer_order)

    
    context = {
        'customers': customers, 
        'customer_order': customer_order,
        'customers_sorted': customers_sorted,

        'filtered_bets': filtered_bets,
        'bet_filter': bet_filter,
        'scroll_to': scroll_to,

        'pending_bets': pending_bets, 
        'tokens_used': tokens_used, 
        'total_tokens': total_tokens, 
        'form': form,
        'pending_total': pending_total,
        'net_total': net_total,
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
        if sport_group == 'American Football':
            load_league = 'americanfootball_nfl'
        else:
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
        return redirect('dashboard', customer_order='user', bet_filter='Pending', scroll_to='users-body')
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
    return redirect('dashboard', customer_order='user', bet_filter='Pending', scroll_to='users-body')


@admin_only
def confirm_delete_user(request, username):
    context = {'username': username}
    return render(request, 'accounts/confirm_delete_user.html', context)


@admin_only
def edit_customer(request, pk):
    print('editing customer')
    customer = Customer.objects.get(id=pk)
    user = customer.user

    form = EditCustomerForm(instance=customer)
    if request.method == 'POST':
        form = EditCustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('dashboard', customer_order='user', bet_filter='Pending', scroll_to='users-body')
    context = {'form': form, 'user': user}
    return render(request, 'accounts/edit_customer.html', context)


@admin_only
def edit_order(request, pk):
    order = Order.objects.get(id=pk)
    customer = Customer.objects.get(pk=order.customer.id)
    old = order.status
    form = OrderForm(instance=order)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():

            # Change the wager back to the pending state
            if old == 'Wager Won':
                customer.balance -= order.to_win
                if order.payment_method == 'Credit':
                    customer.balance -= order.wager
                customer.pending += order.wager
                customer.weekly_profit -= order.to_win
            elif old == 'Wager Lost':
                customer.pending += order.wager
                customer.weekly_profit += order.wager
            elif old == 'Draw':
                if order.payment_method == 'Credit':
                    customer.balance -= order.wager
                elif order.payment_method == 'Freeplay':
                    customer.freeplay -= order.wager
                customer.pending += order.wager
            elif old == 'Void':
                if order.payment_method == 'Credit':
                    customer.balance -= order.wager
                elif order.payment_method == 'Freeplay':
                    customer.freeplay -= order.wager
                customer.pending += order.wager

            # Payouts
            if order.status == 'Wager Won':
                customer.balance += order.to_win
                if order.payment_method == 'Credit':
                    customer.balance += order.wager
                customer.pending -= order.wager
                customer.weekly_profit += order.to_win
            elif order.status == 'Wager Lost':
                customer.pending -= order.wager
                customer.weekly_profit -= order.wager
            elif order.status == 'Draw':
                if order.payment_method == 'Credit':
                    customer.balance += order.wager
                elif order.payment_method == 'Freeplay':
                    customer.freeplay += order.wager
                customer.pending -= order.wager
            elif order.status == 'Void':
                if order.payment_method == 'Credit':
                    customer.balance += order.wager
                elif order.payment_method == 'Freeplay':
                    customer.freeplay += order.wager
                customer.pending -= order.wager

            # Round values
            customer.credit = round(customer.credit, 2)
            customer.balance = round(customer.balance, 2)
            customer.freeplay = round(customer.freeplay, 2)
            customer.pending = round(customer.pending, 2)
            customer.weekly_profit = round(customer.weekly_profit)

            form.save()
            customer.save()
            return redirect('dashboard', customer_order='user', bet_filter='Pending', scroll_to='bets-body')
    context = {'form': form, 'order': order}
    return render(request, 'accounts/edit_order.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer', 'admin'])
def load_table(request, sport_group, league_key, bet_type):
    # CartItem.objects.all().delete()
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
            commence_time_unix = int(match['commence_time'])
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
                    'commence_time': commence_time,
                    'commence_time_unix': commence_time_unix,
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
                            description += "Win Outright "
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
                            description = 'Total ' + description + str(point) + ' '

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
    matches = Match.objects.filter(league=league_key).filter(commence_time_unix__gte=time.time())

    match_ids = matches.values_list('match_id', flat=True).distinct()
    context = {'matches': matches, 'leagues': leagues, 'match_ids': match_ids, 'sport_title': sport_title, 'sport_group': sport_group, 
               'bet_type': bet_type, 'has_draw': has_draw, 'league_key': league_key, 'league_title': league_title, 'in_cart': in_cart, 'prop_market_keys': prop_market_keys.keys()}
    return render(request, 'accounts/load_table.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer', 'admin'])
def checkout(request):
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
            outcome = item.product.description
            price = item.product.price
            wager = item.wager
            cart_item_id = item.id
            max_wager = 0
        
            if price > 0:
                max_wager = round(5000 * 100 / price, 2)
            else:
                max_wager = round(5000 * price / -100, 2)
            row_data = {'date': date, 'game': game, 'outcome': outcome, 'price': price, 'wager': wager, 'cart_item_id': cart_item_id, 'max_wager': max_wager}
            straight_data.append(row_data)

        parlay_odds = 1
        for item in parlay_items:
            date = item.product.match.commence_time
            game = item.product.match.match_name
            outcome = item.product.description
            price = item.product.price
            cart_item_id = item.id

            if price > 0:
                parlay_odds *= 1 + price / 100
            else:
                parlay_odds *= 1 + -100 / price
            
            row_data = {'date': date, 'game': game, 'outcome': outcome, 'price': price, 'cart_item_id': cart_item_id}
            parlay_data.append(row_data)
        parlay_odds -= 1
        parlay_price = 0
        if parlay_odds >= 1:
            parlay_price = round(parlay_odds * 100)
        elif parlay_odds > 0 and parlay_odds < 1:
            parlay_price = round(-100 / parlay_odds)

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
                            if i.product.match == product.match and (i.product.key == 'h2h' or i.product.key == 'spreads') and (product.key == 'h2h' or product.key == 'spreads'):
                                i.delete()

                        elif cart_item.product.key == 'totals':
                            if i.product.match == product.match and i.product.key == 'totals' and product.key == 'totals':
                                i.delete()
                        else:
                            if i.product.match == product.match and i.product.key == product.key and i.product.description.split(":")[0] == product.description.split(":")[0]:
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
    if request.method == 'POST':
        pk = request.POST.get('id', 'None')
        wager = request.POST.get('wager', 'None')
        cart_item = CartItem.objects.get(pk=pk)
        cart_item.wager = float(wager)
        cart_item.save()
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
        payout_date_utx = product.match.commence_time_unix
        dt = datetime.utcfromtimestamp(payout_date_utx) - timedelta(hours=7, minutes=0) 
        payout_date = dt.strftime('%b. %d - %-I:%M %p') 
        to_win = 0
        if price > 0:
            to_win = round(int(price) / 100 * float(wager), 2)
        else:
            to_win = round(-100 /int(price) * float(wager), 2)
        order_item, _ = OrderItem.objects.get_or_create(product=product, price=price)
        order_item.save()
        
        order = Order.objects.create(customer=customer, name=name, description=description, wager=wager, to_win=to_win, status='Pending', price=price, payment_method=payment_method, payout_date_utx=payout_date_utx, payout_date=payout_date)
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
        payout_date_utx = 0

        for cart_item in parlay_items:
            product = cart_item.product
            to_win = 0
            order_item, _ = OrderItem.objects.get_or_create(product=product, price=product.price)
            order_item.save()

            if int(product.match.commence_time_unix) > payout_date_utx:
                payout_date_utx = int(product.match.commence_time_unix)

            if product.price > 0:
                odds *= 1 + product.price / 100
            else:
                odds *= 1 + -100 / product.price

            description += product.match.match_name  + ': ' + product.description + '\n'
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

        dt = datetime.utcfromtimestamp(payout_date_utx) - timedelta(hours=7, minutes=0) 
        payout_date = dt.strftime('%b. %d - %-I:%M %p') 

        order.price = price
        order.description = description
        order.name = str(len(parlay_items)) + ' leg parlay'
        order.payment_method = payment_method
        order.to_win = round(to_win, 2)
        order.payout_date_utx = payout_date_utx
        order.payout_date = payout_date
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
    

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer', 'admin'])
def get_prop_data(request):
    if request.method == 'POST':
        match_id = request.POST.get('match_id', 'None')
        prop_key = request.POST.get('prop_key', 'None')
        sport_group = request.POST.get('sport_group', 'None')
        PROP_URL = f"{API_BASE_URL}v4/sports/{sport_group}/events/{match_id}/odds?apiKey={API_KEY}&regions=us&oddsFormat=american&markets={prop_key}"
        response = requests.get(PROP_URL)
        prop_data = response.json()
        prop_data_str = json.dumps(prop_data)

        if 'message' not in prop_data.keys():        
            match = Match.objects.get(match_id=match_id)
            prop_data_str = {}

            if len(prop_data['bookmakers']) > 0:
                for outcome in prop_data['bookmakers'][0]['markets'][0]['outcomes']:

                    winner = outcome['name']
                    price = outcome['price']
                    point = 0
                    if 'point' in outcome.keys():
                        point = outcome['point']
                        
                    description = outcome['description'] + ": " + winner + " " + str(point) + " " + prop_market_key_options[prop_key]
                    product, _ = Product.objects.update_or_create(
                        match = match,
                        key = prop_key,
                        winner = winner,
                        description = description,
                        defaults = {
                            'price': price,
                            'point': point,       
                    })

                    row_data = {}
                    row_data['winner'] = winner
                    row_data['price'] = price
                    row_data['point'] = point
                    row_data['id'] = product.id

                    if outcome['description'] in prop_data_str:
                        prop_data_str[outcome['description']].append(row_data)

                    else:
                        prop_data_str[outcome['description']] = [row_data]
                prop_data_str = json.dumps(prop_data_str)
                return HttpResponse(prop_data_str)
            else:
                return HttpResponse("No Data Available")

        else:
            return HttpResponse("No Data Available")


def place_casino_wager(request):
    if request.method =='POST':
        print('Creating')
        customer = request.user.customer
        wager = request.POST.get('wager', 'None')
        game = request.POST.get('game', 'None')
        result  = request.POST.get('outcome', 'None')
        payout = request.POST.get('payout', 'None')
        casino_wager = CasinoWager.objects.create(customer=customer, wager=wager, payout=payout, game=game, result=result)

        return HttpResponse("Wager Confirmed")


