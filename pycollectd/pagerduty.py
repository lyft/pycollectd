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
Collectd plugin for sending notifications via PagerDuty
(http://www.pagerduty.com/)
"""
from __future__ import absolute_import
from pygerduty import PagerDuty
import collectd
from pycollectd.plugin import CollectDPlugin, PluginError


class PagerDutyNotifier(CollectDPlugin):
    """
    Collectd plugin for sending notifications to PagerDuty.
    """
    def configure(self, config, **kwargs):
        """
        Ensure the required configuration options are set in collectd's config.
        """
        super(PagerDutyNotifier, self).configure(config, **kwargs)

        for key in ('APIKey', 'Subdomain',
                    'WarningServiceKey', 'FailureServiceKey'):
            if key not in self.config.keys():
                message = 'Required configuration key %s missing!' % key
                self.error(message)
                raise PluginError(message)

    def initialize(self):
        """
        Set up the PagerDuty API client and add the notification callback.
        """
        self.pager = PagerDuty(self.config['Subdomain'], self.config['APIKey'])
        self.service_keys = dict((
            (collectd.NOTIF_FAILURE, self.config['FailureServiceKey']),
            (collectd.NOTIF_WARNING, self.config['WarningServiceKey']),
        ))

        self.add_notification_callback(self.notify)

    def services(self, trigger_type, severity):
        """
        Return the service keys to send the event to. For trigger events, this
        is a 1-item list containing the configured service key for the
        given severity. For resolve events, this is a list of all service
        keys, because we need to ensure the event is resolved everywhere it
        was triggered.
        """
        if trigger_type == 'resolve':
            keys = self.service_keys.values()
        else:
            keys = [self.service_keys[severity]]

        return keys

    def notify(self, notification):
        """
        Send the notification to PagerDuty.
        """
        # Use a friendly string instead of a number.
        severity = {
            collectd.NOTIF_FAILURE: 'FAILURE',
            collectd.NOTIF_WARNING: 'WARNING',
            collectd.NOTIF_OKAY: 'OKAY',
        }.get(notification.severity)

        # Short description - this ends up in SMS and email subject, so
        # keep it short!
        description = '%s on %s (from %s plugin)' % (
            severity,
            notification.host,
            notification.plugin,
        )

        # This is the details of the incident, will end up in the email
        # body and the PagerDuty interface. Go crazy.
        details = {
            'host': notification.host,
            'plugin': notification.plugin,
            'plugin_instance': notification.plugin_instance,
            'type': notification.type,
            'type_instance': notification.type_instance,
            'message': notification.message,
            'severity': severity,
        }

        # We construct an incident key from any of these components that
        # are not None.
        components = filter(None, [
            notification.host,
            notification.plugin,
            notification.plugin_instance,
            notification.type,
            notification.type_instance,
        ])
        incident_key = '.'.join(components)

        # Figure out what kind of trigger this is.
        trigger_type = {
            collectd.NOTIF_FAILURE: 'trigger',
            collectd.NOTIF_WARNING: 'trigger',
            collectd.NOTIF_OKAY: 'resolve',
        }.get(notification.severity)

        # Finally, trigger the event in PagerDuty
        service_keys = self.services(trigger_type, notification.severity)

        for service in service_keys:
            self.info('Triggering %r event in PagerDuty service %s: %r' %
                      (trigger_type, service, details))
            self.pager.create_event(
                service,
                description,
                trigger_type,
                details,
                incident_key
            )


# We have to call the constructor in order to actually register our plugin
# with collectd.
PAGERDUTY = PagerDutyNotifier('notifier')
