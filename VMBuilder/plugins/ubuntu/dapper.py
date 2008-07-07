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
import glob
import logging
import suite
import VMBuilder.disk as disk
from   VMBuilder.util import run_cmd

class Dapper(suite.Suite):
    updategrub = "/sbin/update-grub"
    grubroot = "/lib/grub"
    valid_flavours = { 'i386' :  ['386', '686', '686-smp', 'k7', 'k7-smp', 'server', 'server-bigiron'],
                       'amd64' : ['amd64-generic', 'amd64-k8', 'amd64-k8-smp', 'amd64-server', 'amd64-xeon']}
    default_flavour = { 'i386' : 'server', 'amd64' : 'amd64-server' }
    disk_prefix = 'hd'

    def check_kernel_flavour(self, arch, flavour):
        if flavour in self.valid_flavours[arch]:
            return True
        else:
            return False

    def kernel_name(self):
        return 'linux-image-%s' % (self.vm.flavour or self.default_flavour[self.vm.arch],)

    def install(self, destdir):
        self.destdir = destdir

        logging.debug("debootstrapping")
        self.debootstrap()

        logging.debug("Installing fstab")
        self.install_fstab()
    
        logging.debug("Installing kernel")
        self.install_kernel()

        logging.debug("Installing grub")
        self.install_grub()

        logging.debug("Creating device.map")
        self.install_device_map()

        logging.debug("Installing menu.list")
        self.install_menu_lst()

        logging.debug("Unmounting volatile lrm filesystems")
        self.unmount_volatile()

    def unmount_volatile(self):
        for mntpnt in glob.glob('%s/lib/modules/*/volatile' % self.destdir):
            logging.debug("Unmounting %s" % mntpnt)
            run_cmd('umount', mntpnt)

    def install_menu_lst(self):
        run_cmd('mount', '--bind', '/dev', '%s/dev' % self.destdir)
        self.vm.add_clean_cmd('umount', '%s/dev' % self.destdir, ignore_fail=True)

        run_cmd('chroot', self.destdir, 'mount', '-t', 'proc', 'proc', '/proc')
        self.vm.add_clean_cmd('umount', '%s/proc' % self.destdir, ignore_fail=True)

        run_cmd('chroot', self.destdir, self.updategrub, '-y')
        self.mangle_grub_menu_lst()
        run_cmd('chroot', self.destdir, self.updategrub)

        run_cmd('umount', '%s/dev' % self.destdir)
        run_cmd('umount', '%s/proc' % self.destdir)

    def mangle_grub_menu_lst(self):
        bootdev = disk.bootpart(self.vm.disks)
        run_cmd('sed', '-ie', 's/^# kopt=root=\([^ ]*\)\(.*\)/# kopt=root=\/dev\/hd%s%d\2/g' % (bootdev.disk.devletters, bootdev.get_index()), '%s/boot/grub/menu.lst' % self.destdir)
        run_cmd('sed', '-ie', 's/^# groot.*/# groot %s/g' % bootdev.get_grub_id(), '%s/boot/grub/menu.lst' % self.destdir)
        run_cmd('sed', '-ie', '/^# kopt_2_6/ d', '%s/boot/grub/menu.lst' % self.destdir)

    def install_fstab(self):
        fp = open('%s/etc/fstab' % self.destdir, 'w')
        fp.write(self.fstab())
        fp.close()

    def install_device_map(self):
        fp = open('%s/boot/grub/device.map' % self.destdir, 'a')
        fp.write(self.device_map())
        fp.close()

    def device_map(self):
        return '\n'.join(['(%s) /dev/%s%s' % (self.disk_prefix, disk.get_grub_id(), disk.devletters) for disk in self.vm.disks])

    def debootstrap(self):
        cmd = ['debootstrap', self.vm.suite, self.destdir]
        if self.vm.mirror:
            cmd += [self.vm.mirror]
        run_cmd(*cmd)

    def install_kernel(self):
        kernel_name = self.kernel_name()
        run_cmd('chroot', self.destdir, 'apt-get', '--force-yes', '-y', 'install', kernel_name, 'grub')

    def install_grub(self):
        run_cmd('chroot', self.destdir, 'apt-get', '--force-yes', '-y', 'install', 'grub')
        run_cmd('cp', '-a', '%s%s/%s/' % (self.destdir, self.grubroot, self.vm.arch == 'amd64' and 'x86_64-pc' or 'i386-pc'), '%s/boot/grub' % self.destdir) 

    def fstab(self):
        retval = '''# /etc/fstab: static file system information.
#
# <file system>                                 <mount point>   <type>  <options>       <dump>  <pass>
proc                                            /proc           proc    defaults        0       0
'''
        parts = disk.get_ordered_partitions(self.vm.disks)
        for part in parts:
            retval += "/dev/%s%-38s %15s %7s %15s %d       %d\n" % (self.disk_prefix, disk.devletters, part.mntpnt, part.fstab_fstype(), part.fstab_options(), 0, 0)
        return retval
