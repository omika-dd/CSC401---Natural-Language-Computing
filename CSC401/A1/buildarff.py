from __future__ import print_function
from collections import OrderedDict
import sys, getopt, re

def main(argv):

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h', ['help'])
    except getopt.GetoptError:
        print('buildarff.py <inputfile:.twt file> <outputfile:.arff file> <optional argument: maxtweets>')
        sys.exit(2)

    if len(args) < 2:
        print('usage: buildarff.py <inputfile:.twt file> <outputfile:.arff file> <optional argument: maxtweets>')
        sys.exit(2)

    inputfile = args[0]
    outputfile = args[1]

    if len(args) > 2:
        maxtweets = args[2]
    else:
        maxtweets = -1

    # assemble feature counts per tweet in multiple dictionaries
    featurecounts = countfeatures(separateinput(inputfile, int(maxtweets)))

    # assemble output string for arff file
    out = assembleoutput(inputfile, featurecounts)

    # print to output file
    printtooutput(out, outputfile)

def separateinput(inputfile, maxtweets):
    '''Take inputfile and separate tweets with their class and return list of tweets with their class'''

    with open(inputfile, "r") as inputf:
        inputlist = re.split("<A=(0|2|4){1}>", inputf.read())[1:]

    tweetlist = list()

    for c, t in zip(inputlist[0::2], inputlist[1::2]):
         tweetlist.append(list((c, t)))

    if maxtweets != -1 and maxtweets <= len(tweetlist):
        tweetlist = tweetlist[:maxtweets]

    return tweetlist

def tokenize(tweet, delimeter = ' '):
    '''Split tweet by spaces and return list of tokens (made up of pos tags with phrase)'''
    return tweet.split(delimeter)

def returnfeature(tag, word = '', relevanttokenlist = []):
    '''
    Return feature name associated with tag, word (optional), and relevanttokenlist (optional).
    In case that tag directly corresponds/categorizes to feature, return tag.
    If no feature name associated with tag, return tag.
    '''

    wordlistpath = '/u/cs401/Wordlists/'

    specialtags = ['CD', 'DT', 'EX', 'FW', 'NN', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'PDT',
                   'POS', 'PRP', 'PRP$', 'RP', 'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBG',
                   'VBN', 'VBP', 'VBZ', '#', '$', '.', ':', '"', '\'']
    dashes = ['SYM', 'UH', 'JJ', 'VBN', 'NN', ':'] #could be in SYM, UH, JJ, VBN, NN, : (in training data)
    slang = ['FW', 'NN']
    future = ['VB', 'VBG']
    pronouns = ['PRP', 'PRP$']
    pronoundict = {'First-person': 'fpp',
                   'Second-person': 'spp',
                   'Third-person': 'tpp'}

    if relevanttokenlist:
        if tag in future:
            separatedtokenlist = [separatetoken(t) for t in relevanttokenlist] #[('guys', 'NNS'), ('see', 'VB'), ('this', 'NN')]
            # CASE 1: \VB \VBG \VB -- VB ON EITHER SIDE OF VBG
            # CASE 2: \TO \VB (sometimes incorrectly tagged as \NN)
            # CASE 3: \MD \VB or \MD \PRP \VB (sometimes incorrectly tagged as \NN)
            if any((['VB', 'VBG'] == [separatedtokenlist[i][1], separatedtokenlist[i + 1][1]]) for i in range(len(separatedtokenlist) - 1)) \
                    or any((['VBG', 'VB'] == [separatedtokenlist[i][1], separatedtokenlist[i + 1][1]]) for i in range(len(separatedtokenlist) - 1)) \
                    or any((['TO', 'VB'] == [separatedtokenlist[i][1], separatedtokenlist[i + 1][1]]) for i in range(len(separatedtokenlist) - 1)) \
                    or any((['MD', 'VB'] == [separatedtokenlist[i][1], separatedtokenlist[i + 1][1]]) for i in range(len(separatedtokenlist) - 1)) \
                    or any((['MD', 'PRP', 'VB'] == [separatedtokenlist[i][1], separatedtokenlist[i + 1][1], separatedtokenlist[i + 2][1]]) for i in range(len(separatedtokenlist) - 2)):
                tag = 'ftv'

    if tag in specialtags: # special tags are tags that don't directly correspond to a feature
        if tag in pronouns:
            for file in pronoundict.keys():
                with open(wordlistpath + file, "r") as inputfile:
                    wordlist = inputfile.read().splitlines()
                    if word.lower() in (w.lower() for w in wordlist):
                        tag = pronoundict[file]
                        break

        elif tag == ":": #Could be colon, semi-colon, ellipsis, or DASH
            if word == "...":
                tag = 'ellipses'
            elif word == '-':
                tag = 'dashes'
            else: # ':' or ';'
                tag = 'colons'

        elif tag in slang:
            with open(wordlistpath + "Slang", "r") as inputfile:
                wordlist = inputfile.read().splitlines()
                if word.lower() in (w.lower() for w in wordlist):
                    tag = 'slang'

        elif tag == '.':
            tag = 'sc'

        elif tag in dashes:
            if word.count('-') > 1:
                # special case: count for a feature within a token
                tag = 'special-dashes'
            elif word.count('-') == 1:
                tag = 'dashes'

    return tag


