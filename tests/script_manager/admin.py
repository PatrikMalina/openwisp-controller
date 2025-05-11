from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import ScriptRecord

@admin.register(ScriptRecord)
class FileRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'file_button')
    search_fields = ('name', 'description')
    readonly_fields = ('validation_notice',)

    def validation_notice(self, _obj):
        return mark_safe(
            '''
            <div style="padding: 10px; background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; border-radius: 4px;">
                <strong>Note:</strong> We do not validate <b>.sh</b> files. Please upload valid files only.<br><br>
                <strong>Installed tools you can use inside of scripts:</strong>
                <pre style="white-space: pre-wrap; font-family: monospace;">
    Tool           Description
    -------------  ---------------------------------------------------------------
    net-tools      Legacy networking tools (ifconfig, netstat, etc.)
    iputils-ping   Basic connectivity testing (ping)
    traceroute     Traces the route packets take to a host
    dnsutils       DNS tools like dig, nslookup
    mtr            Combines ping and traceroute in real-time
    iw             Configure and get info about wireless devices
    wireless-tools Legacy Wi-Fi tools (iwconfig, iwlist)
    macchanger     Change/spoof MAC address of network interfaces
    tcpdump        Powerful packet sniffer for terminal
    tshark         Terminal version of Wireshark (packet analyzer)
    iftop          Real-time bandwidth usage per interface and IP
    vnstat         Network traffic monitoring over time (persistent)
    aircrack-ng    Wi-Fi security toolkit (deauth, cracking, sniffing)
    arp-scan       LAN scanner using ARP packets
    iperf3         Network bandwidth/throughput testing between two hosts
                </pre>
            </div>
            '''
        )

    validation_notice.short_description = "Notice"

    def file_button(self, obj):
        if obj.file:
            return format_html(
                '<a class="button" href="{}" download style="padding: 4px 8px; background-color: #5cb85c; color: white; text-decoration: none; border-radius: 4px;">Download</a>',
                obj.file.url
            )
        return 'No file'
    file_button.short_description = 'File'