import re
import urllib.request
import string
import praw
import config
import time
from googlesearch import search 
from bs4 import BeautifulSoup

def bot_login():
    
    r = praw.Reddit(*RedditInfo*)
    return r

def CommentParse(Comment):

    Season = ''
    SeasonNum = ''

    Name = Comment[Comment.find('[[')+2:Comment.rfind(']]')]

    Comment = Comment.replace('[[' + Name + ']]', '')

    Comment = Comment.split()

    for Word in Comment:
        if Word.__contains__(Name):
            Comment.remove(Word)
            break

    if Comment is None:
        print(Name)
        print(Season)
        print(SeasonNum)
        return Name, Season, SeasonNum

    for Word in Comment:
        if Word.__contains__('LTP' or 'ltp'):
            Season = Word
            break

    if Season == 'nLTP' or 'mLTP' or 'oLTP' or 'eLTP':
        
        Season = Season
        
    else:
        
        Season = Season.upper()
    
    for Word in Comment:
        if any(char.isdigit() for char in Word):
            SeasonNum = Word
            break

    SeasonNum = SeasonNum.strip('S')
    SeasonNum = SeasonNum.strip('s')

    return Name, Season, SeasonNum

    

def VerifyTPL(Name):

    Marker = True

    # Marker = did I find a valid URL for this name??

    SplitName = Name.split()
    SpacedName = ('%20').join(SplitName)

    URL = 'https://www.tagproleague.com/Player/' + SpacedName

    # Lets try the ol direct reference

    page = urllib.request.urlopen(URL)
    soup = BeautifulSoup(page, "html.parser")

    verify = soup.find('div', attrs={'style': 'background:#222;display:flex;'})
    verify = verify.text.strip()
    
    if verify.__contains__('No records matching your query were found.'):

        # Direct reference didn't work, lets try googling

        query = Name + ' TagProLeague'
        print(query)
        
        for j in search(query, num=2, stop=1, pause=2):
            
            Marker = False
            
            if j.__contains__("https://www.tagproleague.com/Player/"):

                URL = j
                print(URL)

                # Empty Page Check

                page = urllib.request.urlopen(URL)
                soup = BeautifulSoup(page, "html.parser")

                verify = soup.find('div', attrs={'style': 'background:#222;display:flex;'})
                verify = verify.text.strip()

                if verify.__contains__('No records matching your query were found.'):
                    break

                Marker = True

                # We found a player page on google

                break

        # Google didn't work either, I'm out of ideas, pass the error message

    return URL, Marker

# input URL (string), Seasons (string list form of xLTP Sx)

def ScrapeTPL(URL, Season):

    Marker = False
    Content = ''
    
    page = urllib.request.urlopen(URL)
    soup = BeautifulSoup(page, "html.parser")

    Name = soup.find('h1', attrs={'style': 'text-align:center;'})
    Name = Name.text.strip()

    row = soup.findAll('div', 'statcardrow')

    if Season == '':
        try:
            Content = row[0].text.strip()
        except:
            return Marker, Content
        Content = Content.split('\n')
        Content = list(filter(None, Content))
        Marker = True #no seasons on page
        
        
    else:
        for seas in row:
            seas = seas.text.strip()
            if seas.__contains__(Season) == True:
                Content = seas.split('\n')
                Content = list(filter(None, Content))
                Marker = True
                break
        

    return Marker, Content, Name

def RedditFormat(Name, Content):

    Difference = float(Content[4]) - float(Content[5])
    
    if abs(Difference) < 1:
        Position = 'Both'
    else:
        if Difference > 0:
            Position = 'O'
        else:
            Position = 'D'

    Ranks = [Content[21].strip('Caps'), Content[22].strip('Hold'), Content[23].strip('Returns'), Content[24].strip('Prevent')]

    i = 0
    for Rank in Ranks:
        if Rank == '-':
            Ranks[i] = ''
        else:
            Ranks[i] = ' (#' + Rank + ')'
        i += 1
    

    Team = Content[7]

    Output = '#**' + Name + '**\n\nSeason: ' + Content[0] + '\n\nPosition: ' + Position + '\n\nTeam: ' + Team
    Output += '\n\n&nbsp;\n\n' + 'Minutes | Captures | Hold | Returns | Prevent | +/- '
    Output += '\n:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:\n'


    Values = [Content[1], Content[2] + Ranks[0], Content[15] + Ranks[1], Content[3] + Ranks[2],
              Content[16] + Ranks[3], Content[14]]
        
    Values = ('|').join(Values)

    Output2 = '\n\n' + 'OGASP | DGASP | TGASP' + '\n:----:|:----:|:----:\n'

    Output3 = '\n\n' + 'ONISH | DNISH | TNISH' + '\n:----:|:----:|:----:\n'

    Values2 = [Content[4], Content[5], Content[6]]

    Values2 = ('|').join(Values2)

    Values3 = [Content[17], Content[18], Content[19]]
    
    Values3 = ('|').join(Values3)

    Comment = Output + Values + Output2 + Values2 + Output3 + Values3

    return Comment


def Info(InputName, Season, SeasonNum):

    URL, Marker = VerifyTPL(InputName)

    if Marker == False:

        Comment = InputName + " not found in TagPro League"

        return Comment

    if Season != '':

        Season = Season + ' S' + str(SeasonNum)
        

    Marker, Content, Name = ScrapeTPL(URL, Season)

    if Marker == False:
        
        if Season == '':
            
            Comment = "Stats not found for " + Name

        else:

            Comment = Season + " stats not found for " + Name
        
    else:
        
        Comment = RedditFormat(Name, Content)

        
    return Comment


##Name, Season, SeasonNum = CommentParse()

r = bot_login()


subreddit = r.subreddit('RutgersTP+nltp+mltp+tagpro')

for Comment in subreddit.stream.comments():
    if Comment.body.__contains__('[[' and ']]'):

        RepliedStatus = False
        
        try:

            Comment.refresh()
            for Reply in Comment.replies:
                if Reply.author == 'BaayBot':
                    RepliedStatus = True
                    break

            if RepliedStatus == True:
                continue
            
            InputName, Season, SeasonNum = CommentParse(Comment.body)

            try:
                Output = Info(InputName, Season, SeasonNum)
                Comment.reply(Output)

            except:
                print("whoops2")

        except:
            print("whoops")

        
        


