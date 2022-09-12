from django import template
from django.utils import timezone, dateformat
from datetime import datetime, timedelta
from forum import models as forum_models
from pytz import timezone as timezonePYTZ

register = template.Library()

# Template Filters #
@register.filter
def splitContent(content):
    return content.split('\n')
    
@register.filter
def splitLine(line):

    wordList = []
    currentString = ''
    tagStartedCheck = False
    for i, currentWord in enumerate(line.split(' ')):
        #print('CURRENTWORD:'+currentWord)
        word = currentWord.rstrip()
        while word != '':
            startTag = containsStartTag(word)
            endTag = containsEndTag(word)
            #print('WORD:'+word)
            
            if startTag and endTag == False:
                if len(currentString) > 0 : currentString = currentString + ' '
                currentString = currentString + word
                tagStartedCheck = True
                word = ''
                #print('1')
            elif tagStartedCheck and endTag == False and i != len(line.split(' ')) - 1:
                if len(currentString) > 0 : currentString = currentString + ' '
                currentString = currentString + word
                word = ''
                #print('2')
            elif endTag:
                #print('ENDTAG:'+endTag)
                if len(currentString) > 0 : currentString = currentString + ' '
                currentString = currentString + word[0:word.index(endTag)+len(endTag)]
                wordList.append(currentString)
                currentString = ''
                if endTag in word : word = word[word.index(endTag)+len(endTag)::]
                else : word = ''
                tagStartedCheck = False
                #print('3')
            else:
                if len(currentString) > 0 : currentString = currentString + ' '
                currentString = currentString + word
                word = ''
                if i == len(line.split(' ')) - 1:
                    wordList.append(currentString)
                #print('4')
                
    #print(wordList)
    return wordList
    
@register.filter
def containsAttribute(value, targetAttribute):
    attributeString = targetAttribute + '='
    #print("A:"+attributeString)
    #print("V:"+value)
    
    if attributeString in value:
        startLoc = value.index(attributeString) + len(attributeString)
        if len(value.split(' ')) == 1 or ']' in value[startLoc::].split(' ')[0]:
            if len(value.split(' ')) > 1 and ']' not in value[startLoc::].split(' ')[0]: targetChar = ' '
            else : targetChar = ']'
            endLoc = value[value.index(attributeString)::].index(targetChar) + value.index(attributeString)
            #print("1" + targetChar)
        else:
            if len(value.split(' ')) > 1 and ']' in value[startLoc::].split(' ')[0] : targetChar = ']'
            else : targetChar = ' '
            endLoc = startLoc + len(value[startLoc::].split(targetChar)[0])
            #print("2" + targetChar)
        extractedAttribute = value[startLoc:endLoc]
        if extractedAttribute[-1] == ']':
            extractedAttribute = extractedAttribute[0:-1]
        
        # Attribute Mods #
        if targetAttribute == 'color' and len(extractedAttribute) > 0 and extractedAttribute[0] != '#':
            extractedAttribute = '#' + extractedAttribute
        elif targetAttribute == 'size' and len(extractedAttribute) > 0:
            if extractedAttribute.lower() == 'medium' : return 'large'
            elif extractedAttribute.lower() == 'large' : return 'x-large'
            return 'small'
        elif targetAttribute == 'pinterest' and 'pinterest.com/pin/' in extractedAttribute:
            extractedAttribute = 'https://assets.pinterest.com/ext/embed.html?id=' + extractedAttribute[extractedAttribute.rfind('pinterest.com/pin/')+18:-1]
        elif targetAttribute == 'youtube' and 'youtube.com/watch?v=' in extractedAttribute:
            extractedAttribute = 'https://www.youtube.com/embed/' + extractedAttribute[extractedAttribute.rfind('youtube.com/watch?v=')+20::]
        elif targetAttribute == 'vimeo' and 'vimeo.com' in extractedAttribute:
            extractedAttribute = 'https://player.vimeo.com/video/' + extractedAttribute[extractedAttribute.rfind('vimeo.com/')+10::]
        elif targetAttribute == 'twitter' and 'twitter.com/' in extractedAttribute:
            extractedAttribute = 'https://twitter.com/' + extractedAttribute[extractedAttribute.rfind('twitter.com/')+12::]
         
        #print('-'+extractedAttribute+'-')
        return extractedAttribute
        
    return '#'
    
@register.filter
def containsContent(value):
    for tag in getTagList():
    
        # Start Tag #
        if tag in value and '=' in tag:
            startLoc = value.index(tag)
            #print("V:"+str(value))
            endLoc = value[value.index(tag)::].index(']') + value.index(tag) + 1
            targetString = value[startLoc:endLoc]
            value = value.replace(targetString, '')
        else:
            value = value.replace(tag, '')
            
        # End Tag #
        endTagString = '[/' + tag[1:-1] + ']'
        if endTagString in value:
            value = value.replace(endTagString, '')
        
    return value
    
