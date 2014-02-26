# -*- coding: utf-8 -*-
# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the
# MIT License set forth at:
#   https://github.com/riverbed/flyscript-portal/blob/master/LICENSE ("License").
# This software is distributed "AS IS" as set forth in the License.

from rvbd_portal.apps.report.models import Report, Section
import rvbd_portal.apps.report.modules.yui3 as yui3
from rvbd_portal.apps.datasource.modules import analysis
import rvbd_portal.libs.profiler_tools as protools

from rvbd_portal_profiler.datasources import profiler
from rvbd_portal_profiler.datasources import profiler_devices

import rvbd_portal_business_hours.libs.business_hours as bizhours

report = Report(title="Business Hour Reporting - Profiler Interfaces", position=9,
                field_order=['endtime', 'duration', 'profiler_filterexpr',
                             'business_hours_start', 'business_hours_end',
                             'business_hours_tzname', 'business_hours_weekends'],
                hidden_fields=['resolution'])
report.save()

section = Section.create(report)

bizhours.fields_add_business_hour_fields(section)

#
# Define by-interface table from Profiler
#
basetable = profiler.create_groupby_table('bh-basetable', 'interface',
                                          duration=60,
                                          resolution=3600, interface=True)

# Define all of your columns here associated with basetable
# For each data column (iskey=False), you must specify the aggreation method
# in the bizhours.create below.
profiler.column(basetable, 'interface_dns', 'Interface', iskey=True,
                isnumeric=False)
profiler.column(basetable, 'interface_alias', 'Ifalias', iskey=True,
                isnumeric=False)
profiler.column(basetable, 'avg_util', '% Utilization', datatype='pct',
                issortcol=True)
profiler.column(basetable, 'in_avg_util', '% Utilization In', datatype='pct',
                issortcol=False)
profiler.column(basetable, 'out_avg_util', '% Utilization Out', datatype='pct',
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
bustable_pre = bizhours.create('bh-bustable-pre', basetable,
                               aggregate={'avg_util': 'avg',
                                          'in_avg_util': 'avg',
                                          'out_avg_util': 'avg'})

# Device Table

devtable = profiler_devices.create_table('devtable')
profiler_devices.column(devtable, 'ipaddr', 'Device IP', iskey=True,
                        isnumeric=False)
profiler_devices.column(devtable, 'name', 'Device Name', isnumeric=False)
profiler_devices.column(devtable, 'type', 'Flow Type', isnumeric=False)
profiler_devices.column(devtable, 'version', 'Flow Version', isnumeric=False)

bustable = analysis.create_table('bh-bustable', tables={'devices': devtable.id,
                                                        'traffic': bustable_pre.id},
                                 func=protools.process_join_ip_device)

analysis.column(bustable, 'interface_name', 'Interface', iskey=True,
                isnumeric=False)
bustable.copy_columns(bustable_pre, except_columns=['interface_dns'])

yui3.TableWidget.create(section, bustable, "Interface", height=600)
yui3.BarWidget.create(section, bustable, "Interface Utilization", height=600,
                      keycols=['interface_name'], valuecols=['avg_util'])
yui3.TableWidget.create(section, bizhours.timestable(), "Covered times",
                        width=12, height=200)
