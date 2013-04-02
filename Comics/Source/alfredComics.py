import alp
import json
import time
import pickle
import webbrowser
import os
import string
import sys

from datetime import datetime, timedelta
from previewsScraper import getComics

def get_comics(query=None):

    comicData = 'savedata/comicData'
    pageData = 'savedata/pageData'

    try:
        # Open pickled file for reading
        entries = getData(comicData)
        # Check for second "screen"
        if query in entries.keys():
            # Get which page we came from
            page = getData(pageData)

            feedback = []
            item = alp.Item(title='Go Back', subtitle='...', valid=False, icon=get_icon('BACK'), autocomplete=page)
            feedback.append(item)
            books = entries[query]
            for book in books:
                url = book['link']
                subtitle = '%s - %s - %s - %s' % (book['price'], query, book['id'], time.strftime("%-m/%d/%Y", book['date']))
                natural = '%s on %s' % (book['title'], time.strftime("%-m/%d/%Y", book['date']))
                argument = json_args({"command":"link", "url":url, 'natural':natural})
                item = alp.Item(title = book['title'],
                                subtitle = subtitle,
                                valid = True,
                                icon = get_icon(query),
                                arg = argument
                                )
                feedback.append(item)

            return alp.feedback(feedback)

        if query == 'this' or query == 'next':
            t = 'inside loop %s' % query
            alp.log(t)
            # Check cache and delete if too old
            checkCache()

            # Set the correct url based on query
            if query == 'this':
                url = "http://www.previewsworld.com/Home/1/1/71/952" # New Releases
            else:
                url = "http://www.previewsworld.com/Home/1/1/71/954" # Upcoming Releases

            # Get the comics dictionary
            entries = getComics(url)

            # Save the entries for next script
            f = open(comicData, 'w')
            pickle.dump(entries, f)
            f.close()

            # Save so we can navigate between pages
            f = open(pageData,'w')
            pickle.dump(query,f)
            f.close()

            # Build the feedback Array
            feedback = []
            keys = entries.keys()
            
            # Build the Date item
            firstkey = keys[0]
            date = entries[firstkey][0]['date']
            title = 'Comics for %s' % time.strftime("%-m/%-d/%Y", date)
            if query == 'this':
                auto = 'next'
            else:
                auto = 'this'
            item = alp.Item(title = title, valid = False, icon = get_icon('CALENDAR') , autocomplete = auto)
            feedback.append(item)
            for key in entries.keys():
                # Create the subtitle
                sub = 'Show Comics for %s' % string.capwords(key)
                # Build the Alfred item
                item = alp.Item(title = string.capwords(key),
                                subtitle = sub,
                                uid = key,
                                valid = False,
                                autocomplete = string.capwords(key),
                                icon = get_icon(key)
                                )
                # Put item in feedback array
                feedback.append(item)

        else:
            feedback = []
            item = alp.Item(title='This weeks comics?', valid=False, autocomplete='this', icon=get_icon('FORWARD'))
            feedback.append(item)
            item = alp.Item(title='Next weeks comics?', valid=False, autocomplete='this', icon=get_icon('FORWARD'))
            feedback.append(item)
            return alp.feedback(feedback)

    except IOError:
        f = open(comicData, 'w')
        pickle.dump({'reload':'data'}, f)
        f.close()

        f = open(pageData, 'w')
        pickle.dump('this', f)
        f.close()

    except:
        for error in sys.exc_info():
            log = 'Unexpected Error: %s' % error
            alp.log(log)

        # Build the Alfred item
        item = alp.Item(title = 'Something went wrong...',
                        subtitle = 'Check the logs',
                        uid = 'Error',
                        valid = False,
                        autocomplete = None,
                        icon = None
                        )
        feedback = [item]

    # Generate feedback and send to Alfred
    return alp.feedback(feedback)


def getData(filename):
    f = open(filename, 'r')
    entries = pickle.load(f)
    f.close()
    return entries

# Delete cache after time expires or when flag is set to True
def checkCache(delete=False):
    filepath = alp.cache()
    f = '%s_requests_cache.sqlite' % alp.bundle()
    fullpath = os.path.join(filepath,f)
    if os.path.exists(fullpath):
        if ((datetime.now() - datetime.fromtimestamp(os.path.getmtime(fullpath))) > timedelta(hours=6)) or delete:
            try:
                os.remove(fullpath)
                alp.log('Successfully removed requests cache')
            except:
                alp.log('Problem: Could not remove requests cache')
    return

# Return the correct icon based on the key
def get_icon(key='DEFAULT'):
    key = key.upper()
    icon = None

    # Comic Publishers
    if key == "IMAGE COMICS":
        icon = 'icons/image.jpeg'
    elif key == "MARVEL COMICS":
        icon = 'icons/marvel.gif'
    elif key == "IDW PUBLISHING":
        icon = 'icons/idw.jpeg'
    elif key == "DARK HORSE COMICS":
        icon = 'icons/darkhorse.jpeg'
    elif key == "DC COMICS":
        icon = 'icons/dc.jpeg'

    # Navigation Icons
    elif key == 'BACK':
        icon = 'icons/back.png'
    elif key == 'FORWARD':
        icon = 'icons/forward.png'
    elif key == 'CALENDAR':
        icon = 'icons/calendar.png'

    # Default Icon
    elif key == 'DEFAULT':
        icon = 'icons/default.png'
    else:
        icon = 'icons/default.png'

    return icon

# Creates single quoted JSON arguments from a list.
# Single quotes are used instead of double quotes because for some reason
# it doesn't work with double quotes through Alfred.
def json_args(args):
  return json.dumps(args).replace("\"", "'")

# Perform actions based off of json arguments
def action(query):
    args = json.loads(query.replace("'", "\""))
    if args is None or len(args) == 0:
        return
    elif args['command'] == 'link':
        webbrowser.open(args['url'])

# Send comic book to Fantastical
def fantastical(query):
    args = json.loads(query.replace("'", "\""))
    if args is None or len(args) == 0:
        return
    cmd = """osascript -l AppleScript -e 'tell application "Fantastical"' -e 'parse sentence "%s /c"' -e 'end tell'""" % args['natural']
    os.system(cmd)

if __name__ == "__main__":
    get_comics('next')
