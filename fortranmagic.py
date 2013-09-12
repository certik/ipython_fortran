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
                if cell.startswith("use"):
                    # put "implicit none" below all "use" lines:
                    source = []
                    c = cell.split("\n")
                    line = c[0]; del c[0]
                    while line.startswith("use"):
                        source.append(line)
                        line = c[0]; del c[0]
                    source.append("implicit none")
                    source.append(line)
                    source.extend(c)
                    source = "\n".join(source) + "\nend"
                else:
                    source = "implicit none\n" + cell + "\nend"

            implicit_modules = """\
module types
implicit none
private
public dp
integer, parameter :: dp=kind(0.d0)          ! double precision
end module

module constants
use types, only: dp
implicit none
private
public pi, e_, i_

! Constants contain more digits than double precision, so that
! they are rounded correctly. Single letter constants contain underscore so
! that they do not clash with user variables ("e" and "i" are frequently used as
! loop variables)
real(dp), parameter :: pi    = 3.1415926535897932384626433832795_dp
real(dp), parameter :: e_    = 2.7182818284590452353602874713527_dp
complex(dp), parameter :: i_ = (0, 1)
end module
"""
            source = implicit_modules + source

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
                print("*** FAILED TO COMPILE ***")
                return

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
