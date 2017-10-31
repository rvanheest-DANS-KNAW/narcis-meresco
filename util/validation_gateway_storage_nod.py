import os
from StringIO import StringIO
from lxml.etree import parse, XMLSchema, tostring
import datetime
import logging.handlers

STORAGE_DIR = '/data/meresco/gateway/store/'
LOG_FILENAME = '/home/meresco/xml_validation/log/validation_nod.log'
PERSON_SCHEMA = '/home/meresco/xsd/person.xsd'
ORGANISATION_SCHEMA = '/home/meresco/xsd/organisation.xsd'
RESEARCH_SCHEMA = '/home/meresco/xsd/research.xsd'

### Local / Testing properties ######
# STORAGE_DIR = '/home/vesaa/meresco/testintegration-examples-seecr-vesaa/gateway/store/'
# LOG_FILENAME = '/home/vesaa/meresco/xml_validation/log/validation_nod.log'
# PERSON_SCHEMA = '/home/vesaa/narcis-meresco/meresco/xsd/person.xsd'
# ORGANISATION_SCHEMA = '/home/vesaa/narcis-meresco/meresco/xsd/organisation.xsd'
# RESEARCH_SCHEMA = '/home/vesaa/narcis-meresco/meresco/xsd/research.xsd'
### ! Local / Testing properties ######

NOD_COLLECTIONS = ['organisation', 'person', 'research']

if os.path.exists(LOG_FILENAME):
    os.remove(LOG_FILENAME)

MAX_LOGSIZE = 10485760
logger = logging.getLogger('ValidationLogger')
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, backupCount=14, maxBytes=MAX_LOGSIZE)
formatter = logging.Formatter("%(asctime)s - %(message)s", "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info('### Start validation of person, organisation and research entities in normdoc files in %s' % STORAGE_DIR)
logger.info('NOTE: only failed validations are logged!')
logger.info('Start time: %s\n' % datetime.datetime.now())

xmlschema_doc = parse(PERSON_SCHEMA)
xmlschema_person = XMLSchema(xmlschema_doc)
xmlschema_doc = parse(ORGANISATION_SCHEMA)
xmlschema_organisation = XMLSchema(xmlschema_doc)
xmlschema_doc = parse(RESEARCH_SCHEMA)
xmlschema_research = XMLSchema(xmlschema_doc)

# Loop over api storage
for item in os.listdir(STORAGE_DIR):
    path = os.path.join(STORAGE_DIR, item)
    if os.path.isdir(path) and item in NOD_COLLECTIONS:

        logger.info('### Start validation of xml files in %s' % path)
        print('### Start validation of xml files in %s' % path)

        count_person = 0
        count_person_invalid = 0
        count_organisation = 0
        count_organisation_invalid = 0
        count_research = 0
        count_research_invalid = 0

        if item == 'person':
            for subdir, dirs, files in os.walk(path):
                if "normdoc" in files:
                    for file in files:
                        file_path = os.path.join(subdir, file)
                        xml = tostring(parse(file_path))
                        person_xml = xml[xml.index('&lt;persoon'): xml.index('&lt;/persoon&gt;') + 16]
                        person_xml = person_xml.replace('&lt;', '<').replace('&gt;', '>')
                        person = parse(StringIO(person_xml))
                        count_person += 1
                        if not xmlschema_person.validate(person):
                            count_person_invalid += 1
                            logger.error("ERROR in validating " + file_path)
                            logger.error("    " + xmlschema_person.error_log.last_error.message)
                            print("ERROR in validating " + file_path)
            logger.info('%d person normdocs validated' % count_person)
            logger.info('%d invalid person normdocs' % count_person_invalid)
        elif item == 'organisation':
            for subdir, dirs, files in os.walk(path):
                if "normdoc" in files:
                    for file in files:
                        file_path = os.path.join(subdir, file)
                        xml = tostring(parse(file_path))
                        organisation_xml = xml[xml.index('&lt;organisatie'): xml.index('&lt;/organisatie&gt;') + 20]
                        organisation_xml = organisation_xml.replace('&lt;', '<').replace('&gt;', '>')
                        organisation = parse(StringIO(organisation_xml))
                        count_organisation += 1
                        if not xmlschema_organisation.validate(organisation):
                            count_organisation_invalid += 1
                            logger.error("ERROR in validating " + file_path)
                            logger.error("    " + xmlschema_organisation.error_log.last_error.message)
                            print("ERROR in validating " + file_path)
            logger.info('%d organisation normdocs validated' % count_organisation)
            logger.info('%d invalid organisation normdocs' % count_organisation_invalid)
        elif item == 'research':
            for subdir, dirs, files in os.walk(path):
                if "normdoc" in files:
                    for file in files:
                        file_path = os.path.join(subdir, file)
                        xml = tostring(parse(file_path))
                        research_xml = xml[xml.index('&lt;activiteit'): xml.index('&lt;/activiteit&gt;') + 19]
                        research_xml = research_xml.replace('&lt;', '<').replace('&gt;', '>')
                        research = parse(StringIO(research_xml))
                        count_research += 1
                        if not xmlschema_research.validate(research):
                            count_research_invalid += 1
                            logger.error("ERROR in validating " + file_path)
                            logger.error("    " + xmlschema_research.error_log.last_error.message)
                            print("ERROR in validating " + file_path)
            logger.info('%d research normdocs validated' % count_research)
            logger.info('%d invalid research normdocs' % count_research_invalid)

        logger.info('### Finished validation of xml files in %s\n' % path)

logger.info('End time: %s' % datetime.datetime.now())
logger.info('### Ready: Finished validating xml files. ###')
