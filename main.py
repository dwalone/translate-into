import praw
import keys
from googletrans import Translator
from langcodes import langcodes

langExceptions = {
    'chinese' : 'zh-cn',
    'haitian' : 'ht',
    'kurdish' : 'ku',
    'kurmanji' : 'ku',
    'myanmar' : 'my',
    'burmese' : 'my',
    'scots' : 'gd',
    'gaelic' : 'gd',
    }

translator = Translator()

def translate(text, source, destination):
    
    source = langExceptions[source] if source in langExceptions.keys() else source
    destination = langExceptions[destination] if destination in langExceptions.keys() else destination
    
    try:
        if source is None:
            translation = translator.translate(text, dest=destination)
        else:
            translation = translator.translate(text, src=source, dest=destination)
            
        return [translation.text, langcodes[translation.src], langcodes[translation.dest]]
    
    except ValueError as e:
        return e
    
    except:
        return 'error'



'''

reddit = praw.Reddit(client_id = keys.client_id,
                     client_secret = keys.client_secret,
                     user_agent = keys.user_agent,
                     username = keys.username,
                     password = keys.password)

unread_messages = []
for item in reddit.inbox.unread(limit=None):
    if isinstance(item, praw.models.Message):
        unread_messages.append(item)
reddit.inbox.mark_read(unread_messages)

for r in praw.models.util.stream_generator(reddit.inbox.unread):
    print(r)
    
    '''