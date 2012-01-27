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

from xbmcswift import Plugin, xbmc, xbmcgui
from resources.lib.eyetv_parser import Eyetv

__url__ = "http://github.com/beenje/plugin.video.eyetv.parser"
__plugin_name__ = 'EyeTV Parser'
__plugin_id__ = 'plugin.video.eyetv.parser'
plugin = Plugin(__plugin_name__, __plugin_id__)



# Default View
@plugin.route('/', default=True)
def show_homepage():
    items = [
        # Live TV
        {'label': plugin.get_string(30020), 'url': plugin.url_for('live_tv')},
        # Recordings
        {'label': plugin.get_string(30021), 'url': plugin.url_for('show_recordings')},
    ]
    return plugin.add_items(items)

@plugin.route('/live/')
def live_tv():
    pass

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
            'iconImage': icon,
            'thumbnailImage': thumbnail,
            'url': url,
            'info': info,
            'is_folder': False,
            'is_playable': True,
        } for (url, icon, thumbnail, info) in eyetv.recordingsInfo()]
        return plugin.add_items(items)


if __name__ == '__main__':
    plugin.run()
