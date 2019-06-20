import simplejson as json
from urllib2 import Request, urlopen, URLError
from meresco.core import Observable
import ConfigParser
from os.path import abspath, dirname, join


class RecordPidToAuthNid(Observable):

	def __init__(self):
		Observable.__init__(self)
		config = ConfigParser.ConfigParser()
		config.read(join(dirname(abspath(__file__)), '..', 'conf', 'application.ini'))
		self._pidgraph_api = config.get('IndexServer', 'pidGraphUrl')
		self._pidgraph_enabled = config.getboolean('IndexServer', 'pidGraphIsEnabled')
		print "PidGraph API:", self._pidgraph_api,". IsEnabled:", self._pidgraph_enabled

	def lookupNameIds(self, pidlist):
		if len(pidlist) > 0 and self._pidgraph_enabled:
			req = Request(self._pidgraph_api + '?' + "&".join(list(map(lambda x: 'pid='+x, pidlist))), headers={'User-Agent': "Meresco Index Server"})
			try:
				data = json.load(urlopen(req))
				for nid in data:
					yield nid
			except URLError as e:
				if hasattr(e, 'reason'):
					print 'Failed to reach https://test.pidgraph.narcis.nl endpoint.'
					print 'Reason: ', e.reason
				elif hasattr(e, 'code'):
					print 'The https://test.pidgraph.narcis.nl couldn\'t fulfill the request.'
					print 'Error code: ', e.code
