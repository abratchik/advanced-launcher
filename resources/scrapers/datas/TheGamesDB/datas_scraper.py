# -*- coding: UTF-8 -*-
import os
from xbmcaddon import Addon
import requests
import json

base_url = "https://api.thegamesdb.net"
__settings__ = Addon(id="plugin.program.advanced.launcher")


# Return Game search list
def _get_games_list(search):
    path = "/Games/ByGameName"
    params = {
        "apikey": __settings__.getSetting("thegamesdb_api_key"),
        "name": search,
        "include": "platform",
        "fields": "overview,genres,platform"
    }

    results = []
    display = []
    url = base_url + path
    r = requests.get(url, params=params)
    data = r.json()
    for item in data['data']['games']:
        game = {}
        game["id"] = item['id']
        game["title"] = str(item['game_title'].encode('utf-8'))
        game['release'] = str(item['release_date'].encode('utf-8')) if item['release_date'] is not None else ""
        game['plot'] = str(item['overview'].encode('utf-8')) if item['overview'] is not None else ""
        game['studio'] = item['developers'] if item['developers'] is not None else []
        game['genre'] = item['genres'] if item['genres'] is not None else []
        game["gamesys"] = str(data['include']['platform'][str(item['platform'])]['name'].encode('utf-8'))
        game["order"] = 1
        if game["title"].lower() == search.lower():
            game["order"] += 1
        if game["title"].lower().find(search.lower()) != -1:
            game["order"] += 1
        results.append(game)
    results.sort(key=lambda result: result["order"], reverse=True)
    for result in results:
        display.append(result["title"] + " / " + result["gamesys"])

    return results, display


# Return 1st Game search
def _get_first_game(search, gamesys):
    platform = _system_conversion(gamesys)
    path = "/Games/ByGameName"
    params = {
        "apikey": __settings__.getSetting("thegamesdb_api_key"),
        "name": search,
        "include": "platform",
        "fields": "overview,genres,platform"
    }
    if platform is not None:
        params.update({"filter[platform]": platform})

    results = []
    url = base_url + path

    r = requests.get(url, params=params)
    data = r.json()

    for item in data['data']['games']:
        game = {}
        game["id"] = item['id']
        game["title"] = str(item['game_title'].encode('utf-8'))
        game['release'] = str(item['release_date'].encode('utf-8')) if item['release_date'] is not None else ""
        game['plot'] = str(item['overview'].encode('utf-8')) if item['overview'] is not None else ""
        game['studio'] = item['developers'] if item['developers'] is not None else []
        game['genre'] = item['genres'] if item['genres'] is not None else []
        game["gamesys"] = str(data['include']['platform'][str(item['platform'])]['name'].encode('utf-8'))
        game["order"] = 1
        if game["title"].lower() == search.lower():
            game["order"] += 1
        if game["title"].lower().find(search.lower()) != -1:
            game["order"] += 1
        results.append(game)
    results.sort(key=lambda result: result["order"], reverse=True)
    return results


# Return Game data
def _get_game_data(game_object):
    params = {
        "apikey": __settings__.getSetting("thegamesdb_api_key")
    }

    dev_path = '/Developers'
    url = base_url + dev_path
    r = requests.get(url, params=params)
    dev_data = r.json()

    studios = []
    for d in game_object['studio']:
        studios.append(dev_data['data']['developers'][str(d)]['name'])

    genre_path = '/Genres'
    url = base_url + genre_path
    r = requests.get(url, params=params)
    genre_data = r.json()

    genres = []
    for g in game_object['genre']:
        genres.append(genre_data['data']['genres'][str(g)]['name'])

    gamedata = {}
    gamedata["genre"] = str((', '.join(genres)).encode('utf-8'))
    gamedata["release"] = str(game_object['release'].encode('utf-8'))
    gamedata["studio"] = str((', '.join(studios)).encode('utf-8'))

    gamedata["plot"] = str(game_object['plot'].encode('utf-8'))

    return gamedata


def _system_conversion(system_id):
    try:
        rootDir = Addon(id="plugin.program.advanced.launcher").getAddonInfo('path')
        if rootDir[-1] == ';': rootDir = rootDir[0:-1]
        with open(os.path.join(rootDir, 'resources', 'scrapers', 'game-systems.json')) as jsonfile:
            data = json.loads(jsonfile.read())
        keys_orig = data.keys()
        keys = [s.lower() for s in keys_orig]
        if system_id.lower() in keys:
            return data[keys_orig[keys.index(system_id.lower())]]['TheGamesDB']
    except:
        return ''
