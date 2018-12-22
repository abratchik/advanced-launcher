# -*- coding: UTF-8 -*-

import os
import xbmc
import requests
from xbmcaddon import Addon
import json

base_url = "https://api.thegamesdb.net"
__settings__ = Addon(id="plugin.program.advanced.launcher")


# Fanarts list scrapper
def _get_fanarts_list(system, search, imgsize):
    platform = _system_conversion(system)
    path = "/Games/ByGameName"
    params = {
        "apikey": __settings__.getSetting("thegamesdb_api_key"),
        "name": search
    }
    if platform is not None:
        params.update({"filter[platform]": platform})

    url = base_url + path
    r = requests.get(url, params)
    data = r.json()
    results = []
    for item in data['data']['games']:
        game = {}
        game["id"] = item['id']
        game["title"] = str(item['game_title'].encode('utf-8'))
        game["order"] = 1
        if game["title"].lower() == search.lower():
            game["order"] += 1
        if game["title"].lower().find(search.lower()) != -1:
            game["order"] += 1
        results.append(game)
    results.sort(key=lambda result: result["order"], reverse=True)

    games_id = results[0]['id']

    path = "/Games/Images"
    image_params = {
        "apikey": __settings__.getSetting("thegamesdb_api_key"),
        "games_id": games_id,
        "filter[type]": "fanart,screenshot"
    }

    url = base_url + path
    r = requests.get(url, image_params)
    data = r.json()

    prefixes = data['data']['base_url']
    try:
        image_base_url = prefixes[imgsize]
    except:
        image_base_url = prefixes['large']

    image_thumb_url = prefixes['thumb']

    full_fanarts = []

    if len(data['data']['images']) > 0:
        for index, image in enumerate(data['data']['images'][str(games_id)]):
            full_fanarts.append((image_base_url + image['filename'], image_thumb_url + image['filename'], image['type'] + " " + str(index)))

    return full_fanarts


# Get Fanart scrapper
def _get_fanart(image_url):
    return image_url


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
