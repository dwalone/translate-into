'''TODO

DO source and dest checking in separate func or in main, not in translate

'''

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

specialChars = {
    '&gt;' : '__000__',
    '&lt;' : '__00__'
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
    return generated_html
    
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
        return str(e)
    
    except:
        return 'error'
    
def parseCall(text):
    tarr = text.lower().split()
    if tarr[0] in ('u/translate-into', '/u/translate-into'):
        
        if len(tarr) == 1:            
            return None, 'en'
        
        elif len(tarr) == 2:            
            return None, tarr[1]
        
        elif len(tarr) == 4:            
            if tarr[2] == 'from':                
                return tarr[3], tarr[1]
            
        else:
            return 'Invalid syntax. Check my pinned post for usage!'
        
    else:
        return 'Invalid syntax. Check my pinned post for usage!'
    
def formatTranslation(text, source, destination):
    reply = text+'\n\n'+source+' -> '+destination
    return reply
            
def getTextFromHTML(htmlText):
    originalText = ''
    for k, v in specialChars.items():
        htmlText = htmlText.replace(k, v)
    htmlText = htmlText.replace('&nbsp;', '')
    for i, c in enumerate(htmlText):
        if c == '>':
            try:
                closePos = getClose(htmlText[i:]) + i
                if closePos != i+1:
                    snippet = htmlText[i+1:closePos]
                    originalText += snippet+'\n'
            except TypeError as e:
                print(e)
    return originalText
            
def replaceHTMLWithTranslation(html, original, translated):
    orArr = original.split('\n')
    trArr = translated.split('\n')
    for i in range(len(orArr)):
        html = html.replace(orArr[i], trArr[i])
    for k, v in specialChars.item():
        html = html.replace(v, k)
    return html
    

            
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
    
    
    comment = 'u/translate-into german'
    src, dest = parseCall(comment)
    print(src,dest)
    html = mdToHTML(body)
    print(html)
    originalText = getTextFromHTML(html)
    print(originalText)
    result = translate(originalText, src, dest)
    if isinstance(result, list):
        html = replaceHTMLWithTranslation(html, originalText, result[0])
        reply = formatTranslation(html, result[1], result[2])
        print(reply)
    elif result == 'error':
        print("error")
        #break
    else:
        print('Invalid syntax. '+result)
    
    


if __name__ == '__main__':
    main()       
    
    
text = '''
Hello, enter text here to see what your reddit post will look like.
Here's an example of some reddit formatting tricks:
Bold, italic, code, 
link
, strikethrough
hjhjbjbh /r/pics hjgjhbhj __000____00__
dsds
dsds
Quote
Nested quote
[ffefw]'''
translator.translate(text, dest='german').text