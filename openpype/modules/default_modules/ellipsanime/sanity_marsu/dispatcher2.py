import os, re, sys
import imp
from collections import OrderedDict

SANITY_CHECKS_MAPPING = os.path.join(os.path.dirname(__file__), "sanity-checks-mapping.txt")
COMMENT_REGEX = re.compile(r'\s*[#;]')


def _parse_mapping_file():
    """ Parse the "mapping" file, which consist of a text file with
        regular expressions followed by an indented list of sanity
        check module names.
        - A line starting with a "non-space" character is considered as a regex.
        - The following indented lines (starting with a space character)
        are considered as SC module names to apply to the file if it matches
        the previous regex.
        - lines starting with `#` or `;` are ignored.
    """
    result = []

    print "#"*80
    print SANITY_CHECKS_MAPPING
    print

    with open(SANITY_CHECKS_MAPPING, 'r') as f:
        current_regex = None
        current_checks = []
        for line in f:
            if len(line) == 0 or line.isspace():
                # is an empty line
                continue
            if COMMENT_REGEX.match(line):
                # is a comment
                continue
            if not line[0].isspace():
                # is a regex
                result.append((current_regex, current_checks))
                current_regex = re.compile(line.rstrip())
                current_checks = []
            else:
                # is a sanity check name
                current_checks.append(line.strip())
        # remainder
        result.append((current_regex, current_checks))

    return result[1:]


def get_sanity_checks(filename, search_paths=[]):
    """ Load and return sanity check modules which match the given filename """
    modules = []
    filtered_checks = []

    # append current script directory to the paths to look for sanity checks
    search_paths.append(os.path.dirname(__file__))

    # read and parse the "mapping" text file
    mapping = _parse_mapping_file()

    # extract matching sanity checks
    for regex, sanity_checks in mapping:
        if regex.search(filename):
            filtered_checks.extend(sanity_checks)

    # remove duplicates
    refiltered_checks = OrderedDict.fromkeys(filtered_checks)

    # try to load corresponding modules
    for name in refiltered_checks:
        try:
            sys.stdout.write('loading {}...\n'.format(name))
            mod_data = imp.find_module(name, search_paths)
            mod = imp.load_module(name, *mod_data)
            if not hasattr(mod, 'check'):
                raise Exception('Missing `check` method'.format(name))
            modules.append(mod)
        except Exception as err:
            sys.stdout.write('{}: {}\n'.format(name, err))

    return modules


# TEST
if __name__ == '__main__':
    sc_list = get_sanity_checks('pipo__test__paf')
    print sc_list

""" TEST IN MAYA
import j_smurfs.sanity.dispatcher2

sanity_checks = j_smurfs.sanity.dispatcher2.get_sanity_checks('pif__std__paf')

for sc in sanity_checks:
    print format('==[ ' + sc.__name__ + ' ]', '=<80')
    sc.check()
print '=' * 80
"""