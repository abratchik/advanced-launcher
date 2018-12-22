# -*- coding: UTF-8 -*-

import os
import requests
from xbmcaddon import Addon
import json
import xbmc

base_url = "https://api.thegamesdb.net"
__settings__ = Addon(id="plugin.program.advanced.launcher")


# Thumbnails list scrapper
def _get_thumbnails_list(system, search, region, imgsize):
    path = "/Games/ByGameName"
    params = {
        "apikey": __settings__.getSetting("thegamesdb_api_key"),
        "name": search,
        "include": "boxart"
    }

    url = base_url + path
    r = requests.get(url, params=params)
    data = r.json()

    prefixes = data['include']['boxart']['base_url']
    try:
        image_base_url = prefixes[imgsize]
    except:
        image_base_url = prefixes['large']

    image_thumb_url = prefixes['thumb']

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

    xbmc.log("Selected title: " + results[0]['title'], level=xbmc.LOGNOTICE)
    xbmc.log("Selected id: " + str(games_id), level=xbmc.LOGNOTICE)

    boxarts = []
    for i, item in enumerate(data['include']['boxart']['data'][str(games_id)]):
        boxarts.append((image_base_url + item['filename'], image_thumb_url + item['filename'], "Boxart " + str(i + 1)))
    return boxarts


# Get Thumbnail scrapper
def _get_thumbnail(image_url):
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
