from copy import copy
from PTree import ParseTree, MatchParen

def tryint(x):
    try:
        return(int(x))
    except:
        return(-1000)


def POSSearch(tree):
    foreign = []
    names = []
    oc = []
    words = []
    if tree.height == 0:
        if ((tree.content[0] not in ['*', '<']) and
           (tree.name not in [',', '.',
                              '"', "'",
                              'X', 'ID',
                              'CODE'])):
            words.append(tree.content)
            if 'FW' in tree.name:
                foreign.append(tree.content)
            elif 'NPR' in tree.name or 'NR' in tree.name:
                names.append(tree.content)
            elif ((tree.name[:2] == 'VB') or
                  ((tree.name[0] == 'N') and
                   ('NP' not in tree.name) and
                   ('NEG' not in tree.name)) or
                  (tree.name[:3] in ['ADV', 'ADJ'])):
                oc.append(tree.content)
    else:
        for x in tree.content:
            output = POSSearch(x)
            foreign += output[0]
            names += output[1]
            oc += output[2]
            words += output[3]
    return (foreign, names, oc, words)


def ParseFile(infile, db):
    def ExtractID(tree):
        if tree.content[-1].name == 'ID':
            return(tree.content[-1].content)
        else:
            for subtree in tree.content:
                if subtree.name == 'ID':
                    return(subtree.content)

    identified_texts = {}
    for key1 in db.keys():
        identified_texts[key1] = {}
        for key2 in db[key1].keys():
            identified_texts[key1][key2] = []
    unidentified_texts = {}
    token = ''
    i = 0
    for line in infile:
        if line == '\n' and 'ID' in token:
            i += 1
            print('Parsed Token #' + str(i))
            ptoken = ParseTree(MatchParen(token.lstrip().rstrip())[0][0])
            tokid = ExtractID(ptoken)
            if tokid is None:
                token = ''
                continue
            tokfn = tokid.split(',')[0].lower()
            toknum = tokid.split('.')[-1]
            try:
                if list(identified_texts[tokfn].keys())[0] == ('x', 'x'):
                    identified_texts[tokfn][('x', 'x')].append(ptoken)
                else:
                    for key in identified_texts[tokfn].keys():
                        if ((int(toknum) >= int(key[0])) and
                           (int(toknum) <= int(key[1]))):
                            identified_texts[tokfn][key].append(ptoken)
                            break
                    else:
                        try:
                            unidentified_texts[tokfn].append(ptoken)
                        except:
                            unidentified_texts[tokfn] = [ptoken]
            except:
                try:
                    unidentified_texts[tokfn].append(ptoken)
                except:
                    unidentified_texts[tokfn] = [ptoken]
            token = ''
        elif line == '\n':
            token = ''
        else:
            token = token + line.rstrip().lstrip()
    return identified_texts, unidentified_texts


db_file = open('English_database.txt').readlines()
bkp_file = open('English_database.bkp', 'w')

db_names = db_file[0].rstrip().split(':')
bkp_file.write(db_file[0])
# Dictionary of dictionaries:
# Key 1: Filename
# Key 2: (start token number, end token number)
# Value: dictionary of column values (including above material)
db = {}

print('Generating database')
for line in db_file[1:]:
    bkp_file.write(line)
    s = line.rstrip().split(':')
    db_entry = {}
    for i in range(len(db_names)):
        db_entry[db_names[i]] = s[i]
    try:
        db[s[0]][(s[1], s[2])] = copy(db_entry)
    except:
        db[s[0]] = {}
        db[s[0]][(s[1], s[2])] = copy(db_entry)

bkp_file.close()
print('Parsing texts')
identified_texts, unidentified_texts = ParseFile(open('corpus.txt'), db)

