import papers.boxea as boxea
import csv

class bcol:
    # https://stackoverflow.com/a/287944/2192272
    HEAD    = '\033[95m'
    BLUE    = '\033[94m'
    GREEN   = '\033[92m'
    WARN    = '\033[93m'
    FAIL    = '\033[91m'
    ENDC    = '\033[0m'
    BOLD    = '\033[1m'
    ULINE   = '\033[4m'

def read_journal_abbrv(journal):
    with open('/usr/local/share/papers/journalList_dots.csv', mode='r') as infile:
        reader = csv.reader(infile, delimiter=';')
        abbrev = {rows[0]:rows[1] for rows in reader}
    if journal in abbrev.keys():
        journal_abbrev = abbrev[journal]
    else:
        journal_abbrev = journal

    return journal_abbrev

def boxed_status(lines, fstatus, bstatus, title):
    """boxedlist: from a list of lines it returns
                 a printable boxed output. 

    :param lines:
    :param fstatus:
    :param bstatus:
    :param title:
    """

    # Get dimensions ============================================
    lenlines = [len(a) for a in lines]
    maxlines = max(lenlines)
    span     = [maxlines-len(a) for a in lines]

    # Add the top-rule ==========================================
    lines[0]='+'+'-'*maxlines+'--+'

    # Reformat the inner lines ==================================
    for iline, line in enumerate(lines):
        if iline>0:
            lines[iline]='| '+lines[iline]+span[iline]*' '+' |'

    # Add bottom-rule ===========================================
    lines.append(lines[0])


    boxlines = boxea.ascii_to_box(u'\n'.join(lines))
    if "missing" in fstatus or "empty" in fstatus:
        boxlines = boxlines.replace(fstatus, bcol.WARN+fstatus+bcol.ENDC)
    else:
        boxlines = boxlines.replace(fstatus, bcol.BLUE+fstatus+bcol.ENDC)
    if "empty" in bstatus: 
        boxlines = boxlines.replace(bstatus, bcol.WARN+bstatus+bcol.ENDC)
    elif "corrupted" in bstatus:
        boxlines = boxlines.replace(bstatus, bcol.FAIL+bstatus+bcol.ENDC)
    else:
        boxlines = boxlines.replace(bstatus, bcol.BLUE+bstatus+bcol.ENDC)

    boxlines = boxlines.replace(title,   bcol.BOLD+title+bcol.ENDC)
    return boxlines

def boxed_list(lines_out, cname, list_entries, total_entries):
    strdel= '<xBo><xBl><xE><xG><xE>'
    strname= '[bib: '+cname+']'
    maxlines = max([len(a) for a in lines_out])
    lenlines = [len(a)  for a in lines_out]
    str_number = '['+str(list_entries)+'/'+str(total_entries)+strdel+']'
    len_number = len(str_number)
    for iline, oline in enumerate(lines_out):
        newstring = (maxlines-lenlines[iline])*' '+'    |'
        lines_out[iline] = lines_out[iline].replace('<xF>', newstring)
    delta = len('<xBo><xBl><xE><xG><xE>')
    header = '\n+---'+str_number+'---'+strname+(maxlines-4-len_number-len(strname)-3)*'-'+'+'
    footer = '+-'+strdel+(maxlines-2-delta)*'-'+'+\n'
    lines_out.insert(0,header)
    lines_out.append(footer)
    output = boxea.ascii_to_box(u"\n".join(lines_out))
    output = output.replace(strdel+'-','─')
    output = output.replace('<xBo>',bcol.BOLD)
    output = output.replace('<xBl>',bcol.BLUE)
    output = output.replace('<xE>' ,bcol.ENDC)
    output = output.replace('<xG>' ,bcol.GREEN)
    return output
