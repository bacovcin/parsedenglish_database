from copy import copy
from PTree import ParseTree, MatchParen

# Returns integer for integer strings or -1000 for non-int


def tryint(x):
    try:
        return(int(x))
    except:
        return(-1000)

# Search for Part Of Speech types


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
        for key2 in db[key1].keys():
            try:
                identified_texts[key2[0]][(key2[1], key2[2])] = []
            except:
                identified_texts[key2[0]] = {}
                identified_texts[key2[0]][(key2[1], key2[2])] = []
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
# Key 1: TextID
# Key 2: (filename, start token number, end token number)
# Value: dictionary of column values (including above material)
db = {}

print('Generating database')
for line in db_file[1:]:
    bkp_file.write(line)
    s = line.rstrip().split(':')
    db_entry = {}
    for i in range(len(db_names)):
        try:
            db_entry[db_names[i]] = s[i]
        except:
            db_entry[db_names[i]] = 'x'
    try:
        db[s[0]][(s[1], s[2], s[3])] = copy(db_entry)
    except:
        db[s[0]] = {}
        db[s[0]][(s[1], s[2], s[3])] = copy(db_entry)

bkp_file.close()
print('Parsing texts')
identified_texts, unidentified_texts = ParseFile(open('corpus.txt'), db)

textids = {}
for key in db.keys():
    textids[key] = []

print('Updating identified text')
for fn in identified_texts.keys():
    for text in identified_texts[fn].keys():
        key2 = (fn, text[0], text[1])
        for key in db.keys():
            if key2 in db[key].keys():
                textid = key
                break
        else:
            print(key2)
            input('ERROR!!! ERROR!!!')
        textids[textid] += identified_texts[fn][text]

for fn in identified_texts.keys():
    for text in identified_texts[fn].keys():
        key2 = (fn, text[0], text[1])
        for key in db.keys():
            if key2 in db[key].keys():
                textid = key
                break
        else:
            print(key2)
            input('ERROR!!! ERROR!!!')
        foreign = []
        names = []
        oc = []
        words = []
        for tree in textids[textid]:
            output = POSSearch(tree)
            foreign += output[0]
            names += output[1]
            oc += output[2]
            words += output[3]
        db[textid][key2]['Words'] = str(len(words))
        db[textid][key2]['OCWords'] = str(len(oc))
        db[textid][key2]['NamWords'] = str(len(names))
        db[textid][key2]['ForWords'] = str(len(foreign))

        db[textid][key2]['Types'] = str(len(set(words)))
        db[textid][key2]['OCTypes'] = str(len(set(oc)))
        db[textid][key2]['NamTypes'] = str(len(set(names)))
        db[textid][key2]['ForTypes'] = str(len(set(foreign)))

        db[textid][key2]['Chars'] = str(len([y for x in words for y in x]))
        db[textid][key2]['OCChars'] = str(len([y for x in oc for y in x]))
        db[textid][key2]['NamChars'] = str(len([y for x in names for y in x]))
        db[textid][key2]['ForChars'] = str(len([y for x in foreign for y in x]))

        db[textid][key2]['Tokens'] = str(len(textids[textid]))

print('Collecting data on unidentified texts')
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

unident_id = 1
for fn in unidentified_texts.keys():
    key1 = 'x' + str(unident_id)
    unident_id += 1
    key2 = (fn, 'x', 'x')
    try:
        db[key1][key2] = {}
    except:
        db[key1] = {}
        db[key1][key2] = {}
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
    db[key1][key2]['Words'] = str(len(words))
    db[key1][key2]['OCWords'] = str(len(oc))
    db[key1][key2]['NamWords'] = str(len(names))
    db[key1][key2]['ForWords'] = str(len(foreign))

    db[key1][key2]['Types'] = str(len(set(words)))
    db[key1][key2]['OCTypes'] = str(len(set(oc)))
    db[key1][key2]['NamTypes'] = str(len(set(names)))
    db[key1][key2]['ForTypes'] = str(len(set(foreign)))

    db[key1][key2]['Chars'] = str(len([y for x in words for y in x]))
    db[key1][key2]['OCChars'] = str(len([y for x in oc for y in x]))
    db[key1][key2]['NamChars'] = str(len([y for x in names for y in x]))
    db[key1][key2]['ForChars'] = str(len([y for x in foreign for y in x]))

    db[key1][key2]['Tokens'] = str(len(unidentified_texts[fn]))

    db[key1][key2]['Lat'] = 'x'
    db[key1][key2]['Long'] = 'x'
    db[key1][key2]['Location'] = 'x'
    db[key1][key2]['Dialect'] = 'x'

    token = unidentified_texts[fn][0]
    if token.content[0].name == 'METADATA':
        print(token.content[0])
    print(token.content[-1].content)
    db[key1][key2]['Genre'] = input('What is the value of column Genre?\n')

    if db[key1][key2]['Genre'].lower() == 'l':
        for ask in lasklist:
            db[key1][key2][ask] = input('What is the value of column ' +
                                     ask +
                                     '?\n').rstrip()
    else:
        db[key1][key2]['RecName'] = 'x'
        db[key1][key2]['RecBD'] = 'x'
        db[key1][key2]['RecSex'] = 'x'
        db[key1][key2]['RecRelation'] = 'x'
        for ask in oasklist:
            db[key1][key2][ask] = input('What is the value of column ' +
                                     ask +
                                     '?\n').rstrip()
    try:
        db[key1][key2]['AuthAge'] = str(int(db[key1][key2]['YoC']) -
                                     int(db[key1][key2]['AuthBD']))
    except:
        db[key1][key2]['AuthAge'] = 'x'
    try:
        db[key1][key2]['RecAge'] = str(int(db[key1][key2]['YoC']) -
                                    int(db[key1][key2]['RecBD']))
    except:
        db[key1][key2]['RecAge'] = 'x'

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