print('Updating identified text')
for fn in identified_texts.keys():
    for text in identified_texts[fn].keys():
        foreign = []
        names = []
        oc = []
        words = []
        for tree in identified_texts[fn][text]:
            output = POSSearch(tree)
            foreign += output[0]
            names += output[1]
            oc += output[2]
            words += output[3]
        db[fn][text]['Words'] = str(len(words))
        db[fn][text]['OCWords'] = str(len(oc))
        db[fn][text]['NamWords'] = str(len(names))
        db[fn][text]['ForWords'] = str(len(foreign))

        db[fn][text]['Types'] = str(len(set(words)))
        db[fn][text]['OCTypes'] = str(len(set(oc)))
        db[fn][text]['NamTypes'] = str(len(set(names)))
        db[fn][text]['ForTypes'] = str(len(set(foreign)))

        db[fn][text]['Chars'] = str(len([y for x in words for y in x]))
        db[fn][text]['OCChars'] = str(len([y for x in oc for y in x]))
        db[fn][text]['NamChars'] = str(len([y for x in names for y in x]))
        db[fn][text]['ForChars'] = str(len([y for x in foreign for y in x]))

        db[fn][text]['Tokens'] = str(len(identified_texts[fn][text]))

print('Collecting data on unidentified texts')
key = ('x', 'x')
oasklist = ['YoC',
            'YoM',
            'AuthName',
            'AuthBD',
            'AuthSex']
lasklist = ['YoC',
            'YoM',
            'AuthName',
            'AuthBD',
            'AuthSex',
            'RecName',
            'RecBD',
            'RecSex',
            'RecRelation']

for fn in unidentified_texts.keys():
    try:
        db[fn][key] = {}
    except:
        db[fn] = {}
        db[fn][key] = {}
    foreign = []
    names = []
    oc = []
    words = []
    for tree in unidentified_texts[fn]:
        output = POSSearch(tree)
        foreign += output[0]
        names += output[1]
        oc += output[2]
        words += output[3]
    db[fn][key]['Words'] = str(len(words))
    db[fn][key]['OCWords'] = str(len(oc))
    db[fn][key]['NamWords'] = str(len(names))
    db[fn][key]['ForWords'] = str(len(foreign))

    db[fn][key]['Types'] = str(len(set(words)))
    db[fn][key]['OCTypes'] = str(len(set(oc)))
    db[fn][key]['NamTypes'] = str(len(set(names)))
    db[fn][key]['ForTypes'] = str(len(set(foreign)))

    db[fn][key]['Chars'] = str(len([y for x in words for y in x]))
    db[fn][key]['OCChars'] = str(len([y for x in oc for y in x]))
    db[fn][key]['NamChars'] = str(len([y for x in names for y in x]))
    db[fn][key]['ForChars'] = str(len([y for x in foreign for y in x]))

    db[fn][key]['Tokens'] = str(len(unidentified_texts[fn]))

    db[fn][key]['Lat'] = 'x'
    db[fn][key]['Long'] = 'x'
    db[fn][key]['Location'] = 'x'
    db[fn][key]['Dialect'] = 'x'

    token = unidentified_texts[fn][0]
    if token.content[0].name == 'METADATA':
        print(token.content[0])
    print(token.content[-1].content)
    db[fn][key]['Genre'] = input('What is the value of column Genre?\n')

    if db[fn][key]['Genre'].lower() == 'l':
        for ask in lasklist:
            db[fn][key][ask] = input('What is the value of column ' +
                                     ask +
                                     '?\n').rstrip()
    else:
        db[fn][key]['RecName'] = 'x'
        db[fn][key]['RecBD'] = 'x'
        db[fn][key]['RecSex'] = 'x'
        db[fn][key]['RecRelation'] = 'x'
        for ask in oasklist:
            db[fn][key][ask] = input('What is the value of column ' +
                                     ask +
                                     '?\n').rstrip()
    try:
        db[fn][key]['AuthAge'] = str(int(db[fn][key]['YoC']) -
                                     int(db[fn][key]['AuthBD']))
    except:
        db[fn][key]['AuthAge'] = 'x'
    try:
        db[fn][key]['RecAge'] = str(int(db[fn][key]['YoC']) -
                                    int(db[fn][key]['RecBD']))
    except:
        db[fn][key]['RecAge'] = 'x'

print('Writing out database...')
outfile = open('English_database.txt', 'w')
outfile.write(':'.join(db_names) + '\n')
for fn in sorted(db.keys()):
    for text in sorted(db[fn].keys(), key=lambda x: tryint(x[0])):
        i += 1
        print('Database line #' + str(i))
        outtext = fn + ':' + text[0] + ':' + text[1] + ':'
        print(db[fn][text])
        for key in db_names[3:]:
            outtext += db[fn][text][key] + ':'
        outfile.write(outtext.rstrip(':') + '\n')
