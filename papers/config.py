import os, json, shutil
import subprocess as sp, sys, shutil
import hashlib
import bibtexparser
import six
from six.moves import input as raw_input
from papers import logger
import boxea
import copy
# GIT = False
DRYRUN = False

# config directory location
HOME        = os.environ.get('HOME'           , os.path.expanduser('~'))
CONFIG_HOME = os.environ.get('XDG_CONFIG_HOME', os.path.join(HOME, '.config'))
CACHE_HOME  = os.environ.get('XDG_CACHE_HOME' , os.path.join(HOME, '.cache'))
DATA_HOME   = os.environ.get('XDG_DATA_HOME'  , os.path.join(HOME, '.local','share'))


CONFIG_FILE = os.path.join(CONFIG_HOME , 'papersconfig.json')
DATA_DIR    = os.path.join(DATA_HOME   , 'papers')
CACHE_DIR   = os.path.join(CACHE_HOME  , 'papers')


# utils
# -----

class bcolors:
    # https://stackoverflow.com/a/287944/2192272
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def check_filesdir(folder):
    folder_size = 0
    file_count = 0
    for (path, dirs, files) in os.walk(folder):
      for file in files:
        filename = os.path.join(path, file)
        if filename.endswith('.pdf'):
            folder_size += os.path.getsize(filename)
            file_count += 1
    return file_count, folder_size


class Config(object):
    """configuration class to specify system-wide collections and files-dir
    """
    def __init__(self, file=CONFIG_FILE, data=DATA_DIR, cache=CACHE_DIR,
        bibtex=None, filesdir=None, gitdir=None, git=False, name=None):
        self.file  = file
        self.cname = name
        self.data  = data
        self.cache = cache
        self.gitdir = gitdir  or data
        self.git    = git
        self.filesdir = filesdir or os.path.join(data, 'files')
        self.bibtex = bibtex  or os.path.join(data, 'papers.bib')

    def collections(self):
        files = []
        for root, dirs, files in os.walk(os.path.dirname(self.bibtex)):
            break
        # return sorted(f[:-4] for f in files if f.endswith('.bib'))
        return sorted(f for f in files if f.endswith('.bib'))

    def save(self):
        json.dump({
            "name":self.cname,
            "filesdir":self.filesdir,
            "bibtex":self.bibtex,
            "git":self.git,
            "gitdir":self.gitdir,
            }, open(self.file, 'w'), sort_keys=True, indent=2, separators=(',', ': '))


    def load(self):
        js = json.load(open(self.file))
        self.bibtex = js.get('bibtex', self.bibtex)
        self.filesdir = js.get('filesdir', self.filesdir)
        self.git = js.get('git', self.git)
        self.gitdir = js.get('gitdir', self.gitdir)
        self.cname   = js.get('name', self.cname)

    def reset(self):
        cfg = type(self)()
        self.bibtex = cfg.bibtex
        self.filesdir = cfg.filesdir


    def check_install(self):
        if not os.path.exists(self.cache):
            logger.info('make cache directory for DOI requests: '+self.cache)
            os.makedirs(self.cache)


    # make a git commit?
    @property
    def _gitdir(self):
        return os.path.join(self.gitdir, '.git')

    def gitinit(self, branch=None):
        if not os.path.exists(self._gitdir):
            # with open(os.devnull, 'w') as shutup:
            sp.check_call(['git','init'], cwd=self.gitdir)
        else:
            raise ValueError('git is already initialized in '+self.gitdir)

    def gitcommit(self, branch=None, message=None):
        if os.path.exists(self._gitdir):
            target = os.path.join(self.gitdir, os.path.basename(self.bibtex))
            if not os.path.samefile(self.bibtex, target):
                shutil.copy(self.bibtex, target)
            message = message or 'save '+self.bibtex+' after command:\n\n    papers ' +' '.join(sys.argv[1:])
            with open(os.devnull, 'w') as shutup:
                if branch is not None:
                    sp.check_call(['git','checkout',branch], stdout=shutup, stderr=shutup, cwd=self.gitdir)
                sp.check_call(['git','add',target], stdout=shutup, stderr=shutup, cwd=self.gitdir)
                res = sp.call(['git','commit','-m', message], stdout=shutup, stderr=shutup, cwd=self.gitdir)
                if res == 0:
                    logger.info('git commit')
        else:
            raise ValueError('git is not initialized in '+self.gitdir)

    def status(self, check_files=False, verbose=False):
        title = 'Papers configuration ['+str(self.cname)+']' 

        lines = []
        lines.append(' ')
        lines.append(' '+title )
        lines.append(' ')
        lines.append(' * config file: '+self.file)
        lines.append(' * cache path:  '+self.cache)
        lines.append(' * git-tracked: '+str(self.git))
        if self.git:
           lines.append(' * git path:    '+self.gitdir)

        # CHECKING STATUS filesdir =================================
        if not os.path.exists(self.filesdir):
            fstatus = ' (missing)'
        elif not os.listdir(self.filesdir):
            fstatus = ' (empty)'
        elif check_files:
            file_count, folder_size = check_filesdir(self.filesdir)
            fstatus = " ({} files, {:.1f} MB)".format(file_count, folder_size/(1024*1024.0))
        else:
            fstatus = ''

        files = self.filesdir
        lines.append(' * files path:  '+files+fstatus )


        # CHECKING STATUS bibtex   =================================
        if not os.path.exists(self.bibtex):
            bstatus = ' (missing) '
        elif check_files:
            try:
                bibtexstring = open(self.bibtex).read()
                db = bibtexparser.loads(bibtexstring)
                if len(db.entries):
                    bstatus = ' ({} entries)'.format(len(db.entries))

                else:
                    bstatus = ' (empty) '
            except:
                bstatus = ' (corrupted) '
        elif os.path.getsize(self.bibtex) == 0:
            bstatus = ' (empty) '
        else:
            bstatus = ''
        lines.append(' * bibtex path: '+self.bibtex+bstatus)

        return listlines(lines, fstatus, bstatus, title)

