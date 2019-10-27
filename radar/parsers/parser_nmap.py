#  This file is part of RADAR.
#  Copyright (C) 2019 Cole Daubenspeck
#
#  RADAR is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  RADAR is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with RADAR.  If not, see <https://www.gnu.org/licenses/>.
from radar.objects import SystemCommand
import re

MODULE_NAME = "PARSE_NMAP"


def run(command: SystemCommand):
    target_list = []
    parse_results = {'targets': target_list}
    nmap_output = command.command_output.split('\n')

    for line in nmap_output:
        try:
            line = line.strip()

            if 'scan report for' in line:
                current_target = line.split(' ')[4]
                target_list.append({'target_host': current_target, "services": [], 'details': {}})

            elif 'Host is' in line:
                split_line = line.split(' ')
                target_list[len(target_list)-1]['details']['status'] = split_line[2]
                target_list[len(target_list)-1]['details']['latency'] = split_line[3][1:-1]

            elif '/tcp' or '/udp' in line:
                regex = '^(?P<port>[0-9]+)/(?P<protocol>[a-z]+)\s+(?P<state>.*?)(\s+(?P<service>.*))?$'
                matches = re.search(regex, line)
                if not matches:
                    continue
                info = {}
                port = matches.group('port')
                info['port'] = port
                protocol = matches.group('protocol')
                info['protocol'] = protocol
                state = matches.group('state')
                info['state'] = state
                service = matches.group('service')
                if service:
                    info['service'] = service
                target_list[len(target_list)-1]['services'].append(info)

            elif 'Network Distance' in line:
                hop_number = line.split(' ')[1]
                target_list[len(target_list)-1]['details']['hop_distance'] = hop_number

            elif 'MAC Address' in line:
                split_line = line.split(' ')
                mac_addr = split_line[1]
                target_list[len(target_list)-1]['details']['mac_address'] = mac_addr
                if len(split_line) > 2:
                    vendor = split_line[2]
                    target_list[len(target_list)-1]['details']['mac_address_vendor'] = vendor

            elif 'Nmap done' in line:
                regex = '^Nmap done: (?P<total_scanned>[0-9]+) IP address(es)?'\
                        '\((?P<total_online>[0-9]+).*?scanned in (?P<scan_duration>[0-9\.]+ .*)$'
                matches = re.search(regex, line)
                if not matches:
                    continue
                parse_results['total_scanned'] = matches.group('total_scanned')
                parse_results['total_online'] = matches.group('total_online')
                parse_results['scan_duration'] = matches.group('scan_duration')

        except IndexError:
            continue

    return parse_results, target_list
