# -*- coding: utf-8 -*-
import re
import subprocess
import os
import os.path

import utils
import config


class fetch_and_store_subtitles():
    def __init__(self):
        self.db = utils.get_connection()
        self.fetch_subtitles()

    def fetch_subtitles(self):
        iplayer_ids = self.fetch_new_episode_ids()
        for iplayer_id in iplayer_ids:
            episode_info = self.fetch_episode_info(iplayer_id)
            if self.db.files.find_one({"pid": episode_info["pid"]}) is not None:
                # episode is already in the db
                print "'%s' has already been processed. Skipping..." % episode_info["title"]
                continue
            # download the file
            print "Downloading: '%s'" % episode_info["title"]
            self.fetch_subtitle_file(episode_info["pid"])
            # save file info to db
            file_db_id = self.db.files.save(episode_info)
            file_path = "%s/%s.srt" % (config.SUBTITLE_DIR, episode_info["fileprefix"])
            print "Processing: '%s'" % episode_info["title"]
            self.process_subtitle_file(file_path, file_db_id)

    def fetch_subtitle_file(self, pid):
        fetch_file_cmd = 'perl get_iplayer.pl --subs-only --output="%s/" --pid=%s' % (config.SUBTITLE_DIR, pid)
        # TODO: check this worked!
        self.__silent_exec(fetch_file_cmd)

    '''
    Fetch a list of IDs for news programmes from the last 24 hours
    '''
    def fetch_new_episode_ids(self):
        list_new_episodes_cmd = 'perl get_iplayer.pl --type=tv --category=news --since=24 --hide --skipdeleted'
        raw_new_episodes = self.__silent_exec(list_new_episodes_cmd)
        return re.findall('\n(\d+):\t', raw_new_episodes)

    def fetch_episode_info(self, iplayer_id):
        interesting_fields = ["categories", "channel", "descshort", "episode", "fileprefix", "name", "pid", "player", "thumbnail", "title"]
        fields_re = "|".join(interesting_fields)
        gi_info_cmd = 'perl get_iplayer.pl --info %s' % iplayer_id
        raw_episode_info = self.__silent_exec(gi_info_cmd)
        episode_info = dict(re.findall('\n(%s): +(.*)' % fields_re, raw_episode_info))
        if 'title' not in episode_info:
            episode_info["title"] = "%s: %s" % (episode_info["name"], episode_info["episode"])
        return episode_info

    # def process_files(self, directory):
    #     # TODO: bit more file checking here
    #     for filename in os.listdir(directory):
    #         self.process_file(directory, filename)

    def process_subtitle_file(self, file_path, file_db_id):
        if not os.path.exists(file_path):
            print "File not found - the download must have failed."
            return
        with open(file_path) as lines:
            while True:
                # ignore the subtitle frame counter
                frame_num = lines.readline()
                if not frame_num:
                    # if we hit this, we're at the end of the file
                    break

                # parse the timestamp
                timestamp = lines.readline()
                t = re.match('(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})\n', timestamp)
                t_from = (int(t.group(1)) * 60 * 60) + (int(t.group(2)) * 60) + int(t.group(3)) + (int(t.group(4)) / 1000.)
                t_to = (int(t.group(5)) * 60 * 60) + (int(t.group(6)) * 60) + int(t.group(7)) + (int(t.group(8)) / 1000.)

                # there may be multiple subtitle lines
                text = ''
                while True:
                    line = lines.readline()
                    if line == '\n':
                        # separator line tells us that's it for this subtitle
                        break
                    # convert to unicode
                    line = line.decode('Windows-1252').encode('utf8').strip()
                    if line == '':
                        # just a blank line. Move on
                        continue
                    if text != '':
                        text = '%s %s' % (text, line)
                    else:
                        text = line
                if text != '':
                    # store the subtitle
                    self.db.subtitles.save({'text': text, 'file': file_db_id, 'from': t_from, 'to': t_to, 'frame_num': frame_num.strip()})

    def __silent_exec(self, cmd):
        with open(os.devnull, "w") as f:
            return subprocess.check_output(cmd, stderr=f, shell=True)

    '''
    Empty the database
    '''
    def __clear(self):
        self.db.subtitles.remove()
        self.db.files.remove()

fetch_and_store_subtitles()
