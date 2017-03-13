import os, shutil, glob
import xml.etree.ElementTree
import urllib
import gzip
import datetime
import logging.handlers
from bsddb import btopen

STORAGE_DIR = '/data/meresco/api/store/'
MAX_FILE_ENTRIES = 20000 # LETOP: dit dient een even getal te zijn (i.v.m. MultiLangual collections count)!!
SITEMAP_PROXY_DIR = '/home/meresco/www/sitemaps'

### Local / Testing properties ######
#STORAGE_DIR = 'storage'
#MAX_FILE_ENTRIES = 2000  # LETOP: dit dient een even getal te zijn (i.v.m. MultiLangual collections)!!
#SITEMAP_PROXY_DIR = 'sitemaps'
### ! Local / Testing properties ######

SITEMAP_TEMP_DIR = 'sitemaps_temp'

MULTI_LANGUAL = ['person', 'organisation', 'research']
# Order does matter:
WCP_COLLECTIONS = ['publication', 'dataset', 'organisation', 'person', 'research']
BDB_NAMES = WCP_COLLECTIONS + ['gscholar']

collection_prio_map = dict(zip(WCP_COLLECTIONS, ["1.0", "1.0", "1.0", "1.0", "1.0"]))
LANGUAGE = ['en', 'nl']
BDB_DIR = 'berkeleydb'
DB_DELIMIT = '#@'

LOG_FILENAME = 'log/sitemapper.log'
MAX_LOGSIZE = 10485760

END_SITEMAP = '''</urlset>'''
END_SITEMAP_IDX = '''</sitemapindex>'''
START_SITEMAP = '''<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'''
START_SITEMAP_IDX = '''<?xml version="1.0" encoding="UTF-8"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'''
STATICPAGES = '''<sitemap><loc>http://www.narcis.nl/sitemap_staticpages.xml</loc><lastmod>2015-08-10T14:22:22Z</lastmod></sitemap>'''

