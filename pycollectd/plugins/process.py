# -*- coding: utf-8 -*-
#
# © 2013 Lyft, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.  You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Process monitoring plugins for pycollectd.
"""
# Standard Library Imports
from __future__ import absolute_import

# Other Library Imports
from collectd import Values
from procfs import Proc
from procfs.exceptions import DoesNotExist, UnknownProcess

# Internal Library Imports
from pycollectd.plugin import CollectDPlugin


class ProcessMemoryPlugin(CollectDPlugin):
    """
    Monitor process memory usage.

    This plugin is intended to be subclassed.
    """
    def __init__(self, name):
        super(ProcessMemoryPlugin, self).__init__(name)
        self.procfs = Proc()
        self.add_read_callback(self.read_memory)

    @property
    def processes(self):
        """
        Subclasses must over-ride this to return a list of processes to sample.
        """
        raise NotImplemented

    def read_memory(self):
        """
        Called by collectd to gather memory metrics from the processes.
        """
        # Get the procfs status information for each process.
        #
        # Done in a loop instead of a comprehension because we need to handle
        # the case where one of these processes is no longer alive, which will
        # cause a DoesNotExist exception.
        statuses = []
        for process in self.processes:
            try:
                statuses.append(process.status)
            except (DoesNotExist, UnknownProcess):
                # Process is no longer running.
                continue

        # Dispatch metrics for each worker.
        for idx, status in enumerate(statuses):
            try:
                vmsize = Values(
                    plugin_instance='vmsize',
                    values=(status['VmSize'],),
                )

                vmrss = Values(
                    plugin_instance='vmrss',
                    values=(status['VmRSS'],),
                )
            except (DoesNotExist, UnknownProcess):
                # Process is no longer running.
                continue

            for metric in (vmsize, vmrss):
                metric.dispatch(
                    plugin=self.name,
                    type='gauge',
                    type_instance=str(idx),
                )
