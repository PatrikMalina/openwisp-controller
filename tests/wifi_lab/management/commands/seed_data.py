import os

from django.core.files import File
from django.core.management.base import BaseCommand
from swapper import load_model

from script_manager.models import ScriptRecord


class Command(BaseCommand):
    help = "Seed the database with initial data."

    def handle(self, *args, **kwargs):
        path_to_file = 'media/fake_traffic_with_reconnect.sh'
        if not os.path.exists(path_to_file):
            raise FileNotFoundError(f"{path_to_file} does not exist")

        with open(path_to_file, 'rb') as f:
            django_file = File(f)

            record = ScriptRecord(
                name='Traffic with constant reconnect',
                description='This script simulates traffic and reconnects to designated SSID'
            )
            record.file.save('fake_traffic_with_reconnect.sh', django_file, save=True)

        path_to_file = 'media/lab_capture.sh'
        if not os.path.exists(path_to_file):
            raise FileNotFoundError(f"{path_to_file} does not exist")

        with open(path_to_file, 'rb') as f:
            django_file = File(f)
            record = ScriptRecord.objects.create(
                name='Wifi capture on SSID: LabCapture',
                description='Script connects to wifi network LabCapture and does analyzation of network and creates .pcap file',

            )

            record.file.save('lab_capture.sh', django_file, save=True)

        templates = [
            {
                'name': 'WEP configuration',
                'backend': 'netjsonconfig.OpenWrt',
                'config': {
                    "radios": [],
                    "interfaces": [
                        {
                            "wireless": {
                                "network": ["lan"],
                                "mode": "access_point",
                                "radio": "radio0",
                                "ack_distance": 0,
                                "rts_threshold": 0,
                                "frag_threshold": 0,
                                "ssid": "LabWEP",
                                "hidden": False,
                                "wds": False,
                                "encryption": {
                                    "protocol": "wep_open",
                                    "key": "1234567890",
                                    "disabled": False
                                },
                                "wmm": True,
                                "isolate": False,
                                "ieee80211r": False,
                                "reassociation_deadline": 1000,
                                "ft_psk_generate_local": False,
                                "ft_over_ds": True,
                                "rsn_preauth": False,
                                "macfilter": "disable",
                                "maclist": []
                            },
                            "type": "wireless",
                            "name": "lab_wep",
                            "mtu": 1500,
                            "disabled": False,
                            "network": "lan",
                            "mac": "",
                            "autostart": True,
                            "addresses": []
                        }
                    ]
                }
            },
            {
                'name': 'WPA2 LabCapture',
                'backend': 'netjsonconfig.OpenWrt',
                'config': {
                    "interfaces": [
                        {
                            "wireless": {
                                "network": ["lan"],
                                "mode": "access_point",
                                "radio": "radio0",
                                "ack_distance": 0,
                                "rts_threshold": 0,
                                "frag_threshold": 0,
                                "ssid": "LabCapture",
                                "hidden": False,
                                "wds": False,
                                "encryption": {
                                    "protocol": "wpa2_personal",
                                    "key": "labcapture1",
                                    "disabled": False,
                                    "cipher": "auto",
                                    "ieee80211w": "0"
                                },
                                "wmm": True,
                                "isolate": False,
                                "ieee80211r": False,
                                "reassociation_deadline": 1000,
                                "ft_psk_generate_local": False,
                                "ft_over_ds": True,
                                "rsn_preauth": False,
                                "macfilter": "disable",
                                "maclist": []
                            },
                            "type": "wireless",
                            "name": "LabCapture",
                            "mtu": 1500,
                            "disabled": False,
                            "network": "lan",
                            "mac": "",
                            "autostart": True,
                            "addresses": []
                        }
                    ]
                }
            },
            {
                'name': 'Dual Guest wifi',
                'backend': 'netjsonconfig.OpenWrt',
                'config': {
                    "interfaces": [
                        {
                            "wireless": {
                                "network": ["lan"],
                                "mode": "access_point",
                                "radio": "radio0",
                                "ack_distance": 0,
                                "rts_threshold": 0,
                                "frag_threshold": 0,
                                "ssid": "Dual",
                                "hidden": False,
                                "wds": False,
                                "encryption": {
                                    "protocol": "wpa2_personal",
                                    "key": "openwisp",
                                    "disabled": False,
                                    "cipher": "auto",
                                    "ieee80211w": "0"
                                },
                                "wmm": True,
                                "isolate": True,
                                "ieee80211r": False,
                                "reassociation_deadline": 1000,
                                "ft_psk_generate_local": False,
                                "ft_over_ds": True,
                                "rsn_preauth": False,
                                "macfilter": "disable",
                                "maclist": []
                            },
                            "type": "wireless",
                            "name": "wdual1",
                            "mtu": 1500,
                            "disabled": False,
                            "network": "lan",
                            "mac": "",
                            "autostart": True,
                            "addresses": []
                        },
                        {
                            "wireless": {
                                "network": ["lan"],
                                "mode": "access_point",
                                "radio": "radio1",
                                "ack_distance": 0,
                                "rts_threshold": 0,
                                "frag_threshold": 0,
                                "ssid": "Dual",
                                "hidden": False,
                                "wds": False,
                                "encryption": {
                                    "protocol": "wpa2_personal",
                                    "key": "openwisp",
                                    "disabled": False,
                                    "cipher": "auto",
                                    "ieee80211w": "0"
                                },
                                "wmm": True,
                                "isolate": True,
                                "ieee80211r": False,
                                "reassociation_deadline": 1000,
                                "ft_psk_generate_local": False,
                                "ft_over_ds": True,
                                "rsn_preauth": False,
                                "macfilter": "disable",
                                "maclist": []
                            },
                            "type": "wireless",
                            "name": "wdual2",
                            "mtu": 1500,
                            "disabled": False,
                            "network": "lan",
                            "mac": "",
                            "autostart": True,
                            "addresses": []
                        }
                    ]
                }
            },
            {
                'name': 'WP2 for deauthentication',
                'backend': 'netjsonconfig.OpenWrt',
                'config': {
                    "interfaces": [
                        {
                            "wireless": {
                                "network": ["lan"],
                                "mode": "access_point",
                                "radio": "radio0",
                                "ack_distance": 0,
                                "rts_threshold": 0,
                                "frag_threshold": 0,
                                "ssid": "DeauthTest",
                                "hidden": False,
                                "wds": False,
                                "encryption": {
                                    "protocol": "wpa2_personal",
                                    "key": "openwisp",
                                    "disabled": False,
                                    "cipher": "auto",
                                    "ieee80211w": "0"
                                },
                                "wmm": True,
                                "isolate": False,
                                "ieee80211r": False,
                                "reassociation_deadline": 1000,
                                "ft_psk_generate_local": False,
                                "ft_over_ds": True,
                                "rsn_preauth": False,
                                "macfilter": "disable",
                                "maclist": []
                            },
                            "type": "wireless",
                            "name": "deauth",
                            "mtu": 1500,
                            "disabled": False,
                            "network": "lan",
                            "mac": "",
                            "autostart": True,
                            "addresses": []
                        }
                    ]
                }
            }
        ]

        Template = load_model('config', 'Template')

        for t in templates:
            Template.objects.update_or_create(
                name=t['name'],
                defaults={
                    'backend': t['backend'],
                    'config': t['config'],
                    'type': 'generic',
                    'default': False,
                    'auto_cert': False,
                    'organization': None,
                    'vpn': None,
                    'default_values': {},
                    'required': False,
                }
            )