ms_logger = logging.getLogger('SitemapLogger')
ms_logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, backupCount=14, maxBytes=MAX_LOGSIZE)
formatter = logging.Formatter("%(asctime)s - %(message)s", "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
ms_logger.addHandler(handler)


def emptyfolder(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
                # elif os.path.isdir(file_path): shutil.rmtree(file_path) # Uncomment to delete all subfolders as well.
        except Exception, e:
            print e


# First get the repo dirs with collection = publication only from WCP (dir).
ms_logger.info('### Start generating sitemaps in %s' % SITEMAP_TEMP_DIR)
ms_logger.info('Start time: %s' % datetime.datetime.now())
emptyfolder(SITEMAP_TEMP_DIR)
emptyfolder(BDB_DIR)
ms_logger.info('Deleted temporary sitemaps (%s) and indexes (%s)' % (SITEMAP_TEMP_DIR, BDB_DIR))

# Global record counter:
cnt = 0

ms_logger.info('Start reading meresco storage in: %s' % STORAGE_DIR)

# Create and open our indexes:
bdbmap = {}
for bdb in BDB_NAMES:
    bdbmap[bdb] = btopen(os.path.join(BDB_DIR, bdb + ".bdb"), 'n')
# Loop over meresco storage:
for subdir, dirs, files in os.walk(STORAGE_DIR):
    # if subdir == STORAGE_DIR:
    #     dirs[:] = [d for d in dirs if d in publication_dirs]
    #     ms_logger.info('Dirs to sitemap: %s' % dirs)
    if "knaw_short" in files:  # Found existing (non-deleted) record dir.
        # reset our state/counters stuff:
        record = []
        hasAbstract = False
        isOpenAccess = False
        strCollection = ''
        abstract = ''

        # File-list is alfabetisch gesort: header, knaw_short, meta. Wij willen meta first, dus we reversen de file map.
        #for bestand in reversed(files):
        for bestand in reversed(files):
            # print os.path.join(subdir, file)
            if bestand == 'knaw_short' and strCollection == "publication":
                knaw_short = xml.etree.ElementTree.parse(os.path.join(subdir, bestand)).getroot()
                rights = knaw_short.find('{http://www.knaw.nl/narcis/1.0/short/}accessRights')
                abstract = knaw_short.find(
                    '{http://www.knaw.nl/narcis/1.0/short/}metadata/{http://www.knaw.nl/narcis/1.0/short/}abstract')
                if rights is not None and rights.text is not None:
                    isOpenAccess = True if ("open" in rights.text.lower()) else False
                if abstract is not None and abstract.text is not None:
                    hasAbstract = True if (len(abstract.text.encode('utf-8')) > 10) else False
            elif bestand == 'meta':
                meta = xml.etree.ElementTree.parse(os.path.join(subdir, bestand)).getroot()
                oai_id = meta.find(
                    '{http://meresco.org/namespace/harvester/meta}record/{http://meresco.org/namespace/harvester/meta}id')
                harvestdate = meta.find(
                    '{http://meresco.org/namespace/harvester/meta}record/{http://meresco.org/namespace/harvester/meta}harvestdate')
                collection = meta.find(
                    '{http://meresco.org/namespace/harvester/meta}repository/{http://meresco.org/namespace/harvester/meta}collection')
                if oai_id is None or harvestdate is None or collection is None:
                    break  # skip this dir and rest of the files in it...
                strCollection = collection.text.strip().lower()
                record.append(urllib.quote(oai_id.text, ''))  # oai identifier: encode slashes.
                record.append(harvestdate.text)  # lastmod => harvestdate

        # Both 'meta' and 'knaw_short' have now been processed: Add priority:
        if strCollection == "publication":
            record.append("1.0" if isOpenAccess else "0.8")
        else:
            record.append(collection_prio_map.get(strCollection))

        # Get appropiate index/bdb to add the reocrd to:
        cnt += 1
        if strCollection == "publication" and (hasAbstract or isOpenAccess):  # Add to scholar sitemap:
            bdbmap.get("gscholar")[record[1] + str(cnt)] = DB_DELIMIT.join(record)
        # Add to the regular sitemap BDB's, according to collection:
        bdbmap.get(strCollection)[record[1] + str(cnt)] = DB_DELIMIT.join(record)

        if cnt % 10000 == 0:
            ms_logger.info('Records processed: %s' % cnt)

for k, v in bdbmap.iteritems():
    v.sync()
    # print k, len(v.items())
    ms_logger.info(k + ": " + str(len(v.items())) + " records.")

ms_logger.info('Finished reading (and synching db) meresco storage to Berkerly DBs. Total records count: %s' % cnt)

def get_sorted_sitemap_items(bdb):
    int_total = len(bdb.items())
    yield bdb.last()[1]
    for i in range(1, int_total):
        yield bdb.previous()[1]

def sm_item2xml(str_items, collectie):

    item_list = str(str_items).rsplit(DB_DELIMIT)

    if collectie in MULTI_LANGUAL:
        return '''  <url>
        <loc>http://www.narcis.nl/%(collection)s/RecordID/%(oai_id)s/Language/nl</loc>
        <lastmod>%(last_mod)s</lastmod>
        <priority>%(prio)s</priority>
    </url>\n    <url>
        <loc>http://www.narcis.nl/%(collection)s/RecordID/%(oai_id)s/Language/en</loc>
        <lastmod>%(last_mod)s</lastmod>
        <priority>%(prio)s</priority>
    </url>\n''' % {
            'collection': collectie,
            'oai_id': item_list[0],
            'last_mod': item_list[1],
            'prio': item_list[2]}
    else:
        return '''  <url>
        <loc>http://www.narcis.nl/%(collection)s/RecordID/%(oai_id)s</loc>
        <lastmod>%(last_mod)s</lastmod>
        <priority>%(prio)s</priority>
    </url>\n''' % {
            'collection': collectie,
            'oai_id': item_list[0],
            'last_mod': item_list[1],
            'prio': item_list[2]}


def idx_fname2xml(sm_filename):
    return '''<sitemap>
    <loc>http://www.narcis.nl/%s</loc>
    <lastmod>%s</lastmod>
</sitemap>\n''' % (sm_filename, datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%dT%H:%M:%SZ'))


# Create google scholar maps:
smfile_number = 0

idx_gs_file = open(SITEMAP_TEMP_DIR + os.path.sep + 'sitemap_scholar_index.xml', 'w')
ms_logger.info('Opened scholar sitemap index file: %s.' % idx_gs_file.name)

idx_gs_file.write(START_SITEMAP_IDX)
curr_sm_filename = ''

for counter, sm_item in enumerate(get_sorted_sitemap_items(bdbmap.get("gscholar"))):
    if counter % MAX_FILE_ENTRIES == 0:  # Reset all counters, open new sitemapfile
        if smfile_number > 0:
            smf.write(END_SITEMAP)
            smf.close()
            ms_logger.debug('Closed scholar sitemap file: %s.' % curr_sm_filename)
            idx_gs_file.write(idx_fname2xml(curr_sm_filename))
            ms_logger.info('Wrote finished scholar sitemap file into index file: %s.' % curr_sm_filename)
        curr_sm_filename = 'sitemap_scholar_%s.xml.gz' % smfile_number
        smf = gzip.open(SITEMAP_TEMP_DIR + os.path.sep + curr_sm_filename, 'w')
        ms_logger.debug('Opened scholar sitemap file: %s.' % curr_sm_filename)
        smf.write(START_SITEMAP)
        smfile_number += 1
    smf.write(sm_item2xml(sm_item, "publication"))

smf.write(END_SITEMAP)
smf.close()
ms_logger.info('Closed last scholar sitemap file: %s.' % curr_sm_filename)

# Write last gs sitemap to gs index:
idx_gs_file.write(idx_fname2xml(curr_sm_filename))

# Close scholar db and remove from our db dict{}:
bdbmap.get("gscholar").close()
del bdbmap["gscholar"]

###### Create regular sitemaps:

# Open index file:
idx_file = open(SITEMAP_TEMP_DIR + os.path.sep + 'sitemap_index.xml', 'w')
ms_logger.info('Opened regular sitemap index file: %s.' % idx_file.name)

idx_file.write(START_SITEMAP_IDX)
curr_sm_filename = ''

# iedere BDB uitloopen in custom volgorde:
for collection_key in WCP_COLLECTIONS:
    db = bdbmap.get(collection_key)
    smfile_number = 0
    counter = 0
    for sm_item in get_sorted_sitemap_items(db):
        if counter % MAX_FILE_ENTRIES == 0:  # Reset all counters, open new sitemapfile
            if smfile_number > 0:
                smf.write(END_SITEMAP)
                smf.close()
                ms_logger.debug('Closed regular sitemap file: %s.' % curr_sm_filename)
                idx_file.write(idx_fname2xml(curr_sm_filename))
                if collection_key == 'research': # registreer research sitemap url ook in scholar index.
                    idx_gs_file.write(idx_fname2xml(curr_sm_filename))
                ms_logger.info('Wrote regular finished sitemap file into index file: %s.' % curr_sm_filename)
            curr_sm_filename = 'sitemap_%s_%s.xml.gz' % (collection_key, smfile_number)
            smf = gzip.open(SITEMAP_TEMP_DIR + os.path.sep + curr_sm_filename, 'w')
            ms_logger.debug('Opened regular sitemap file: %s.' % curr_sm_filename)
            smf.write(START_SITEMAP)
            smfile_number += 1
        smf.write(sm_item2xml(sm_item, collection_key))
        if collection_key in MULTI_LANGUAL:
            counter += 2
        else:
            counter += 1

    smf.write(END_SITEMAP)
    smf.close()
    ms_logger.info('Closed last regular sitemap file: %s.' % curr_sm_filename)
    idx_file.write(idx_fname2xml(curr_sm_filename)) # registreer sitemap url in index.
    if collection_key == 'research': # registreer research sitemap url ook in scholar index.
        idx_gs_file.write(idx_fname2xml(curr_sm_filename))

idx_file.write(STATICPAGES)
idx_file.write(END_SITEMAP_IDX)
idx_gs_file.write(END_SITEMAP_IDX)
idx_file.close()
idx_gs_file.close()

for v in bdbmap.itervalues():
    v.close()

ms_logger.info('Finished generating sitemaps in temp-dir.')

ms_logger.info('Copying all newly created sitemaps from temp-dir to narcis portal proxy dir.')

for smapfile in glob.iglob(os.path.join(SITEMAP_TEMP_DIR, "*.*")):
     shutil.copy(smapfile, SITEMAP_PROXY_DIR)

ms_logger.info('End time: %s' % datetime.datetime.now())
ms_logger.info('### Ready: Finished generating sitemaps. ###')