def classify(word, postag, relevanttokenlist = []):
    '''
    Return feature name (the dictionary keys indicated in countfeatures) associated with
    postag, word, and relevanttokenlist (optional).
    '''

    # MODULARITY: ADD HERE FOR NEW POSTAG CORRESPONDING TO CERTAIN FEATURE.
    # IF SPECIAL, SEND postag + word AS PARAMETER TO returnfeature
    # IF DIRECTLY CORRESPONDS TO FEATURE, SEND feature (indicated in dictionary keys in countfeatures() to returnfeature
    options = {'CC': returnfeature('cc'),
               #'CD': returnfeature('NA'),
               #'DT': returnfeature('NA'),
               #'EX': returnfeature('NA'),
               'FW': returnfeature('FW', word),
               #'IN': returnfeature('NA'),
               #'JJ': returnfeature('NA'),
               #'JJR': returnfeature('NA'),
               #'JJS': returnfeature('NA'),
               #'LS': returnfeature('NA'),
               #'MD': returnfeature('NA'),
               'NN': returnfeature('NN', word),
               #'NNS': returnfeature('NA'),
               #'NNP': returnfeature('NA'),
               #'NNPS': returnfeature('NA'),
               #'PDT': returnfeature('NA'),
               #'POS': returnfeature('NA'),
               'PRP': returnfeature('PRP', word),
               'PRP$': returnfeature('PRP$', word),
               'RB': returnfeature('adverbs'),
               'RBR': returnfeature('adverbs'),
               'RBS': returnfeature('adverbs'),
               #'RP': returnfeature('NA'),
               'SYM': returnfeature('SYM', word),
               #'TO': returnfeature('NA'),
               'UH': returnfeature('UH', word),
               'VB': returnfeature('VB', word, relevanttokenlist),
               'VBD': returnfeature('ptv'),
               'VBG': returnfeature('VBG', word, relevanttokenlist),
               'VBN': returnfeature('ptv'),
               #'VBP': returnfeature('NA'),
               #'VBZ': returnfeature('NA'),
               'WDT': returnfeature('whwords'),
               'WP': returnfeature('whwords'),
               'WP$': returnfeature('whwords'),
               'WRB': returnfeature('whwords'),
               #'#': returnfeature('NA'),
               #'$': returnfeature('NA'),
               '.': returnfeature('.', word),
               ',': returnfeature('commas'),
               ':': returnfeature(':', word),
               '(': returnfeature('parentheses'),
               ')': returnfeature('parentheses')
               #'"': returnfeature('NA'),
               #'\'': returnfeature('NA')
               # unsure about left and right quotes
               }

    if postag not in options.keys():
        return 'NA'

    return options[postag]

