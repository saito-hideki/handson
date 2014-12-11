#!/bin/sh

source ./openrc

function get_uuid () { cat - | grep " id " | awk '{print $4}'; }
export OS_DMZ_NET=`neutron net-show dmz-net | get_uuid`
export OS_APP_NET=`neutron net-show app-net | get_uuid`
export OS_DBS_NET=`neutron net-show dbs-net | get_uuid`

env | grep "^OS.*_NET"

#
# [EOF]
#
