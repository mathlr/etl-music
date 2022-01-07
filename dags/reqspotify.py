def get_cred (CLIENT_ID,CLIENT_SECRET):
    import requests

    AUTH_URL = 'https://accounts.spotify.com/api/token'
# POST
    auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    })
# convert the response to JSON
    auth_response_data = auth_response.json()
# save the access token
    return auth_response_data['access_token']


def search_req(track,artist,album,type_q,token,quick=False):
    import urllib
    import requests
 
    track='+track:{track}'.format(track=urllib.parse.quote(track)) if (track != '') else ''
    album='+album:{album}'.format(album=urllib.parse.quote(album)) if (album != '' ) else ''
    artist='artist:{artist}'.format(artist=urllib.parse.quote(artist)) if (artist != '') else ''
    
    if artist+album+track == '':
        raise Exception('No filters provided.')

    query='?q='
    if type_q == 'artist':
        query=query+artist
    elif type_q == 'album':
        query=query+artist+album
    elif type_q == 'track':
        query=query+artist+album+track
    else:
        raise Exception('Types allowed: artist, album, track. Type used: '+type_q)

    if quick:
        if query.count(':') == 1:
            query='?q='+query.split(':')[1]
        else:
            raise Exception('For quick search, only 1 filter is accepted. Filters used: '+query)

    endpoint = 'https://api.spotify.com/v1/search/'
    type_s = '&type={type}'.format(type=type_q)
    req = requests.get(endpoint+query+type_s, headers={'Authorization': 'Bearer {token}'.format(token=token)})

    return req