def separatetoken(token):
    '''
    Separate token composed of word and postag. Return tuple (word, postag).

    >>> separatetoken('head\NN')
    ('head', 'NN')
    '''

    index = token.rfind("\\")

    word = token[:index]             #hello
    postag = token[index + 1:]       #\\NN

    return word, postag

def countfeatures(tweetlist):
    '''
    Return list of dictionaries for each tweet. Each dictionary is composed of a feature count
    for each individual tweet.
    '''

    featurecount = list()

    for classtweet in tweetlist:
        #MODULARITY: ADD FEATURE TO THIS LIST
        dict = {'fpp': 0, 'spp': 0, 'tpp': 0, 'cc': 0, 'ptv': 0, 'ftv': 0, 'commas': 0, 'colons': 0,
                'dashes': 0, 'parentheses': 0, 'ellipses': 0, 'cn': 0, 'pn': 0, 'adverbs': 0,
                'whwords': 0, 'slang': 0, 'ucw': 0, 'asl': 0, 'atl': 0, 'sc': 0, 'class': 0}

        # set the class feature
        tweetclass = classtweet[0]
        dict['class'] = int(tweetclass)

        tweet = classtweet[1]
        tokenizedtweet = tokenize(tweet)

        tokenizedtweet = [t.strip('\n') for t in tokenizedtweet] #assumes a '\n' doesn't exist in the tweet

        for idx, token in enumerate(tokenizedtweet):

            word, postag = separatetoken(token)

            # check for upper case words that are > 1 characters
            if word.isupper() and len(word) > 1:
                dict['ucw'] += 1

            if postag in ['VBG', 'VB']: # special case: check if in future tense
                subsets = [(idx - 2, idx + 1), (idx - 1, idx + 1), (idx - 1, idx), (idx, idx + 1)]
                for ss in subsets:
                    if tokenizedtweet[ss[0]:ss[1]]:
                        # ideally takes 2 tokens before it, the token itself, and the token after it
                        feat = classify(word, postag, tokenizedtweet[ss[0]:ss[1]])

                        if feat == 'ftv':
                            dict['ftv'] += 1

                        break

            feat = classify(word, postag)

            if feat not in dict.keys():
                feat = 'NA'

            specialcase = 'special-'

            if feat.startswith(specialcase): # special case: feature exists within token
                specialfeat = feat[feat.index(specialcase) + len(specialcase):]
                if specialfeat == 'dashes': # special case: dashes
                    dict[specialfeat] += word.count('-')

            elif feat != 'NA':
                dict[feat] += 1

        # Calculate asl and atl
        dict['asl'] = calculateasl(tweet)
        dict['atl'] = calculateatl(tokenizedtweet)

        featurecount.append(dict)

    return featurecount

def calculateasl(tweet):
    '''
    Return average sentence length (in tokens).
    '''

    newlinestrip = tweet.strip('\n')
    sentencesplittweet = filter(None, re.split("\W+\\.", newlinestrip))

    numbertokens = 0
    numbersentences = len(sentencesplittweet)

    for sentence in sentencesplittweet:
        numbertokens += len(filter(None, tokenize(sentence)))

    return numbertokens/float(numbersentences)

def calculateatl(tokenizedtweet):
    '''
    Return average token length (in characters) excluding punctuation.
    '''

    punctuation = ['#', '$', '.', ',', ':', '(', ')', '"', '\'']
    charactercount = 0
    punctuationtokens = 0

    tokenizedtweet = [t.strip('\n') for t in tokenizedtweet]

    for token in tokenizedtweet:
        index = token.rfind("\\")
        postag = token[index + 1:]

        if postag not in punctuation:
            charactercount += len(token[:index])
        else:
            punctuationtokens += 1

    return charactercount/float(len(tokenizedtweet) - punctuationtokens)