@register.filter
def multiply(value1, value2):
    return value1 * value2

@register.filter
def divide(value1, value2):
    value1 = int(value1)
    value2 = int(value2)
    if value2 == 0:
        return 0

    return int(value1 / value2)
    
@register.filter
def toString(value):
    return str(value)

@register.filter
def getLastAuthor(value):
    return value[len(value)-1].author

@register.filter
def makePageNumList(value):
    numList = ''
    
    for i in range(int(value)):
        if i == 4 and int(value) > 4:
            numList = numList + '.' + str(value - 1)
            break
        else:
            numList = numList + str(i)
    
    return numList
    
@register.filter
def quoteDateFilter(value):
    if len(value) >= 14 and value.isnumeric():
        dateYear = value[0:4]
        dateMonth = value[4:6]
        dateDay = value[6:8]
        timeHour = value[8:10]
        timeMinute = value[10:12]
        timeSeconds = value[12:14]
        strDate = dateYear + '-' + dateMonth + '-' + dateDay
        strTime = timeHour + ':' + timeMinute
        strSuffix = 'AM'
        if strTime[0:2].isnumeric() and int(strTime[0:2]) > 12:
            strTime = str(int(strTime[0:2]) - 12) + strTime[2::]
            strSuffix = 'PM'
        if strTime[0] == '0':
            strTime = strTime[1::]
        quoteDate = datetime.fromisoformat(dateYear + '-' + dateMonth + '-' + dateDay + 'T' + timeHour + ':' + timeMinute + ':' + timeSeconds)
        
        if datetime.today().date() == quoteDate.date():
            return 'Today at ' + strTime + ' ' + strSuffix
        elif (datetime.today() - timedelta(days=1)).date() == quoteDate.date():
            return 'Yesterday at ' + strTime + ' ' + strSuffix
        else:
            return 'On ' + strDate + ' at ' + strTime + ' ' + strSuffix
            
    return value
    
@register.filter
def dateString(targetDate, targetType):
    strDate = str(dateformat.format(targetDate.astimezone(timezonePYTZ('US/Eastern')), 'm/d/Y'))
    strTime = str(targetDate.astimezone(timezonePYTZ('US/Eastern'))).split(' ')[1][0:5]
    strSuffix = 'AM'
    if strTime[0:2].isnumeric() and int(strTime[0:2]) > 12:
        strTime = str(int(strTime[0:2]) - 12) + strTime[2::]
        strSuffix = 'PM'
    if strTime[0] == '0':
        strTime = strTime[1::]
        
    if targetType == 'Time':
        return strTime + ' ' + strSuffix
    elif targetType == 'Date':
        return strDate
    elif targetType == 'Live Date':
        if datetime.today().date() == targetDate.astimezone(timezonePYTZ('US/Eastern')).date():
            return 'Today'
        elif (datetime.today() - timedelta(days=1)).date() == targetDate.astimezone(timezonePYTZ('US/Eastern')).date():
            return 'Yesterday'
        else:
            return strDate
    else:
        return ''

@register.filter
def getSubforum(targetTitleURL, targetAttribute):
    targetSubforum = forum_models.Subforum.objects.filter(titleURL=targetTitleURL).first()
    
    if targetAttribute == 'title':
        return targetSubforum.title
    elif targetAttribute == 'description':
        return targetSubforum.description
    elif targetAttribute == 'imageURL':
        return targetSubforum.image.url
    elif targetAttribute == 'threadCount':
        return targetSubforum.threadCount()
    
    return targetSubforum

@register.filter
def trimString(targetString, maxLength):
    if len(targetString) > int(maxLength):
        targetString = targetString[0:int(maxLength)] + '...'
    return targetString

@register.filter
def daysSince(targetDate):
    return str(((timezone.now() - targetDate).days) - 1)

# Functions #
def getTagList():
    return ['[b]', '[u]', '[i]', '[color=', '[size=', '[link=', '[image=', '[youtube=', '[quote=']
    
def containsStartTag(value):
    for tag in getTagList():
        if tag in value:
            return True
    return False

def containsEndTag(value):
    for tag in getTagList():
        tag = '[/' + tag[1::] 
        if tag[-1] == '=':
            tag = tag[0:-1] + ']'
            
        if tag in value:
            return tag
        elif tag == '[/link]' and '[/link]' in value:
            return '[/link]'
        elif tag == '[/image]' and (('[image=' in value and ']' in value[value.index('[image=')::])
                                  or '[image=' not in value and len(value) > 0 and value[-1] == ']'):
            return ']'
    return False
    