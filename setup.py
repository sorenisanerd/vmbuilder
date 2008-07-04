from distutils.core import setup
import VMBuilder.plugins

setup(name='VMBuilder',
      version='0.1',
      description='Uncomplicated VM Builder',
      author='Soren Hansen',
      author_email='soren@canonical.com',
      url='http://launchpad.net/ubuntu-jeos/',
      packages=['VMBuilder', 'VMBuilder.plugins'] + VMBuilder.plugins.find_plugins(),
      scripts=['vmbuilder'], 
      )

