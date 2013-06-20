Agogo Bell – a searchable iPlayer subtitle database
==

Search BBC iPlayer programmes for occurrences of a word or phrase, and
provide a link to (or embed) the iPlayer programme at the timestamp where
the word or phrase occurred.

How does it work?
--
Using Phil Lewis’ excellent
[get_iplayer](http://linuxcexntre.net/getiplayer), we can download and
index iPlayer subtitles. We store timestamps, so it’s possible to embed
the original iplayer content.

```
get_iplayer --info --type=tv --category=news --exclude-channel=parliament --since=24 --hide --skipdeleted --subs-only --output="subtitles/" --get
```

TODO!

