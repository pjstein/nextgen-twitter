# NextGen Twitter

A little, tiny twitter bot. 

## Installation

    pipenv install 

## Usage

First, set the following environment variables: 

    TWITTER_CONSUMER_KEY
    TWITTER_CONSUMER_SECRET
    TWITTER_ACCESS_TOKEN_KEY
    TWITTER_ACCESS_TOKEN_SECRET

To run the bot: 

    pipenv run promote --events-path="./events.log.ndjson" --ids-path="./config-files/ids.json" --states-path="./config-files/states.json"

Samples of both `./config-files/ids.json` and `./config-files/states.json` are available in this repository. Their structure is described therein. By default, this application writes its event log to `--events-path`. Different implementations of the event logger could be authored to send the event log elsewhere (like Civis). 