def assembleoutput(inputfilename, featurecount):
    '''Sample ARFF file

        @RELATION test

        @ATTRIBUTE firstpersonpronouns          NUMERIC
        @ATTRIBUTE secondpersonpronouns         NUMERIC
        @ATTRIBUTE thirdpersonpronouns          NUMERIC
        @ATTRIBUTE coordinatingconjunctions     NUMERIC
        @ATTRIBUTE pasttenseverbs               NUMERIC
        @ATTRIBUTE futuretenseverbs             NUMERIC
        @ATTRIBUTE commas                       NUMERIC
        @ATTRIBUTE colons                       NUMERIC
        @ATTRIBUTE dashes                       NUMERIC
        @ATTRIBUTE parentheses                  NUMERIC
        @ATTRIBUTE ellipses                     NUMERIC
        @ATTRIBUTE commonnouns                  NUMERIC
        @ATTRIBUTE propernouns                  NUMERIC
        @ATTRIBUTE adverbs                      NUMERIC
        @ATTRIBUTE whwords                      NUMERIC
        @ATTRIBUTE modernslang                  NUMERIC
        @ATTRIBUTE uppercasewords               NUMERIC
        @ATTRIBUTE avgsentencelength            NUMERIC
        @ATTRIBUTE avgtokenlength               NUMERIC
        @ATTRIBUTE sentencecount                NUMERIC
        ...
        @ATTRIBUTE class                        {0, 2, 4}

        @DATA
        5,1,0,2,3,4,0,1,0,1,4,1,1,1,1,1,1,1,1,1,1,0
        5,1,0,2,3,4,0,1,0,1,4,1,1,1,1,1,1,1,1,1,1,0
        5,1,0,2,3,4,0,1,0,1,4,1,1,1,1,1,1,1,1,1,1,0
        5,1,0,2,3,4,0,1,0,1,4,1,1,1,1,1,1,1,1,1,1,0
        5,1,0,2,3,4,0,1,0,1,4,1,1,1,1,1,1,1,1,1,1,2
        5,1,0,2,3,4,0,1,0,1,4,1,1,1,1,1,1,1,1,1,1,4
    '''

    out = "@RELATION " + inputfilename + "\n"

    # MODULARITY: ADD FEATURE TO THIS LIST WITH CORRESPONDING 'CODE' INDICATED IN countfeatures() dictionary
    attributedict = OrderedDict([('firstpersonpronouns', 'fpp'), ('secondpersonpronouns', 'spp'),
                                 ('thirdpersonpronouns', 'tpp'), ('coordinatingconjunctions','cc'),
                                 ('pasttenseverbs','ptv'), ('futuretenseverbs','ftv'),
                                 ('commas','commas'), ('colons','colons'),
                                 ('dashes','dashes'), ('parentheses','parentheses'),
                                 ('ellipses','ellipses'), ('commonnouns','cn'),
                                 ('propernouns','pn'), ('adverbs','adverbs'),
                                 ('whwords','whwords'), ('modernslang','slang'),
                                 ('uppercasewords','ucw'), ('avgsentencelength','asl'),
                                 ('avgtokenlength','atl'), ('sentencecount','sc'),
                                 ('class','class')])

    for att in attributedict.items():
        if att[0] != 'class':
            out += "\n@ATTRIBUTE " + att[0] + "\t\t\tNUMERIC"

    out += "\n@ATTRIBUTE class\t\t\t{0,2,4}"
    out += "\n\n@DATA"

    for dict in featurecount:
        out += '\n'
        for att in attributedict.values():
            out += str(dict[att])
            if att != "class": #Don't print last comma
                out += ","
    out += "\n"

    return out

def printtooutput(text, outputfile):
    with open(outputfile, "w") as outputf:
        print(text, file = outputf)

if __name__ == "__main__":
    main(sys.argv[1:])

'''
TODO:
Potentially unfinished business:
    - Future tense verbs
        - cases I didn't consider after running training/test data
    - Past tense verbs
        - cases I didn't consider after running training/test data
    - Modern slang
        - what is slang marked as?

Make more modular!! Functions to add functionality easily!!

'''