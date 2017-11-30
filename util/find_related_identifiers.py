import os
from lxml.etree import parse, tostring
import datetime
import logging.handlers

STORAGE_DIR = '/data/meresco/api/store/dans/'
# LOG_FILENAME = '/home/meresco/xml_validation/log/validation.log'

### Local / Testing properties ######
# STORAGE_DIR = '/home/vesaa/meresco/testintegration-examples-seecr-vesaa/api/store/'
LOG_FILENAME = '/home/vesaa/meresco/xml_validation/log/related_identifiers.log'
### ! Local / Testing properties ######

if os.path.exists(LOG_FILENAME):
    os.remove(LOG_FILENAME)

MAX_LOGSIZE = 10485760
logger = logging.getLogger('FindRelatedIdentifiersLogger')
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, backupCount=14, maxBytes=MAX_LOGSIZE)
formatter = logging.Formatter("%(asctime)s - %(message)s", "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info('### Start loooking for related identifiers in %s' % STORAGE_DIR)
logger.info('Start time: %s\n' % datetime.datetime.now())

total_found = 0
doi = 0
urn = 0
other = 0

# Loop over api storage
for item in os.listdir(STORAGE_DIR):
    path = os.path.join(STORAGE_DIR, item)
    if os.path.isdir(path):

        found = 0
        logger.info('### Start looking for related identifiers in %s' % path)
        # print('### Start looking for related identifiers in %s' % path)

        for subdir, dirs, files in os.walk(path):
            if "knaw_long" in files:
                for file in files:
                    if file.startswith('knaw_long'):
                        file_path = os.path.join(subdir, file)
                        xml_file = open(file_path)
                        contents = tostring(parse(xml_file))
                        xml_file.close()
                        relid_ind_1 = contents.find('<related_identifier')
                        if relid_ind_1 >= 0:
                            # relid_ind_2 = relid_ind_1 + contents[relid_ind_1:].find('>') + 1
                            relid_ind_2 = relid_ind_1 + 19
                            relid_ind_3 = contents[relid_ind_2:].find('</related_identifier>')
                            related_identifier = contents[relid_ind_2 : relid_ind_2 + relid_ind_3]
                            if not related_identifier.startswith('http') and not related_identifier.startswith('www'):
                                found += 1
                                if related_identifier.startswith('10'):
                                    doi += 1
                                elif related_identifier.startswith('urn'):
                                    urn += 1
                                else:
                                    other += 1
                                logger.info("related identifier in %s: %s" % (file, related_identifier))
                                print("related identifier in %s  %s" % (subdir[subdir.rfind('/') + 1:], related_identifier))

        logger.info('%d related identifiers found' % found)
        print('%d related identifiers found' % found)
        total_found += found

logger.info('Total %d related identifiers found' % total_found)
print('Total %d related identifiers found' % total_found)
print('Total %d doi' % doi)
print('Total %d urn' % urn)
print('Total %d other' % other)
logger.info('End time: %s' % datetime.datetime.now())
logger.info('### Ready: Finished looking for related items. ###')