# -*- coding: utf-8 -*-

from __future__ import print_function

import imp
import io
import os
import re
import sys
import time
from tempfile import mkdtemp
from shutil import rmtree


try:
    reload
except NameError:   # Python 3
    from imp import reload

try:
    import hashlib
except ImportError:
    import md5 as hashlib

from distutils.core import Distribution, Extension
from distutils.command.build_ext import build_ext

from IPython.core import display
from IPython.core import magic_arguments
from IPython.core.magic import Magics, magics_class, cell_magic
from IPython.utils import py3compat
from IPython.utils.process import get_output_error_code
from IPython.utils.path import get_ipython_cache_dir


@magics_class
class FortranMagics(Magics):

    def __init__(self, shell):
        super(FortranMagics, self).__init__(shell)

    @cell_magic
    def fortran(self, line, cell):
        """Compile and run a Fortran code cell.
        """
        path = mkdtemp(prefix="fortranmagic_")
        try:
            #print("work dir: %s" % path)
            filename = os.path.join(path, "a.f90")
            if cell.startswith("program") or cell.startswith("module"):
                # The whole program is supplied, don't touch it:
                source = cell
            else:
                # Fortran lines are supplied directly, make it a valid
                # Fortran code:
                source = "implicit none\n" + cell + "\nend"
            with open(filename, "w") as f:
                f.write(source)

            # Compile
            out, err, code = get_output_error_code('cd %s; gfortran -Wall -Wextra -Wimplicit-interface -fPIC -g -fcheck=all -fbacktrace a.f90' % \
                    path)
            if out != "":
                print("out:")
                print(out)
            if err != "":
                print("err:")
                print(err)
            if code != 0:
                raise Exception("Failed to compile")

            # Run
            out, err, code = get_output_error_code('cd %s; ./a.out' % path)
            if out != "":
                print(out)
            if err != "":
                print("err:")
                print(err)
            if code != 0:
                print("Non-zero exit code: %d" % code)
        finally:
            rmtree(path)

def load_ipython_extension(ip):
    """Load the extension in IPython."""
    ip.register_magics(FortranMagics)
