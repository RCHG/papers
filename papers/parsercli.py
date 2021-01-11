import argparse
import logging

def cli_parser(config, settings):

    # Here we create a parser and we store in 'cmd' the commands

    parser     = argparse.ArgumentParser(description='BibTeX library management tool (.bib files)')
    subparsers = parser.add_subparsers(dest='cmd')  

    # =======================================================================================
    # configuration (re-used everywhere)
    # =======================================================================================

    loggingp = argparse.ArgumentParser(add_help=False)
    grp      = loggingp.add_argument_group('logging level (default warn)')
    egrp     = grp.add_mutually_exclusive_group()
    egrp.add_argument('--debug', action='store_const', dest='logging_level', const=logging.DEBUG)
    egrp.add_argument('--info' , action='store_const', dest='logging_level', const=logging.INFO)
    egrp.add_argument('--warn' , action='store_const', dest='logging_level', const=logging.WARN)
    egrp.add_argument('--error', action='store_const', dest='logging_level', const=logging.ERROR)

    cfg = argparse.ArgumentParser(add_help=False, parents=[loggingp])
    grp = cfg.add_argument_group('config')
    grp.add_argument('--filesdir', default=config.filesdir, help='files directory (default: %(default)s)')
    grp.add_argument('--bibtex'  , default=config.bibtex,   help='bibtex database (default: %(default)s)')
    grp.add_argument('--dry-run' , action='store_true',     help='no PDF renaming/copying, no bibtex writing on disk (for testing)')


    # =======================================================================================
    # status
    # =======================================================================================

    statusp = subparsers.add_parser('status', description='view install status', parents=[cfg])
    statusp.add_argument('--no-check-files' , action='store_true', help='faster, less info')
    statusp.add_argument('-v','--verbose'   , action='store_true', help='app status info')

    # =======================================================================================
    # install
    # =======================================================================================

    installp = subparsers.add_parser('install', description='setup or update papers install',
        parents=[cfg])
    installp.add_argument('--reset-paths', action='store_true') 
    # egrp = installp.add_mutually_exclusive_group()
    installp.add_argument('--local', action='store_true', 
        help="""save config file in current directory (global install by default). 
        This file will be loaded instead of the global configuration file everytime 
        papers is executed from this directory. This will affect the default bibtex file, 
        the files directory, as well as the git-tracking option. Note this option does
        not imply anything about the actual location of bibtex file and files directory.
        """)
    installp.add_argument('--git', action='store_true', 
        help="""Track bibtex files with git. 
        Each time the bibtex is modified, a copy of the file is saved in a git-tracked
        global directory (see papers status), and committed. Note the original bibtex name is 
        kept, so that different files can be tracked simultaneously, as long as the names do
        not conflict. This option is mainly useful for backup purposes (local or remote).
        Use in combination with `papers git`'
        """) 
    installp.add_argument('--gitdir', default=config.gitdir, help='default: %(default)s')

    grp = installp.add_argument_group('status')
    # grp.add_argument('-l','--status', action='store_true')
    # grp.add_argument('-v','--verbose', action='store_true')
    # grp.add_argument('-c','--check-files', action='store_true')
    grp.add_argument('--no-check-files', action='store_true', help='faster, less info')
    # grp.add_argument('-v','--verbose', action='store_true', help='app status info')

    # =======================================================================================
    # add
    # =======================================================================================
    addp = subparsers.add_parser('add', description='add PDF(s) or bibtex(s) to library',
        parents=[cfg])
    addp.add_argument('file', nargs='+')
    # addp.add_argument('-f','--force', action='store_true', help='disable interactive')

    grp = addp.add_argument_group('duplicate check')
    grp.add_argument('--no-check-duplicate', action='store_true', 
        help='disable duplicate check (faster, create duplicates)')
    grp.add_argument('--no-merge-files', action='store_true', 
        help='distinct "file" field considered a conflict, all other things being equal')
    grp.add_argument('-u', '--update-key', action='store_true', 
        help='update added key according to any existing duplicate (otherwise an error might be raised on identical insert key)')
    # grp.add_argument('-f', '--force', action='store_true', help='no interactive')
    grp.add_argument('-m', '--mode', default='i', choices=['u', 'U', 'o', 's', 'r', 'i','a'],
        help='''if duplicates are found, the default is to start an (i)nteractive dialogue, 
        unless "mode" is set to (r)aise, (s)skip new, (u)pdate missing, (U)pdate with new, (o)verwrite completely.
        ''')

    grp = addp.add_argument_group('directory scan')
    grp.add_argument('--recursive', action='store_true', 
        help='accept directory as argument, for recursive scan \
        of .pdf files (bibtex files are ignored in this mode')
    grp.add_argument('--ignore-errors', action='store_true', 
        help='ignore errors when adding multiple files')

    grp = addp.add_argument_group('pdf metadata')
    grp.add_argument('--no-query-doi'     , action='store_true', help='do not attempt to parse and query doi')
    grp.add_argument('--no-query-fulltext', action='store_true', help='do not attempt to query fulltext in case doi query fails')
    grp.add_argument('--scholar'          , action='store_true', help='use google scholar instead of crossref')

    grp = addp.add_argument_group('attached files')
    grp.add_argument('-a','--attachment', nargs='+'          , help=argparse.SUPPRESS) #'supplementary material')
    grp.add_argument('-r','--rename'    , action='store_true', help='rename PDFs according to key')
    grp.add_argument('-c','--copy'      , action='store_true', help='copy file instead of moving them')


    # =======================================================================================
    # check
    # =======================================================================================
    
    checkp = subparsers.add_parser('check', description='check and fix entries', 
        parents=[cfg])
    checkp.add_argument('-k', '--keys', nargs='+', help='apply check on this key subset')
    checkp.add_argument('-f','--force', action='store_true', help='do not ask')

    grp = checkp.add_argument_group('entry key')
    grp.add_argument('--fix-key'  , action='store_true', help='fix key based on author name and date (in case missing or digit)')
    grp.add_argument('--key-ascii', action='store_true', help='replace keys unicode character with ascii')
    grp.add_argument('--auto-key' , action='store_true', help='new, auto-generated key for all entries')
    grp.add_argument('--nauthor'  , type=int, default=settings['NAUTHOR'], help='number of authors to include in key (default:%(default)s)')
    grp.add_argument('--ntitle'   , type=int, default=settings['NTITLE'], help='number of title words to include in key (default:%(default)s)')
    # grp.add_argument('--ascii-key', action='store_true', help='replace unicode characters with closest ascii')
    grp.add_argument('-t','--tag' , type=str, default='no-tag', help='Add a tag/keyword to an entry of the bibtex file.')


    grp = checkp.add_argument_group('crossref fetch and fix')
    grp.add_argument('--fix-doi'  , action='store_true', help='fix doi for some common issues (e.g. DOI: inside doi, .received at the end')
    grp.add_argument('--fetch'    , action='store_true', help='fetch metadata from doi and update entry')
    grp.add_argument('--fetch-all', action='store_true', help='fetch metadata from title and author field and update entry (only when doi is missing)')

    grp = checkp.add_argument_group('names')
    grp.add_argument('--format-name', action='store_true', help='author name as family, given, without brackets')
    grp.add_argument('--encoding'   , choices=['latex','unicode'], help='bibtex field encoding')

    grp = checkp.add_argument_group('merge/conflict')
    grp.add_argument('--duplicates',action='store_true', help='solve duplicates')
    grp.add_argument('-m', '--mode', default='i', choices=list('ims'), help='''(i)interactive mode by default, otherwise (m)erge or (s)kip failed''')
    # grp.add_argument('--ignore', action='store_true', help='ignore unresolved conflicts')
    # checkp.add_argument('--merge-keys', nargs='+', help='only merge remove / merge duplicates')
    # checkp.add_argument('--duplicates',action='store_true', help='remove / merge duplicates')



    # filecheck
    # =====
    filecheckp = subparsers.add_parser('filecheck', description='check attached file(s)',
        parents=[cfg])
    # filecheckp.add_argument('-f','--force', action='store_true', 
    #     help='do not ask before performing actions')

    # action on files
    filecheckp.add_argument('-r','--rename', action='store_true', help='rename files')
    filecheckp.add_argument('-c','--copy', action='store_true', help='in combination with --rename, keep a copy of the file in its original location')

    # various metadata and duplicate checks
    filecheckp.add_argument('--metadata-check', action='store_true', help='parse pdf metadata and check against metadata (currently doi only)')
    filecheckp.add_argument('--hash-check'    , action='store_true', help='check file hash sum to remove any duplicates')
    filecheckp.add_argument('-d', '--delete-broken', action='store_true', help='remove file entry if the file link is broken')
    filecheckp.add_argument('--fix-mendeley', action='store_true', help='fix a Mendeley bug where the leading "/" is omitted.')

    filecheckp.add_argument('--force', action='store_true', help='no interactive prompt, strictly follow options') 
    # filecheckp.add_argument('--search-for-files', action='store_true',
    #     help='search for missing files')
    # filecheckp.add_argument('--searchdir', nargs='+',
    #     help='search missing file link for existing bibtex entries, based on doi')
    # filecheckp.add_argument('-D', '--delete-free', action='store_true', 
        # help='delete file which is not associated with any entry')
    # filecheckp.add_argument('-a', '--all', action='store_true', help='--hash and --meta')

    # open
    # =============
    openp = subparsers.add_parser('open', description='open file of an entry',
        parents=[cfg])
    grp = openp.add_argument_group('pdf') 
    grp.add_argument('--key', nargs='+')
    grp.add_argument('--num', nargs="+")

    # list
    # ======
    listp = subparsers.add_parser('list', description='list (a subset of) entries',
        parents=[cfg])

    mgrp = listp.add_mutually_exclusive_group()
    mgrp.add_argument('--strict', action='store_true', help='exact matching - instead of substring (only (*): title, author, abstract)')
    mgrp.add_argument('--fuzzy', action='store_true', help='fuzzy matching - instead of substring (only (*): title, author, abstract)')

    listp.add_argument('--fuzzy-ratio', type=int, default=settings['FUZZY_RATIO'], help='threshold for fuzzy matching of title, author, abstract (default:%(default)s)')
    listp.add_argument('--similarity', choices=['EXACT','GOOD','FAIR','PARTIAL','FUZZY'], default=settings['DEFAULT_SIMILARITY'], help='duplicate testing (default:%(default)s)')
    listp.add_argument('--invert', action='store_true')

    grp = listp.add_argument_group('search')
    grp.add_argument('-a','--author', nargs='+', help='any of the authors (*)')
    grp.add_argument('--first-author', nargs='+')
    grp.add_argument('-y','--year', nargs='+')
    grp.add_argument('-t','--title', help='title (*)')
    grp.add_argument('--abstract', help='abstract (*)')
    grp.add_argument('--key', nargs='+')
    grp.add_argument('--doi', nargs='+')


    grp = listp.add_argument_group('check')
    grp.add_argument('--duplicates-key' , action='store_true', help='list key duplicates only')
    grp.add_argument('--duplicates-doi' , action='store_true', help='list doi duplicates only')
    grp.add_argument('--duplicates-tit' , action='store_true', help='list tit duplicates only')
    grp.add_argument('--duplicates'     , action='store_true', help='list all duplicates (see --similarity)')
    grp.add_argument('--has-file'       , action='store_true')
    grp.add_argument('--no-file'        , action='store_true')
    grp.add_argument('--broken-file'    , action='store_true')
    grp.add_argument('--review-required', action='store_true', help='suspicious entry (invalid dois, missing field etc.)')

    grp = listp.add_argument_group('formatting')
    mgrp = grp.add_mutually_exclusive_group()
    mgrp.add_argument('-k','--key-only', action='store_true')
    mgrp.add_argument('-l', '--one-liner', action='store_true', help='one liner')
    mgrp.add_argument('-ls', '--one-liner-short', action='store_true', help='one liner short')
    mgrp.add_argument('-f', '--field', nargs='+', help='specific field(s) only')
    grp.add_argument('--no-key', action='store_true')

    grp = listp.add_argument_group('action on listed results (pipe)')
    grp.add_argument('--delete', action='store_true')
    grp.add_argument('--edit'  , action='store_true', help='interactive edit text file with entries, and re-insert them')
    grp.add_argument('--fetch' , action='store_true', help='fetch and fix metadata')
    # grp.add_argument('--merge-duplicates', action='store_true')

    # doi
    # ===

    doip = subparsers.add_parser('doi', description='parse DOI from PDF')
    doip.add_argument('pdf')
    doip.add_argument('--image', action='store_true', help='convert to image and use tesseract instead of pdftotext')
    
    # fetch
    # =====   
    fetchp = subparsers.add_parser('fetch', description='fetch bibtex from DOI')
    fetchp.add_argument('doi')

    # extract
    # ========
    extractp = subparsers.add_parser('extract', description='extract pdf metadata', parents=[loggingp])
    extractp.add_argument('pdf')
    extractp.add_argument('-n', '--word-count', type=int, default=200)
    extractp.add_argument('--fulltext', action='store_true', help='fulltext only (otherwise DOI-based)')
    extractp.add_argument('--scholar' , action='store_true', help='use google scholar instead of default crossref for fulltext search')
    extractp.add_argument('--image'   , action='store_true', help='convert to image and use tesseract instead of pdftotext')

    # *** Pure OS related file checks ***

    # undo
    # ====
    undop = subparsers.add_parser('undo', parents=[cfg])

    # git
    # ===
    gitp = subparsers.add_parser('git', description='git subcommand')
    gitp.add_argument('gitargs', nargs=argparse.REMAINDER)

    return parser 
