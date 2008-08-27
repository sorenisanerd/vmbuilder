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
from VMBuilder import register_hypervisor, Hypervisor
from VMBuilder.util import run_cmd
import VMBuilder
import logging
import os.path
import stat

class Xen(Hypervisor):
    name = 'Xen'
    arg = 'xen'
    preferred_storage = Hypervisor.STORAGE_FS_IMAGE
    needs_bootloader = False

    def finalize(self):
        destimages = []
        for filesystem in self.vm.filesystems:
            destfile = '%s/%s' % (self.vm.destdir, os.path.basename(filesystem.filename))
            logging.info('Moving %s to %s' % (filesystem.filename, destfile))
            self.vm.result_files.append(destfile)
            run_cmd('cp', '--sparse=always', filesystem.filename, destfile)
            destimages.append(destfile)
    
        xenconf = '%s/xen.conf' % self.vm.destdir
        fp = open(xenconf, 'w')
        fp.write("""
# Configuration file for the Xen instance %s, created
# by VMBuilder
kernel = '%s'
ramdisk = '%s'
memory = %d

root = '/dev/xvda1,w'
disk = [
%s
]

name = '%s'

dhcp    = 'dhcp'

on_poweroff = 'destroy'
on_reboot   = 'restart'
on_crash    = 'restart'

extra = '2 console=xvc0'

"""  %   (self.vm.name,
          self.vm.distro.xen_kernel_path(),
          self.vm.distro.xen_ramdisk_path(),
          self.vm.mem,
          ',\n'.join(["'file:%s,xvd%d,w'" % (os.path.abspath(img), id+1) for (img, id) in zip(destimages, range(len(destimages)))]),
          self.vm.name))
        fp.close()
        self.vm.result_files.append(xenconf)

register_hypervisor(Xen)
