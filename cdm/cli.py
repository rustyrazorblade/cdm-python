"""cdm - Cassandra Data Manager

Usage:
    cdm search [<term>]
    cdm list [<term>]
    cdm show <dataset>
    cdm install [--host=<host>] [--keyspace=<keyspace>] [--nocassandra] [--graph] [--search] [--noupdate] <dataset>
    cdm update
    cdm tutorials <dataset>
    cdm new <dataset>
    cdm check

Options:
    --debug

Examples:
    cdm install demo

"""

# for the future - cdm web & cdm stream

import sys

from subprocess import Popen

sys.path.append("")
import os
import os.path
from ConfigParser import SafeConfigParser
import logging

# 3rd party

from docopt import docopt
from cdm.util import *

# allow for schema management fun
os.environ['CQLENG_ALLOW_SCHEMA_MANAGEMENT'] = "1"

# set up logging to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
# formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# console.setFormatter(formatter)
# add the handler to the root logger
root_logger = logging.getLogger('')
root_logger.setLevel(logging.INFO)


def main():
    arguments = docopt(__doc__)

    try:
        os.mkdir(CDM_CACHE)
    except OSError:
        pass


    if arguments["search"] or arguments["list"]:
        return list_datasets(arguments["<term>"])

    if arguments["update"]:
        return update_datasets()

    if arguments["install"]:
        tmp = arguments["<dataset>"].split("==")

        if len(tmp) == 1:
            tmp.append("master")

        # get defaults
        cqlshrc = os.path.expanduser("~/.cassandra/cqlshrc")
        if os.path.exists(cqlshrc):
            parser = SafeConfigParser()
            parser.read(cqlshrc)
            default_host = parser.get("connection", "hostname")
            default_port = parser.get("connection", "port")
        else:
            default_host = "localhost"

        host = arguments.get("--host") or default_host
        return install(tmp[0], tmp[1],
                       install_cassandra=not arguments['--nocassandra'],
                       install_graph=arguments['--graph'],
                       install_search=arguments['--search'],
                       host=host)



    if arguments["show"]:
        return show_dataset_details(arguments["<dataset>"])

    if arguments["tutorials"]:
        # move into the tutorial directory

        if arguments["<dataset>"] == ".":
            os.chdir("tutorials")
        else:
            dest = os.path.join(CDM_CACHE,
                                "tutorials",
                                arguments["<dataset>"])
            os.chdir(dest)

        if sys.platform.startswith('win'):
            p = Popen(["jupyter-notebook"], shell=True)
            # Don't raise KeyboardInterrupt in the parent process.
            # Set this after spawning, to avoid subprocess inheriting handler.
            import signal
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            p.wait()
            sys.exit(p.returncode)
        else:
            os.execvp("jupyter-notebook", ['notebook'])

    print "Done"




if __name__ == "__main__":
    main()
