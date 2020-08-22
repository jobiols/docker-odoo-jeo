# setup.py for hashlib standalone for Python versions < 2.5
#

__version__ = "20081119"

import sys, os, re

from distutils.core import setup, Extension
from distutils.ccompiler import new_compiler


# additional paths to check, set from the command line
SSL_INCDIR=''   # --openssl-incdir=
SSL_LIBDIR=''   # --openssl-libdir=
SSL_DIR=''      # --openssl-prefix=


def add_dir_to_list(dirlist, dir):
    """Add the directory 'dir' to the list 'dirlist' (at the front) if
    'dir' actually exists and is a directory.  If 'dir' is already in
    'dirlist' it is moved to the front."""
    if dir is not None and os.path.isdir(dir) and dir not in dirlist:
        if dir in dirlist:
            dirlist.remove(dir)
        dirlist.insert(0, dir)


def prepare_hashlib_Extensions():
    """Decide which C extensions to build and create the appropriate
    Extension objects to build them.  Returns a list of Extensions."""

    # this CCompiler object is only used to locate include files
    compiler = new_compiler()

    # Ensure that these paths are always checked
    if os.name == 'posix':
        add_dir_to_list(compiler.library_dirs, '/usr/local/lib')
        add_dir_to_list(compiler.include_dirs, '/usr/local/include')

        add_dir_to_list(compiler.library_dirs, '/usr/local/ssl/lib')
        add_dir_to_list(compiler.include_dirs, '/usr/local/ssl/include')

        add_dir_to_list(compiler.library_dirs, '/usr/contrib/ssl/lib')
        add_dir_to_list(compiler.include_dirs, '/usr/contrib/ssl/include')

        add_dir_to_list(compiler.library_dirs, '/usr/lib')
        add_dir_to_list(compiler.include_dirs, '/usr/include')

    # look in command line supplied paths
    if SSL_LIBDIR:
        add_dir_to_list(compiler.library_dirs, SSL_LIBDIR)
    if SSL_INCDIR:
        add_dir_to_list(compiler.include_dirs, SSL_INCDIR)
    if SSL_DIR:
        if os.name == 'nt':
            add_dir_to_list(compiler.library_dirs, os.path.join(SSL_DIR, 'out32dll'))
            # prefer the static library
            add_dir_to_list(compiler.library_dirs, os.path.join(SSL_DIR, 'out32'))
        else:
            add_dir_to_list(compiler.library_dirs, os.path.join(SSL_DIR, 'lib'))
        add_dir_to_list(compiler.include_dirs, os.path.join(SSL_DIR, 'include'))

    osNameLibsMap = {
        'posix':  ['ssl', 'crypto'],
        'nt':     ['libeay32',  'gdi32', 'advapi32', 'user32'],
    }
    if not osNameLibsMap.has_key(os.name):
        print "unknown OS, please update setup.py"
        sys.exit(1)

    exts = []

    ssl_inc_dirs = []
    ssl_incs = []
    for inc_dir in compiler.include_dirs:
        f = os.path.join(inc_dir, 'openssl', 'ssl.h')
        if os.path.exists(f):
            ssl_incs.append(f)
            ssl_inc_dirs.append(inc_dir)

    ssl_lib = compiler.find_library_file(compiler.library_dirs, osNameLibsMap[os.name][0])

    # find out which version of OpenSSL we have
    openssl_ver = 0
    openssl_ver_re = re.compile(
        '^\s*#\s*define\s+OPENSSL_VERSION_NUMBER\s+(0x[0-9a-fA-F]+)' )
    ssl_inc_dir = ''
    for ssl_inc_dir in ssl_inc_dirs:
        name = os.path.join(ssl_inc_dir, 'openssl', 'opensslv.h')
        if os.path.isfile(name):
            try:
                incfile = open(name, 'r')
                for line in incfile:
                    m = openssl_ver_re.match(line)
                    if m:
                        openssl_ver = eval(m.group(1))
                        break
            except IOError:
                pass

        # first version found is what we'll use
        if openssl_ver:
            break

    if (ssl_inc_dir and
        ssl_lib is not None and
        openssl_ver >= 0x00907000):

        print 'Using OpenSSL version 0x%08x from' % openssl_ver
        print ' Headers:\t', ssl_inc_dir
        print ' Library:\t', ssl_lib

        # The _hashlib module wraps optimized implementations
        # of hash functions from the OpenSSL library.
        exts.append( Extension('_hashlib', ['_hashopenssl.c'],
                               include_dirs = [ ssl_inc_dir ],
                               library_dirs = [ os.path.dirname(ssl_lib) ],
                               libraries = osNameLibsMap[os.name]) )
    else:
        exts.append( Extension('_sha', ['shamodule.c']) )
        exts.append( Extension('_md5', 
                        sources = ['md5module.c', 'md5.c'],
                        depends = ['md5.h']) )

    if (not ssl_lib or openssl_ver < 0x00908000):
        # OpenSSL doesn't do these until 0.9.8 so we'll bring our own
        exts.append( Extension('_sha256', ['sha256module.c']) )
        exts.append( Extension('_sha512', ['sha512module.c']) )

    def prependModules(filename):
        return os.path.join('Modules', filename)

    # all the C code is in the Modules subdirectory, prepend the path
    for ext in exts:
        ext.sources = [ prependModules(fn) for fn in ext.sources ]
        if hasattr(ext, 'depends') and ext.depends is not None:
            ext.depends = [ prependModules(fn) for fn in ext.depends ]

    return exts


# do the actual build, install, whatever...
def main():
    if sys.version >= (2,5):
        print "You do not need to build hashlib, it comes standard with Python >= 2.5"
        sys.exit(1)

    # parse command line for --openssl=path
    global SSL_INCDIR, SSL_LIBDIR, SSL_DIR
    for arg in sys.argv[:]:
        if arg.startswith('--openssl-incdir='):
            SSL_INCDIR = arg.split('=')[1]
            sys.argv.remove(arg)
        if arg.startswith('--openssl-libdir='):
            SSL_LIBDIR = arg.split('=')[1]
            sys.argv.remove(arg)
        if arg.startswith('--openssl-prefix='):
            SSL_DIR = arg.split('=')[1]
            sys.argv.remove(arg)

    setup(
      name =        'hashlib',
      version =     __version__,
      description = 'Secure hash and message digest algorithm library',
      long_description = """\
This is a stand alone packaging of the hashlib
library introduced in Python 2.5 so that it can
be used on older versions of Python.""",
      license = "PSF license",

      maintainer = "Gregory P. Smith",
      maintainer_email = "greg at krypto dot org",
      url = 'http://code.krypto.org/python/hashlib/',

      ext_modules = prepare_hashlib_Extensions(),

      py_modules = [ 'hashlib' ],
    )

if __name__ == '__main__':
    main()
