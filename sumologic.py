from errbot import BotPlugin, botcmd

import logging
import datetime
import pprint

log = logging.getLogger(name='errbot.plugins.Sumologic')

try:
    import requests
except ImportError:
    log.error("Please install 'requests' python package")

try:
    import sumologic
except ImportError:
    log.error("Please install 'sumologic' python package")


class Sumologic(BotPlugin):

    def get_configuration_template(self):
        """ configuration entries """
        config = {
            'username': u'api_username',
            'password': u'api_password',
            'pastebin_url': u'url',
        }
        return config

    def _connect(self):
        client = sumologic.client.Client(
            auth=(
                self.config['username'],
                self.config['password']
            )
        )
        return client

    def _parse_results(self, results, limit):

        response = []

        try:
            results['data'][0]
            results_set = results['data']
        except KeyError:
            response.append('{0}: {1}'.format(
                results['response'],
                results['reason'])
            )
        except IndexError:
            response.append('No records found.')
        else:
            # parse the stuff
            pastebin_url = self.pastebin(results_set)
            text = 'Showing {0} of {1} results. {2}'.format(
                limit,
                len(results_set),
                pastebin_url
            )
            log.info(text)
            response.append(text)

        clean_response = ' '.join(response)
        return clean_response

    def pastebin(self, data):
        ''' Post the output to pastebin '''
        pretty_data = pprint.pformat(data)
        url = requests.post(
            self.config['pastebin_url'],
            data={
                'content': pretty_data,
            },
        )
        return url.text.strip('"')

    @botcmd(split_args_with=' ')
    def collector_remove(self, msg, args):
        """ removes a collector by name """
        client = self._connect()
        collector_name = args.pop(0)
        collector = sumologic.Collectors(client)
        collector.delete(collector_name)
        message = 'collector {0} deleted.'.format(collector_name)
        self.send(msg.frm,
                  '{0}: {1}'.format(msg.nick, message),
                  message_type=msg.type)

    @botcmd
    def sumologic_search(self, msg, args):
        """ runs a search and returns the first 10 results """
        client = self._connect()
        search = sumologic.search.Search(client)

        # setup dates
        time_now = datetime.datetime.now().replace(second=0, microsecond=0)
        right_now = time_now.isoformat()
        minutes_ago = (time_now - datetime.timedelta(minutes=5)).isoformat()

        options = {}
        options['tz'] = 'UTC'
        options['from'] = minutes_ago
        options['to'] = right_now
        options['format'] = 'json'
        options['limits'] = 10

        results = search.query(args, **options)
        message = self._parse_results(results, options['limits'])
        self.send(msg.frm,
                  '{0}: {1}'.format(msg.nick, message),
                  message_type=msg.type)
