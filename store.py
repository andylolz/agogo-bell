# -*- coding: utf-8 -*-

import os
import re

from bson.objectid import ObjectId

import utils
import config


class store():
    def __init__(self):
        directory = config.SUBTITLE_DIR
        self.process_files(directory)

    def __clear(self):
        db = utils.get_connection()
        db.lookup.remove()
        db.subtitles.remove()
        db.files.remove()

    def process_files(self, directory):
        db = utils.get_connection()

        alphanum_re = re.compile('[^a-zA-Z0-9 ]+', re.UNICODE)
        for filename in os.listdir(directory):
            self.process_file(filename)

    def process_file(self, filename):
        if not filename.endswith('.srt'):
            # not a subtitle file, so skip it
            print '%s is not a subtitle file. Skipping...' % filename
            continue

        if db.files.find({'filename': filename}).count() > 0:
            # file has already been processed, so skip it
            print '%s has already been processed. Skipping...' % filename
            continue

        with open('subtitles/%s' % filename) as fileobj:
            # store subtitle file info
            # todo: store a bit more information here
            file_id = db.files.save({'filename': filename})

            print 'Processing: %s' % filename
            while True:
                # ignore the subtitle frame counter
                line = fileobj.readline()
                if not line:
                    break

                # parse the timestamp
                line = fileobj.readline()
                t = re.match('(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n', line)
                t_from = t.group(1)
                t_to = t.group(2)

                # there may be multiple subtitle lines
                while True:
                    # separator line tells us that's it
                    line = fileobj.readline()
                    if line == '\n':
                        break
                    # convert to unicode
                    line = line.decode('Windows-1252').encode('utf8')
                    # remove non alphanumeric characters, and tokenise
                    words = alphanum_re.sub('', line).lower().split()
                    if words == []:
                        continue
                    # store the subtitle
                    subtitle_id = db.subtitles.save({'line': line, 'file': file_id, 'from': t_from, 'to': t_to})
                    for word in words:
                        # store the tokens
                        db.lookup.save({'word': word, 'subtitle': subtitle_id})
