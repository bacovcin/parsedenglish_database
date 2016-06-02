from sys import argv

# Arguments must occur in this order
# argv[0] = script name
# argv[1] = path to database file
# argv[2] = input file path (.cod.ooo file)
# argv[3] = output file path (tab-separated)
# argv[4:] = additional column names

# Function that returns an integer if the string is an integer and
# -1000 otherwise


def tryint(x):
    try:
        return(int(x))
    except:
        return(-1000)


# Generates a python database and adds correct metadata to file

dbfile = open(argv[1]).readlines()

names = '\t'.join(dbfile[0].rstrip().split(':'))

db = {}
# Database is a dictionary of dicitonaries
# Key of first dictionary: file id
# Key of second dictionary: tuple of start token num and end token num
# For single text files the token ids = x
for line in dbfile[1:]:
    s = line.rstrip().split(':')
    try:
        db[s[1]][(s[2], s[3])] = '\t'.join(s)
    except:
        db[s[1]] = {}
        db[s[1]][(s[2], s[3])] = '\t'.join(s)

# Load the coding output
coded_file = open(argv[2]).readlines()

# Open the final file
outfile = open(argv[3], 'w+')
outfile.write(names + '\t' + '\t'.join(argv[4:]) + '\n')

# Walk through output and append appropriate metadata
keyerrors = []
i = 0
filelen = len(coded_file)
for line in coded_file:
    i += 1
    codes = '\t'.join(line.split('@')[0].split(':')) + '\n'
    token = line.split('@')[1].split('.')[-1].rstrip()
    filename = line.split('@')[1].split(',')[0].lower()
    try:
        for text in db[filename].keys():
            # Check if file is:
            # Single text (i.e. startid == 'x'
            # or if the tokenid is between the text's start and end ids
            if ((text[0] == 'x') or
               ((tryint(token) >= tryint(text[0]) and
                 (tryint(token) <= tryint(text[1]))))):
                outfile.write(db[filename][text] +
                              '\t' +
                              token +
                              '\t' +
                              codes)
    except:
        if filename not in keyerrors:
            keyerrors.append(filename)
            print(filename + ' is missing from database...')

if len(keyerrors) > 0:
    outfile = open('missing_keys.txt', 'w')
    for filename in keyerrors:
        outfile.write(filename + '\n')
