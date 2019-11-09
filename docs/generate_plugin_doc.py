#!/usr/bin/env python
#
# This script walks through all plugin files and
# extracts documentation that should go into the
# reference manual

import os
import re


def findOrderID(filename):
    f = open(filename)
    for line in f.readlines():
        match = re.match(r'.*\\order{([^}]*)}.*', line)
        if match is not None:
            return int(match.group(1))
    return 1000


def extract(target, filename):
    f = open(filename)
    inheader = False
    for line in f.readlines():
        match = re.match(r'^/\*! ?(.*)$', line)
        if match is not None:
            print("Processing %s" % filename)
            line = match.group(1).replace('%', '\%')
            target.write(line + '\n')
            inheader = True
            continue
        if not inheader:
            continue
        if re.search(r'^[\s\*]*\*/$', line):
            inheader = False
            continue
        target.write(line)
    f.close()

# Traverse source directories and process any found plugin code


def process(path, target):
    def capture(fileList, dirname, files):
        suffix = os.path.split(dirname)[1]
        if 'lib' in suffix or suffix == 'tests' \
                or suffix == 'mitsuba' or suffix == 'utils' \
                or suffix == 'converter' or suffix == 'mtsgui':
            return
        for filename in files:
            if '.cpp' == os.path.splitext(filename)[1]:
                fname = os.path.join(dirname, filename)
                fileList += [fname]

    fileList = []
    for (dirname, _, files) in os.walk(path):
        capture(fileList, dirname, files)

    ordering = [(findOrderID(fname), fname) for fname in fileList]
    ordering = sorted(ordering, key=lambda entry: entry[0])

    for entry in ordering:
        extract(target, entry[1])


def process_src(target, src_subdir, section=None):
    if section is None:
        section = "section_" + src_subdir

    # Copy paste the contents of the appropriate section file
    with open(section + '.rst', 'r') as f:
        target.write(f.read())
    process('../src/{0}'.format(src_subdir), target)


def generate(build_dir):
    original_wd = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(build_dir, 'plugins.rst'), 'w') as f:
        # process_src(f, 'shapes')
        process_src(f, 'bsdfs', 'section_bsdf')
        # process_src(f, 'textures')
        # process_src(f, 'subsurface')
        # process_src(f, 'medium', 'section_media')
        # process_src(f, 'phase')
        # process_src(f, 'volume', 'section_volumes')
        # process_src(f, 'emitters')
        # process_src(f, 'sensors')
        # process_src(f, 'integrators')
        # process_src(f, 'samplers')
        # process_src(f, 'films')
        # process_src(f, 'rfilters')

    os.chdir(original_wd)
    
if __name__ == "__main__":
    generate()