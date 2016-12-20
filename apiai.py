from errbot import BotPlugin, cmdfilter
import json
import apiai
import credentials
from datetime import datetime as dt

class ApiAiPlugin(BotPlugin):
    def __init__(self, *args, **kwargs):
        super(ApiAiPlugin, self).__init__(*args, **kwargs)
        self.catch_unprocessed = True
        self.apikey = credentials.apikey
        self.apiai = apiai.ApiAI(self.apikey)

    @cmdfilter
    def apiai_filter(self, msg, cmd, args, dry_run, emptycmd=False):
        if not emptycmd:
            return msg, cmd, args

        matched_prefix = False
        prefixes = self.bot_config.BOT_ALT_PREFIXES + (self._bot.bot_config.BOT_PREFIX,)

        for prefix in prefixes:
            if msg.body.startswith(prefix):
                matched_prefix = True

        if not matched_prefix:
            return msg, cmd, args

        request = self.apiai.text_request()
        request.session_id = msg.frm.person[:36]

        request.query = msg.body

        for prefix in prefixes:
            if request.query.startswith(prefix):
                request.query = request.query.replace(prefix, '', 1).strip()
                break

        separators = self._bot.bot_config.BOT_ALT_PREFIX_SEPARATORS
        for sep in separators:
            if request.query.startswith(sep):
                request.query = request.query.replace(sep, '', 1)

        self.log.debug("API.ai was sent: {}".format(request.query))

        response = request.getresponse().read()

        decoded_response = json.loads(response.decode('utf-8'))

        self.log.debug("API.ai returned: {}".format(decoded_response))

        if decoded_response['status']['errorType'] == 'success':
            speech = decoded_response['result']['fulfillment']['speech']
            if len(speech):
                return speech
            elif decoded_response['result']['action'] == 'notifications.add':
                params = decoded_response['result']['parameters']
                summary = params['summary'] if 'summary' in params else None
                parseddate = params['date'] if 'date' in params else None
                parsedtime = params['time'] if 'time' in params else None

                if not parseddate and not parsedtime:
                    return "I can't set a reminder for that time."

                if parseddate:
                    targetdate = dt.strptime(parseddate, '%Y-%d-%m').date()
                else:
                    targetdate = dt.utcnow().date()

                if parsedtime:
                    targettime = dt.strptime(parsedtime, '%H:%M:%S').time()
                else:
                    targettime = dt.utcnow().time()

                when = dt.combine(targetdate, targettime)
                secondsuntil = (when - dt.utcnow()).seconds

                self.start_poller(secondsuntil,
                                  self.notification_callback,
                                  args=(summary, secondsuntil, msg))

                return "Setting reminder for: {}".format(when)

        return

    def notification_callback(self, summary, secondsuntil, msg):
        self.stop_poller(self.notification_callback,
                         args=(summary, secondsuntil, msg))

        self.log.debug('Notification: {}'.format(summary))
        self.send(msg.frm,
                  groupchat_nick_reply=True,
                  text='Notification: {}'.format(summary))
