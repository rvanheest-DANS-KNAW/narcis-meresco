import simplejson as json
from urllib2 import Request, urlopen, URLError
from meresco.core import Observable
import ConfigParser
from os.path import abspath, dirname, join


class RecordPidToAuthNid(Observable):

	def __init__(self):
		Observable.__init__(self)
		config = ConfigParser.RawConfigParser()
		config.read(join(dirname(abspath(__file__)), '..', 'conf', 'app_config.cfg'))
		pidgraph_api = config.get('PidGraph API', 'url')
		self._pidgraph_api = pidgraph_api
		print "PidGraph API:", pidgraph_api

	def lookupNameIds(self, pidlist):
		if len(pidlist) > 0:
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
