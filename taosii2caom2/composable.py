# ***********************************************************************
# ******************  CANADIAN ASTRONOMY DATA CENTRE  *******************
# *************  CENTRE CANADIEN DE DONNÉES ASTRONOMIQUES  **************
#
#  (c) 2025.                            (c) 2025.
#  Government of Canada                 Gouvernement du Canada
#  National Research Council            Conseil national de recherches
#  Ottawa, Canada, K1A 0R6              Ottawa, Canada, K1A 0R6
#  All rights reserved                  Tous droits réservés
#
#  NRC disclaims any warranties,        Le CNRC dénie toute garantie
#  expressed, implied, or               énoncée, implicite ou légale,
#  statutory, of any kind with          de quelque nature que ce
#  respect to the software,             soit, concernant le logiciel,
#  including without limitation         y compris sans restriction
#  any warranty of merchantability      toute garantie de valeur
#  or fitness for a particular          marchande ou de pertinence
#  purpose. NRC shall not be            pour un usage particulier.
#  liable in any event for any          Le CNRC ne pourra en aucun cas
#  damages, whether direct or           être tenu responsable de tout
#  indirect, special or general,        dommage, direct ou indirect,
#  consequential or incidental,         particulier ou général,
#  arising from the use of the          accessoire ou fortuit, résultant
#  software.  Neither the name          de l'utilisation du logiciel. Ni
#  of the National Research             le nom du Conseil National de
#  Council of Canada nor the            Recherches du Canada ni les noms
#  names of its contributors may        de ses  participants ne peuvent
#  be used to endorse or promote        être utilisés pour approuver ou
#  products derived from this           promouvoir les produits dérivés
#  software without specific prior      de ce logiciel sans autorisation
#  written permission.                  préalable et particulière
#                                       par écrit.
#
#  This file is part of the             Ce fichier fait partie du projet
#  OpenCADC project.                    OpenCADC.
#
#  OpenCADC is free software:           OpenCADC est un logiciel libre ;
#  you can redistribute it and/or       vous pouvez le redistribuer ou le
#  modify it under the terms of         modifier suivant les termes de
#  the GNU Affero General Public        la “GNU Affero General Public
#  License as published by the          License” telle que publiée
#  Free Software Foundation,            par la Free Software Foundation
#  either version 3 of the              : soit la version 3 de cette
#  License, or (at your option)         licence, soit (à votre gré)
#  any later version.                   toute version ultérieure.
#
#  OpenCADC is distributed in the       OpenCADC est distribué
#  hope that it will be useful,         dans l’espoir qu’il vous
#  but WITHOUT ANY WARRANTY;            sera utile, mais SANS AUCUNE
#  without even the implied             GARANTIE : sans même la garantie
#  warranty of MERCHANTABILITY          implicite de COMMERCIALISABILITÉ
#  or FITNESS FOR A PARTICULAR          ni d’ADÉQUATION À UN OBJECTIF
#  PURPOSE.  See the GNU Affero         PARTICULIER. Consultez la Licence
#  General Public License for           Générale Publique GNU Affero
#  more details.                        pour plus de détails.
#
#  You should have received             Vous devriez avoir reçu une
#  a copy of the GNU Affero             copie de la Licence Générale
#  General Public License along         Publique GNU Affero avec
#  with OpenCADC.  If not, see          OpenCADC ; si ce n’est
#  <http://www.gnu.org/licenses/>.      pas le cas, consultez :
#                                       <http://www.gnu.org/licenses/>.
#
#  $Revision: 4 $
#
# ***********************************************************************
#

"""
Implements the default entry point functions for the workflow application.

'run' executes based on either provided lists of work, or files on disk.
'run_incremental' executes incrementally, usually based on time-boxed intervals.
"""

import logging
import sys
import traceback

from caom2pipe.client_composable import ClientCollection
from caom2pipe.data_source_composable import LocalFilesDataSourceRunnerMeta
from caom2pipe.manage_composable import Config, StorageName
from caom2pipe.run_composable import run_by_todo_runner_meta, run_by_state_runner_meta
from taosii2caom2 import main_app, file2caom2_augmentation


META_VISITORS = []
DATA_VISITORS = [file2caom2_augmentation]


def _common_init():
    config = Config()
    config.get_executors()
    StorageName.collection = config.collection
    StorageName.scheme = config.scheme
    StorageName.preview_scheme = config.preview_scheme
    StorageName.data_source_extensions = config.data_source_extensions
    clients = ClientCollection(config)
    sources = []
    if config.use_local_files:
        source = LocalFilesDataSourceRunnerMeta(config, clients.data_client, storage_name_ctor=main_app.TAOSIIName)
        sources.append(source)
    return clients, config, sources


def _run():
    """
    Uses a todo file to identify the work to be done.

    :return 0 if successful, -1 if there's any sort of failure.
    """
    clients, config, sources = _common_init()
    return run_by_todo_runner_meta(
        config=config,
        meta_visitors=META_VISITORS,
        data_visitors=DATA_VISITORS,
        sources=sources,
        clients=clients,
        organizer_module_name='taosii2caom2.main_app',
        organizer_class_name='TAOSIIOrganizeExecutesRunnerMeta',
        storage_name_ctor=main_app.TAOSIIName,
    )


def run():
    """Wraps _run in exception handling, with sys.exit calls."""
    try:
        result = _run()
        sys.exit(result)
    except Exception as e:
        logging.error(e)
        tb = traceback.format_exc()
        logging.debug(tb)
        sys.exit(-1)


def _run_incremental():
    """Uses a state file with a timestamp to kick off time-boxed entry processing.
    """
    clients, config, sources = _common_init()
    return run_by_state_runner_meta(
        config=config,
        meta_visitors=META_VISITORS,
        data_visitors=DATA_VISITORS,
        clients=clients,
        sources=sources,
        organizer_module_name='taosii2caom2.main_app',
        organizer_class_name='TAOSIIOrganizeExecutesRunnerMeta',
        storage_name_ctor=main_app.TAOSIIName,
    )


def run_incremental():
    """Wraps _run_state in exception handling."""
    try:
        _run_incremental()
        sys.exit(0)
    except Exception as e:
        logging.error(e)
        tb = traceback.format_exc()
        logging.debug(tb)
        sys.exit(-1)
