import re, sys, getopt
import csv
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint

import ../NLPlib

reload(sys)
sys.setdefaultencoding('utf-8')


tagger = NLPlib.NLPlib()


tag = re.compile(r'<[^>]+>')    #to remove HTML tags

def main(argv):

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h', ['help'])
    except getopt.GetoptError:
        print('python twtt.py <input .csv file> <optional argument: group number> <output .twt file>')
        sys.exit(2)

    if len(args) < 2:
        print('usage: python twtt.py <input .csv file> <optional argument: group number> <output .twt file>')
        sys.exit(2)

    if len(args) == 2:
        inputfile = args[0]
        outputfile = args[1]

    if len(args) > 2:
        inputfile = args[0]
        groupnumber = int(args[1])
        outputfile = args[2]
    else:
        groupnumber = -1

    preprocessor(inputfile, outputfile, groupnumber)



def html_strip(data):
    return tag.sub('', data)

#we should cite this, PROF mentioned it on the forum
class MyHTMLParser(HTMLParser):  #to parse HTML codes/entities
    output = ""

    def handle_data(self, data):
        self.output += data

    def handle_entityref(self, name):
        c = unichr(name2codepoint[name])
        self.output += c

    def handle_charref(self, name):
        if name.startswith('x'):
            c = unichr(int(name[1:], 16))
        else:
            c = unichr(int(name))
        self.output += c

    def getoutput(self):
        return self.output

    def clearoutput(self):
        self.output = ""

def endofsentence(splittweet):
    '''
    Input splittweet is a tweet split by spaces. Return an array with end of sentence splits.
    '''
    endofsentencesplitters = ['.', '?', '!'] #';', ':', '-']
    otherpunc = ['(', ')', ',']

    wordlistpath = '/u/cs401/Wordlists/'

    commonnames = ['femaleFirstNames.txt', 'lastNames.txt', 'maleFirstNames.txt']
    namelist = list()

    newsplittweet = list(splittweet)
    offset = 0

    for idx, element in enumerate(splittweet): # ex: hey Jr. boy! What up?
        if idx != len(splittweet) - 1:
            post = splittweet[idx + 1] # 'boy!'
        else: post = None

        sentenceboundaryindex = -1
        multpunc = False, 0

        if len(element) == 1 and element in endofsentencesplitters: break #already its own token

        for idx2, char in enumerate(element): # ex: element = 'Jr.'
            if char in endofsentencesplitters: # Putative sentence boundary
                reg = re.compile('(\?|\.|\!)+')
                if idx2 != len(element) - 1:

                    if re.match(reg, element[idx2 + 1:]):
                        regans = reg.search(element[idx2 + 1:])
                        if regans.span()[1] != len(element[idx2 + 1:]):
                            #there are more words after the mult punc
                            multpunc = (True, regans.span()[1])
                        else:
                            multpunc = (True, 0)

                        sentenceboundaryindex = idx2 #len(element) -
                if idx2 == 0: #before the word
                    regans = reg.search(element)
                    if regans.span():
                        sentenceboundaryindex = regans.span()[1]
                        multpunc = (True, 0)

                if idx2 != len(element) - 1: # if it is not the last character, check for quotations or multiple punctuation
                    if element[idx2 + 1] == '"' or element[idx2 + 1] == '\'':
                        sentenceboundaryindex = idx2 + 1 #need to deal with case ..."

                elif char == '.':
                    sentenceboundaryindex = idx2
                    # disqualify if preceded by known abbreviation of a sort that doesn't normally occur word finally,
                    # but is commonly followed by a capitalized proper name, such as Prof. or vs.
                    with open(wordlistpath + 'pn_abbrev.english', "r") as inputfile:
                        abbrevlist = inputfile.read().splitlines()
                        if element[:idx2] in abbrevlist: #these contain words that are almost never word final
                            sentenceboundaryindex = -1
                    with open(wordlistpath + 'abbrev.english', "r") as inputfile:
                        abbrevlist = inputfile.read().splitlines()
                        if element[:idx2] in abbrevlist: #these contain words that are sometimes word final and sometimes in the middle
                            if post != None:
                                if post[0].islower():
                                    sentenceboundaryindex = -1

                elif char == '?' or char == '!':
                    sentenceboundaryindex = idx2
                    if post != None:
                        for file in commonnames:
                            with open(wordlistpath + file, 'r') as inputfile:
                                temp = inputfile.read().splitlines()
                                [namelist.append(x) for x in temp]

                        if post[0].islower() or post in namelist:
                            sentenceboundaryindex = -1

                if sentenceboundaryindex != -1:
                    newsplittweet[idx+offset] = element[:sentenceboundaryindex]
                    newsplittweet.insert(idx + 1 + offset, element[sentenceboundaryindex:])
                    offset += 1
                    if multpunc[0] and multpunc[1] == 0:
                        break
                    elif multpunc[0] and multpunc[1] > 0:
                        newsplittweet[idx+ offset] = element[sentenceboundaryindex:multpunc[1]+sentenceboundaryindex+1]
                        newsplittweet.insert(idx + 1 + offset, element[multpunc[1]+sentenceboundaryindex+1:])
                        offset+=1
                        break

            elif char in otherpunc:

                #idx2 is the index of char in splittweet
                if idx2 == 0:
                    index = 1
                else:
                    index = idx2

                newsplittweet[idx + offset] = element[:index]
                newsplittweet.insert(idx + 1 + offset, element[index:])
                offset += 1

                reg = re.compile('(\(|\)|,)+')

                if re.search(reg, element[index:]):
                    regans = reg.search(element[index:])
                    if regans.span()[1] == len(element[index:]) and len(element[index:]) != 1:
                        #there are more words after the mult punc
                        newsplittweet[idx + offset] = element[index:index-1+regans.span()[1]]
                        newsplittweet.insert(idx + 1 + offset, element[index-1+regans.span()[1]:])
                        offset += 1
                        break

                break
            elif char == '\'':
                if idx2 - 1 >= 0:
                    if element[idx2-1].islower():
                        if idx2 + 1 < len(element):
                            if element[idx2+1].islower():
                                if element[idx2+1] == 's':
                                    # it is a possessive
                                    newsplittweet[idx + offset] = element[:idx2]
                                    newsplittweet.insert(idx + 1 + offset, element[idx2:])
                                    offset += 1
                                    break
                                else:
                                    #normal clitic
                                    newsplittweet[idx + offset] = element[:idx2-1]
                                    newsplittweet.insert(idx + 1 + offset, element[idx2-1:])
                                    offset += 1
                                    break
                            elif element[idx2-1].lower() == 's':
                                newsplittweet[idx + offset] = element[:idx2]
                                newsplittweet.insert(idx + 1 + offset, element[idx2:])
                                offset += 1
                                break

    return newsplittweet


