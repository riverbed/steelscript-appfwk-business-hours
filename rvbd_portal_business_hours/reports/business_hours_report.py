# -*- coding: utf-8 -*-
# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the
# MIT License set forth at:
#   https://github.com/riverbed/flyscript-portal/blob/master/LICENSE ("License").
# This software is distributed "AS IS" as set forth in the License.
from rvbd_portal.apps.datasource.modules.analysis import AnalysisTable

from rvbd_portal.apps.report.models import Report, Section
import rvbd_portal.apps.report.modules.yui3 as yui3
from rvbd_portal.apps.datasource.modules import analysis
from rvbd_portal.libs.fields import Function
import rvbd_portal.libs.profiler_tools as protools

from rvbd_portal_profiler.datasources import profiler
from rvbd_portal_profiler.datasources import profiler_devices

import rvbd_portal_business_hours.libs.business_hours as bizhours
from rvbd_portal_profiler.datasources.profiler import ProfilerGroupbyTable
from rvbd_portal_profiler.datasources.profiler_devices import \
    ProfilerDeviceTable

report = Report(title="Business Hour Reporting - Profiler Interfaces", position=9,
                field_order=['endtime', 'duration', 'profiler_filterexpr',
                             'business_hours_start', 'business_hours_end',
                             'business_hours_tzname', 'business_hours_weekends'],
                hidden_fields=['resolution'])
report.save()

section = Section.create(report)

#
# Define by-interface table from Profiler
#
basetable = ProfilerGroupbyTable.create('bh-basetable', groupby='interface',
                                        duration=60,
                                        resolution=3600, interface=True)

# Define all of your columns here associated with basetable
# For each data column (iskey=False), you must specify the aggregation method
# in the bizhours.create below.
basetable.add_column('interface_dns', 'Interface', iskey=True,
                     datatype="string")
basetable.add_column('interface_alias', 'Ifalias', iskey=True,
                     datatype="string")
basetable.add_column('avg_util', '% Utilization', units='pct',
                     issortcol=True)
basetable.add_column('in_avg_util', '% Utilization In', units='pct',
                     issortcol=False)
basetable.add_column('out_avg_util', '% Utilization Out', units='pct',
                     issortcol=False)

# The 'aggregate' parameter describes how similar rows on different business
# days should be combined.  For example:
#
#     Day    Total Bytes   Avg Bytes/s
# ---------  ------------  -----------
#     Mon    28MB            100
#     Tue    56MB            200
# ========== ============= ===========
# Combined   84MB            150
# Method     sum             avg
#
# Common methods:
#   sum    - just add up all the data, typical for totals
#   avg    - compute average (using time as a weight), for anything "average"
#   min    - minimum of all values
#   max    - maximum of all values
#
biztable = bizhours.create('bh-biztable', basetable,
                           aggregate={'avg_util': 'avg',
                                      'in_avg_util': 'avg',
                                      'out_avg_util': 'avg'})

# Device Table

devtable = ProfilerDeviceTable.create('devtable')
devtable.add_column('ipaddr', 'Device IP', iskey=True,
                    datatype="string")
devtable.add_column('name', 'Device Name', datatype="string")
devtable.add_column('type', 'Flow Type', datatype="string")
devtable.add_column('version', 'Flow Version', datatype="string")

interfaces = AnalysisTable.create('bh-interfaces', tables={'devices': devtable,
                                                           'traffic': biztable},
                                  function=protools.process_join_ip_device)

interfaces.add_column('interface_name', 'Interface', iskey=True,
                      datatype="string")
interfaces.copy_columns(biztable, except_columns=['interface_dns'])

yui3.TableWidget.create(section, interfaces, "Interface", height=600)
yui3.BarWidget.create(section, interfaces, "Interface Utilization", height=600,
                      keycols=['interface_name'], valuecols=['avg_util'])

yui3.TableWidget.create(section, bizhours.get_timestable(biztable), "Covered times",
                        width=12, height=200)
