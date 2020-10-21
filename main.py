'''TODO

DO source and dest checking in separate func or in main, not in translate

'''

import praw
import keys
import re
from googletrans import Translator
from langcodes import langcodes
import mistune
import tomd


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
    '&lt;' : '__00__',
    '&amp;' : '__0__'
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
    for i in ('&#x200B;', '&nbsp;', '*'):    
        body = body.replace(i, '')
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
    for k, v in specialChars.items():
        generated_html = generated_html.replace(k, v)
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
            
def getTextFromHTML(htmlText):
    originalText = ''
    for i, c in enumerate(htmlText):
        if c == '>' and htmlText[i-4:i] != 'code':
            try:
                closePos = getClose(htmlText[i:]) + i
                if closePos != i+1:
                    snippet = htmlText[i+1:closePos]
                    originalText += snippet+'\n'
            except TypeError:
                pass
    return originalText
            
def replaceHTMLWithTranslation(html, original, translated):
    orArr = original.split('\n')
    orArr = [i for i in orArr if i != '']
    trArr = translated.split('\n')
    for i in range(len(orArr)):
        html = html.replace(orArr[i], trArr[i])
    for k, v in specialChars.items():
        html = html.replace(v, k)
    return html

def appendInfo(reply):
    reply += reply+'\n'+'^[info](https://www.reddit.com/user/translate-into/comments/jf7k2l/translateinto_usage_information/) ^| ^[github](https://github.com/dwalone/translate-into) ^| ^[feedback](https://www.reddit.com/message/compose/?to=FullRaise)'
    

            
def main():  
    
    for r in praw.models.util.stream_generator(reddit.inbox.mentions, skip_existing=False):
        
        if isinstance(r, praw.models.Comment):
            
            call = r.body            
            post = r.parent()
    
            if isinstance(post, praw.models.Comment):
                body = post.body
                
            else:
                body = '# '+post.title+'\n'+post.selftext
     
            langs = parseCall(call)
            if isinstance(langs, list):
                html = mdToHTML(body)
                originalText = getTextFromHTML(html)
                result = translate(originalText, langs[0], langs[1])
                if isinstance(result, list):
                    html = replaceHTMLWithTranslation(html, originalText, result[0])
                    reply = tomd.Tomd(html).markdown
                    reply = formatTranslation(reply, result[1], result[2])
                elif result == 'error':
                    print("error")
                else:
                    reply = 'Invalid syntax. '+result
            else:
                reply = langs
                
            print(reply)
            
    
    


if __name__ == '__main__':
    main()       
    