def preprocessor(filename, outputname, group_id):
    file = open(filename, "rb")
    data = csv.reader(file)
    data = [row for row in data]      #gathering data from input file
    file.close()

    l = 0

    if group_id != -1:
        class0 = (group_id * 5500, (group_id + 1) * 5500 - 1)
        class4 = 800000 + group_id * 5500, 800000 + (group_id + 1) * 5500 - 1
    else:
        class0 = (0, len(data))
        class4 = (0, len(data))

    for line in data:
        if (l >= class0[0] and l <= class0[1]) or (l >= class4[0] and l <= class4[1]):
            polarity = line[0]
            count = 0
            final = ''

            for element in line:
                html_strip(element)
                element = re.sub(r'https?:(.*?)(\s)', '', element, 1) #to remove URLs
                element = re.sub(r'www\.+(.*?)(\s)', '', element, 1)  #to remove URLs
                element = re.sub(r'[*|/|$|%|^|{|}|#|@]', '', element)  #to remove non-punctuation special characters
                element = element.decode('cp1252').encode('utf-8')

                count += 1

                if count == 6:    #the actual tweet is now visited
                    parser = MyHTMLParser()
                    parser.feed(element)
                    parser.clearoutput()   #resetting the parser
                    parser.feed(element)   #why are we doing it twice, Jiana?

                    tweet = element + "\n"
                    tweet_array = tweet.strip().split()  #preparing the tweet for tagging
                    tweet_array = endofsentence(tweet_array)
                    tags = tagger.tag(tweet_array)

                    for tag, i in zip(tags, range(len(tweet_array))):
                        tweet_array[i] += "\\" + tag

                    for tagged_tweet in tweet_array:
                        final += tagged_tweet + " "
                    final += "\n"

            first_line = "<A=" + polarity + ">\n"
            op_file = open(outputname, "a")    #append mode
            op_file.write(first_line)
            op_file.write(final)
            op_file.close()
        l += 1


if __name__ == "__main__":
    main(sys.argv[1:])
