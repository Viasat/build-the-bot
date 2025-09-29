# build-a-bot example


## Install

```
# clone the repository
$ git clone git@git.viasat.com:agerami/build-a-bot.git
```
Create a virtualenv and activate it:
```
$ python3 -m venv venv
$ source venv/bin/activate
```
Or on Windows cmd:
```
$ python3 -m venv venv
$ venv\Scripts\activate
```
Install build-a-bot
```
$ pip install -e .
```
Install build_a_bot_example
```
$ cd example
$ pip install -e .
```

## Run
Set the Slack APP_TOKEN and the CHATGPT_API_KEY environment variables
```
$ export APP_TOKEN=<your Slack App token>
$ export SLACK_BOT_TOKEN=<your Slack OAUTH Bot token>
$ export CHATGPT_API_KEY=<your Azure OpenAI ChatGPT API key>
```
Or on Windows cmd:
```
$ set APP_TOKEN=<your Slack App token>
$ set SLACK_BOT_TOKEN=<your Slack OAUTH Bot token>
$ set CHATGPT_API_KEY=<your Azure OpenAI ChatGPT API key>
```
Set your ChatGPT configs (CHATGPT_DEPLOYMENT_NAME, CHATGPT_API_VERSION, CHATGPT_ENDPOINT) at the top of app.py.

Run the app server
```
$ cd example_bot
python app.py
```