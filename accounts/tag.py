from django import template
import requests

register = template.Library()


@register.assignment_tag
def loadLeagues(sport_group):
    API_KEY = 'dce9a665f6077a42401131fc4acf8589'
    API_BASE_URL = "https://api.the-odds-api.com/"
    SPORTS_URL = f"{API_BASE_URL}v4/sports/?apiKey={API_KEY}"

    response = requests.get(SPORTS_URL)
    sports = response.json()
    leagues = []

    for sport in sports:
        if sport['group'] == sport_group and not sport['has_outrights']:
            leagues.append(sport)
    
    return leagues