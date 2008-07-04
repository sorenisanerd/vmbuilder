#
#    Uncomplicated VM Builder
#    Copyright (C) 2007-2008 Canonical
#    
#    See AUTHORS for list of contributors
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Frontend interface and classes

import VMBuilder
import optparse

class Frontend(object):
    def __init__(self):
        self.settings = []

    def setting_group(self, help=None):
        return self.SettingsGroup(help)
    
    def add_setting_group(self, group):
        self.settings.append(group)

    def add_setting(self, **kwargs):
        self.settings.append(Setting(**kwargs))

    setting_types =  ['store', 'store']
    class Setting(object):
        def __init__(self, **kwargs):
            self.shortarg = kwargs.get('shortarg', None)
            self.longarg = kwargs.get('shortarg', None)
            self.default = kwargs.get('default', None)
            self.help = kwargs.get('help', None)
            type = kwargs.get('type', 'store')
            if type not in setting_types:
                raise VMBuilderException("Invalid option type: %s" % type)

    class SettingsGroup(Setting):
        pass

