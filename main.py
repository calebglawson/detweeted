import json
from datetime import datetime, timedelta

import tweepy
import typer

APP = typer.Typer()

def _make_config(config_path):
    '''
    Load the config from a file.
    '''
    try:
        config = open(config_path)
        return json.load(config)
    except:
        return None

def _make_api(config):
    '''
    Make a Tweepy api object.
    '''
    auth = tweepy.OAuthHandler(
        config.get('consumer_key'),
        config.get('consumer_secret')
    )

    auth.set_access_token(
        config.get('access_token'),
        config.get('access_token_secret')
    )

    api = tweepy.API(
        auth,
        wait_on_rate_limit=True
    )

    return api

def main(config: str):
    _config = _make_config(config)
    _api = _make_api(_config)

    for status in tweepy.Cursor(_api.user_timeline, since_id=_config.get('last_id'), include_rts=False, exclude_replies=True).items():       
        if status.created_at < datetime.utcnow() - timedelta(hours=_config.get('expiry_in_hours', 4)) and status.favorite_count == 0 and status.retweet_count == 0:
            typer.echo(f'Bye bye!! No love for: {status.text}')
            status.destroy()
        
        _config['last_id'] = status.id_str

    with open(config, 'w') as f:
        f.write(json.dumps(_config))
        f.truncate()

if __name__ == "__main__":
    typer.run(main)