#
# Copyright (C) 2012 Benjamin Bertrand
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# http://www.gnu.org/copyleft/gpl.html

from xbmcswift import xbmcgui, xbmc
from resources.lib.eyetv_parser import Eyetv
from resources.lib.eyetv_live import EyetvLive, EyetvLiveError
from config import plugin


BIT_RATE = ('320', '800', '1200', '2540', '4540')


def create_eyetv_live():
    """Return an Eyetvlive instance initialized with proper settings

    An instance is only returned if EyeTV is running and iPhone
    access is enabled"""
    server = plugin.get_setting('server')
    bitrate = BIT_RATE[int(plugin.get_setting('bitrate'))]
    xbmc.log('Server: %s - Bitrate: %s' % (server, bitrate), xbmc.LOGDEBUG)
    passwdEnabled = plugin.get_setting('passwdEnabled')
    if passwdEnabled == 'true':
        password = plugin.get_setting('password')
    else:
        password = ''
    return EyetvLive(server, bitrate, password)


@plugin.route('/', default=True)
def show_homepage():
    """Default view showing enabled categories"""
    livetv = plugin.get_setting('livetv')
    recordings = plugin.get_setting('recordings')
    if livetv == 'true' and recordings != 'true':
        return live_tv()
    elif livetv != 'true' and recordings == 'true':
        return show_recordings()
    else:
        # Show both categories if they are both enabled
        # (or both disabled)
        items = [
            # Live TV
            {'label': plugin.get_string(30020), 'url': plugin.url_for('live_tv')},
            # Recordings & Playlists
            {'label': plugin.get_string(30021), 'url': plugin.url_for('show_recordings')},
            {'label': plugin.get_string(30022), 'url': plugin.url_for('show_playlists')},
        ]
        return plugin.add_items(items)


@plugin.route('/live/')
def live_tv():
    """Display the channels available for live TV"""
    try:
        live = create_eyetv_live()
        channels = live.get_channels()
    except EyetvLiveError:
        return show_homepage()
    items = [{
        'label': ' '.join((channel['displayNumber'], channel['name'])),
        'url': plugin.url_for('watch_channel', serviceid=channel['serviceID']),
        'is_folder': False,
        'is_playable': True
    } for channel in channels]
    return plugin.add_items(items)


@plugin.route('/watch/<serviceid>/')
def watch_channel(serviceid):
    """Resolve and play the chosen channel"""
    try:
        live = create_eyetv_live()
        url = live.get_channel_url(serviceid)
    except EyetvLiveError:
        return None
    return plugin.set_resolved_url(url)


@plugin.route('/recordings/')
def show_recordings():
    """Shows all recordings from archive path"""
    archivePath = plugin.get_setting('archivePath')
    sortMethod = int(plugin.get_setting('sortMethod'))
    try:
        eyetv = Eyetv(archivePath, sortMethod)
    except IOError:
        xbmcgui.Dialog().ok(plugin.get_string(30100), plugin.get_string(30101))
    else:
        items = [{
            'label': info['title'],
            'url': url,
            'info': info,
            'is_folder': False,
            'is_playable': True,
        } for (url, icon, thumbnail, info) in eyetv.recordingsInfo()]
        return plugin.add_items(items)


@plugin.route('/playlists/')
def show_playlists():
    """Shows all playlists from archive path"""
    archivePath = plugin.get_setting('archivePath')
    sortMethod = int(plugin.get_setting('sortMethod'))
    try:
        eyetv = Eyetv(archivePath, sortMethod)
    except IOError:
        xbmcgui.Dialog().ok(plugin.get_string(30100), plugin.get_string(30101))
    else:
        items = [{
            'label': name + " (" + str(icount) + " Episodes) ",
            'url': plugin.url_for('display_playlist', playlistid=plid),
        } for (name, icount, plid) in eyetv.playlistsInfo()]
        return plugin.add_items(items)


@plugin.route('/showplaylist/<playlistid>/')
def display_playlist(playlistid):
    """Shows all recordings from playlist """
    archivePath = plugin.get_setting('archivePath')
    sortMethod = int(plugin.get_setting('sortMethod'))
    try:
        eyetv = Eyetv(archivePath, sortMethod)
    except IOError:
        xbmcgui.Dialog().ok(plugin.get_string(30100), plugin.get_string(30101))
    else:
        items = [{
            'label': info['title'],
            'url': url,
            'info': info,
            'is_folder': False,
            'is_playable': True,
        } for (url, icon, thumbnail, info)  in eyetv.RecordingsInPlaylist(playlistid)]
        return plugin.add_items(items)


if __name__ == '__main__':
    plugin.run()
