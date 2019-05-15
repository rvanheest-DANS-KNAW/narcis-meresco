import simplejson as json
from urllib2 import Request, urlopen, URLError


class RecordPidToAuthNid(object):

	def lookupNameIds(self, pidlist):
		print "LookupNameIds..."
		# for pid in pidlist:
		# 	print "RECEIVED:", pid
		# # https://test.pidgraph.narcis.nl/nid?pid=doi:10.1002/lno.10611&pid=wos:000423029300003
		if len(pidlist) > 0:
			print "https://test.pidgraph.narcis.nl/nid?" + "&".join(list(map(lambda x: 'pid='+x, pidlist)))
			req = Request('http://localhost:8011/nid?'+ "&".join(list(map(lambda x: 'pid='+x, pidlist))), headers={'User-Agent': "Meresco Index Server (v???)"})
			# req = Request('http://localhost:8011/nid?pid=doi:10.1002/lno.10611&pid=wos:000423029300003', headers={'User-Agent': "Meresco Index Server (v???)"})
			
			try:
				data = json.load(urlopen(req))
				for nid in data:
					print "NID FROM PID-GRAPH:", nid
					yield nid
				# yield 'dai-nl:068519397'
				# print "NID FROM PID-GRAPH: dai-nl:068519397"
			except URLError as e:
				if hasattr(e, 'reason'):
					print 'Failed to reach https://test.pidgraph.narcis.nl endpoint.'
					print 'Reason: ', e.reason
				elif hasattr(e, 'code'):
					print 'The https://test.pidgraph.narcis.nl couldn\'t fulfill the request.'
					print 'Error code: ', e.code

			# for nid in data['pids']:
			# 	yield (nid['value'], nid['pidType'])

####################################
		# response = urllib2.urlopen('https://test.pidgraph.narcis.nl/nid?') # http://localhost:9080/blaat.. wellicht sneller. https://test.pidgraph.narcis.nl/person/PRS1326072, https://test.pidgraph.narcis.nl/nid?
		# data = json.load(response)
		# for nid in data['pids']:
		# 	yield (nid['value'], nid['pidType'])

# {'pids': [{'pidType': 'orcid', 'source': 'sysvsoi', 'value': '0000-0001-7013-0116'}, {'pidType': 'isni', 'source': 'narcis-idx', 'value': '0000000393537060'}, {'pidType': 'dai-nl', 'source': 'narcis-idx', 'value': '273313045'}, {'pidType': 'scopus', 'source': 'orcid', 'value': '6602492995'}, {'pidType': 'researcherid', 'source': 'orcid', 'value': 'B-9767-2016'}, {'pidType': 'dai-nl', 'source': 'sysvsoi', 'value': 'info:eu-repo/dai/nl/273313045'}, {'pidType': 'nod-person', 'source': 'sysvsoi', 'value': 'PRS1326072'}], 'id': 'PRS1326072'}