import praw
import keys
import re
from googletrans import Translator
from langcodes import langcodes
import mistune


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


reddit = praw.Reddit(client_id = keys.client_id,
                     client_secret = keys.client_secret,
                     user_agent = keys.user_agent,
                     username = keys.username,
                     password = keys.password)

translator = Translator()

def clearInbox():
    unread_messages = []
    for item in reddit.inbox.unread(limit=None):
        if isinstance(item, praw.models.Message):
            unread_messages.append(item)
    reddit.inbox.mark_read(unread_messages) 
    
def mdToHTML(body):
    md_doc = open('input.md', 'w')
    md_doc.write(body)
    md_doc.close()
    
    html_doc = open('converted.html', "w", encoding="utf-8")
    generated_html = (
        "<!DOCTYPE html>"
        + "<html><head></head><body>"
    )
    
    with open('input.md', encoding="utf-8") as f:
        content = f.readlines()
        for line in content:
            generated_html += mistune.markdown(line)
    
    generated_html += "</body></html>"
    generated_html = generated_html.replace('\n', '')
    html_doc.write(generated_html)
    html_doc.close()   
    
def getClose(s):
    openBr = 0
    for pos, char in enumerate(s):
        if char == '>':
            openBr += 1
        elif char == '<':
            openBr -= 1
        if openBr == 0:
            return pos
            break

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
    
def parseCall(text):
    tarr = text.lower().split()
    if tarr[0] in ('u/translate-into', '/u/translate-into'):
        
        if len(tarr) == 1:            
            return [None, 'en']
        
        elif len(tarr) == 2:            
            return [None, tarr[1]]
        
        elif len(tarr) == 4:            
            if tarr[2] == 'from':                
                return [tarr[3], tarr[1]]
            
        else:
            return 'Invalid syntax. Check my pinned post for usage!'
        
    else:
        return 'Invalid syntax. Check my pinned post for usage!'
    
def formatTranslation(text, source, destination):
    reply = text+'\n\n'+source+' -> '+destination
    return reply
            
def formatText(text):
    characters_to_remove = "*`"
    pattern = "[" + characters_to_remove + "]"
    text = re.sub(pattern, "", text)
    replaceSpecial = {}
    tarr = text.split()
    for i,s in enumerate(tarr):
        key = '__'+str(i)+'__'
        
        if s.startswith(('r/', '/r/', 'u/', '/u/')):
            tarr[i] = key
            replaceSpecial[key] = s
            
def main():    
    
    '''
    for r in praw.models.util.stream_generator(reddit.inbox.unread):
        body = r.parent().body 
    '''
    
    
    body = '''
Hello, enter text here to see what your reddit post will look like.

Here's an example of some reddit formatting tricks:
Bold, italic, code, [link](http://redditpreview.com), strikethrough

hjhjbjbh /r/pics hjgjhbhj ><

dsds[dsds](https://youtube.com)

&nbsp;

>Quote
>>Nested quote

[ffefw]
    '''
    
    mdToHTML(body)


if __name__ == '__main__':
    main()         