def listlines(lines, fstatus, bstatus, title):
    lenlines = [len(a) for a in lines]
    maxlines = max(lenlines)
    for line in lines:
        spalines = [maxlines-len(a) for a in lines]

    lines[0]='+'+'-'*maxlines+'--+'
    for iline, line in enumerate(lines):
        if iline>0:
            lines[iline]='| '+lines[iline]+spalines[iline]*' '+' |'
    lines.append(lines[0])

    boxlines = boxea.ascii_to_box(u'\n'.join(lines))
    if "missing" in fstatus or "empty" in fstatus:
        boxlines = boxlines.replace(fstatus, bcolors.WARNING+fstatus+bcolors.ENDC)
    else:
        boxlines = boxlines.replace(fstatus, bcolors.OKBLUE+fstatus+bcolors.ENDC)
    if "empty" in bstatus: 
        boxlines = boxlines.replace(bstatus, bcolors.WARNING+bstatus+bcolors.ENDC)
    elif "corrupted" in bstatus:
        boxlines = boxlines.replace(bstatus, bcolors.FAIL+bstatus+bcolors.ENDC)
    else:
        boxlines = boxlines.replace(bstatus, bcolors.OKBLUE+bstatus+bcolors.ENDC)
    boxlines = boxlines.replace(title,   bcolors.BOLD+title+bcolors.ENDC)
    return boxlines

config = Config()
config.check_install()


def cached(file, hashed_key=False):

    file = os.path.join(config.cache, file)

    def decorator(fun):
        if os.path.exists(file):
            cache = json.load(open(file))
        else:
            cache = {}
        def decorated(doi):
            if hashed_key: # use hashed parameter as key (for full text query)
                if six.PY3:
                    key = hashlib.sha256(doi.encode('utf-8')).hexdigest()[:6]
                else:
                    key = hashlib.sha256(doi).hexdigest()[:6]
            else:
                key = doi
            if key in cache:
                logger.debug('load from cache: '+repr((file, key)))
                return cache[key]
            else:
                res = cache[key] = fun(doi)
                if not DRYRUN:
                    json.dump(cache, open(file,'w'))
            return res
        return decorated
    return decorator


def hash_bytestr_iter(bytesiter, hasher, ashexstr=False):
    for block in bytesiter:
        hasher.update(block)
    return (hasher.hexdigest() if ashexstr else hasher.digest())

def file_as_blockiter(afile, blocksize=65536):
    with afile:
        block = afile.read(blocksize)
        while len(block) > 0:
            yield block
            block = afile.read(blocksize)

def checksum(fname):
    """memory-efficient check sum (sha256)

    source: https://stackoverflow.com/a/3431835/2192272
    """
    return hash_bytestr_iter(file_as_blockiter(open(fname, 'rb')), hashlib.sha256())



# move / copy
def move(f1, f2, copy=False, interactive=True):
    dirname = os.path.dirname(f2)
    if dirname and not os.path.exists(dirname):
        logger.info('create directory: '+dirname)
        os.makedirs(dirname)
    if f1 == f2:
        logger.info('dest is identical to src: '+f1)
        return
    if os.path.exists(f2):
        ans = raw_input('dest file already exists: '+f2+'. Replace? (y/n) ')
        if ans != 'y':
            return

    if copy:
        cmd = u'cp {} {}'.format(f1, f2)
        logger.info(cmd)
        if not DRYRUN:
            shutil.copy(f1, f2)
    else:
        cmd = u'mv {} {}'.format(f1, f2)
        logger.info(cmd)
        if not DRYRUN:
            shutil.move(f1, f2)
