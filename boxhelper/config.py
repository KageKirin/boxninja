
def load_settings(filename = '.boxsettings'):
    import json
    with open(filename, 'r') as settingsfile:
        settings = json.load(settingsfile)
        #print(settings)
        return settings


### self test
if __name__ == '__main__':
    s = load_settings()
    assert s is not None
    print(s)
    assert type(s['client_id']) is str
    assert type(s['client_secret']) is str
    assert type(s['access_token']) is str

