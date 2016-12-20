# errbot-apiai
api.ai integration with errbot

# Basic usage

You'll need a credentials.py in the same directory as the module.  This file should contain your apikey from API.ai

You'll also need the apiai module (see requirements.txt).

Finally, you'll need to make sure that you have the CommandNotFound core plugin.  Currently, it lives at the https://github.com/tamarintech/errbot master branch but there is an open PR.  Disable the CommandNotFoundFilter core plugin and this module should start working immediately.


# How it works

Any unhandled text is sent through to API.ai to answer.  See the API.ai for creating a new agent and configuring it.  This is also where you find your API key.

For this demonstration, we have enabled the _Small Talk_ and _Reminders and Notifications_ domains.  You should see the API.ai requests and responses in your debug logs if you want to find out exactly what is happening.

If you have an existing training or intents already defined then they will work "out of the box".


# Gotchas

Some of the _Reminders and Notifications_ seem kind of questionable.  If you ask it to "remind me in 1 decade to ..." it will set a reminder for 30 minutes.  If you ask for units of time smaller than one minute (ie: 30 seconds) it will not send back any time or date information to schedule the event.  This is not a bug for this plugin - that is currently how API.ai "understands" those items. :)
