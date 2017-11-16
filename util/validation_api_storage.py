import os
from lxml.etree import parse, XMLSchema
import datetime
import logging.handlers

STORAGE_DIR = '/data/meresco/api/store/'
LOG_FILENAME = '/home/meresco/xml_validation/log/validation.log'
SHORT_SCHEMA = '/home/meresco/xsd/knaw_short.xsd'
LONG_SCHEMA = '/home/meresco/xsd/knaw_long.xsd'

### Local / Testing properties ######
#STORAGE_DIR = '/home/vesaa/meresco/testintegration-examples-seecr-vesaa/api/store/'
# LOG_FILENAME = '/home/vesaa/meresco/xml_validation/log/validation.log'
# SHORT_SCHEMA = '/home/vesaa/narcis-meresco/meresco/xsd/knaw_short.xsd'
# LONG_SCHEMA = '/home/vesaa/narcis-meresco/meresco/xsd/knaw_long.xsd'
### ! Local / Testing properties ######

if os.path.exists(LOG_FILENAME):
    os.remove(LOG_FILENAME)

MAX_LOGSIZE = 10485760
logger = logging.getLogger('ValidationLogger')
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, backupCount=14, maxBytes=MAX_LOGSIZE)
formatter = logging.Formatter("%(asctime)s - %(message)s", "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info('### Start validation of knaw_short and knaw_long xml files in %s' % STORAGE_DIR)
logger.info('NOTE: only failed validations are logged!')
logger.info('Start time: %s\n' % datetime.datetime.now())

xmlschema_doc = parse(SHORT_SCHEMA)
xmlschema_short = XMLSchema(xmlschema_doc)
xmlschema_doc = parse(LONG_SCHEMA)
xmlschema_long = XMLSchema(xmlschema_doc)

total_short = 0
total_short_invalid = 0
total_long = 0
total_long_invalid = 0
total_long_invalid_topic = 0

# Loop over api storage
for item in os.listdir(STORAGE_DIR):
    path = os.path.join(STORAGE_DIR, item)
    if os.path.isdir(path):

        count_short = 0
        count_short_invalid = 0
        count_long = 0
        count_long_invalid = 0
        count_long_invalid_topic = 0

        logger.info('### Start validation of xml files in %s' % path)
        print('### Start validation of xml files in %s' % path)

        for subdir, dirs, files in os.walk(path):
            if "knaw_short" in files or "knaw_long" in files:
                for file in files:
                    if file.startswith('knaw_short') or file.startswith('knaw_long'):
                        file_path = os.path.join(subdir, file)
                        xml_file = open(file_path)
                        contents = parse(xml_file)
                        xml_file.close()
                        if file.startswith('knaw_short'):
                            count_short += 1
                            if not xmlschema_short.validate(contents):
                                count_short_invalid += 1
                                logger.error("ERROR in validating " + file_path)
                                logger.error("    " + xmlschema_short.error_log.last_error.message)
                                print("ERROR in validating " + file_path)
                        else:
                            count_long += 1
                            if not xmlschema_long.validate(contents):
                                count_long_invalid += 1
                                if not xmlschema_long.error_log.last_error.message.startswith("Element '{http://www.knaw.nl/narcis/1.0/long/}topic': Missing child element(s). Expected is ( {http://www.knaw.nl/narcis/1.0/long/}topicValue"):
                                    logger.error("ERROR in validating " + file_path)
                                    logger.error("    " + xmlschema_long.error_log.last_error.message)
                                    print("ERROR in validating " + file_path)
                                else:
                                    count_long_invalid_topic += 1

        logger.info('%d knaw_short files validated' % count_short)
        logger.info('%d invalid knaw_short files' % count_short_invalid)
        logger.info('%d knaw_long files validated' % count_long)
        logger.info('%d invalid knaw_long files' % count_long_invalid)
        if count_long_invalid_topic > 0:
            logger.info('%d invalid knaw_long files, caused by erroneous Topic' % count_long_invalid_topic)
        logger.info('### Finished validation of xml files in %s\n' % path)
        total_short += count_short
        total_short_invalid += count_short_invalid
        total_long += count_long
        total_long_invalid += count_long_invalid
        total_long_invalid_topic += count_long_invalid_topic

logger.info('Total %d knaw_short files validated' % total_short)
logger.info('Total %d invalid knaw_short files' % total_short_invalid)
logger.info('Total %d knaw_long files validated' % total_long)
logger.info('Total %d invalid knaw_long files' % total_long_invalid)
if total_long_invalid_topic > 0:
    logger.info('Total %d invalid knaw_long files, caused by erroneous Topic\n' % total_long_invalid_topic)
logger.info('End time: %s' % datetime.datetime.now())
logger.info('### Ready: Finished validating xml files. ###')
