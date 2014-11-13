#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#                                 ESP Health
#                     System-wide Package Install Script
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# @author: Jason McVetta <jason.mcvetta@gmail.com>
# @organization: Channing Laboratory - http://www.channing.harvard.edu
# @contact: http://esphealth.org
# @copyright: (c) 2009-2011 Channing Laboratory
# @license: LGPL 3.0 - http://www.gnu.org/licenses/lgpl-3.0.txt
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Run this script to install system-wide dependencies - i.e. those which must
# be installed using the OS's package manager, rather than being installed to
# the local Python virtual environment by Pip.
#
# Currently this script only supports recent versions of Ubuntu.  Eventually it
# may support other OSes.  
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

_pkg_manager=''
_pkg_list=''
_os=`lsb_release -ds`

echo
echo Detected OS: $_os
echo

#
# Check Operating System
#
case $_os in
    "Ubuntu 11.10" | "Ubuntu 12.04 LTS" | "Ubuntu 12.04.4 LTS" | "Ubuntu 14.04.1 LTS" | "Ubuntu 12.04.2 LTS" )
        _pkg_manager='apt'
        _pkg_list="python-virtualenv python-pip python-setuptools python-dev libpq-dev postgresql-client"
        ;;
    "Ubuntu 10.04.4 LTS" | "Ubuntu 11.04" )
        _pkg_manager='apt'
        _pkg_list="python-virtualenv python-pip python-setuptools python-dev libpq-dev subversion"
        ;;
esac


#
# Install Packages
#
if [ -n "$_pkg_manager" ]; then
    echo "Automatic system package installation is supported!"
    echo 
    echo Installing packages:
    echo "    $_pkg_list"
    echo
else
    echo ERROR:
    echo
    echo Automatic installation of system-wide dependencies is currently supported only for Ubuntu Linux.
    echo
    exit 1
fi

case $_pkg_manager in
    "apt" )
        # Update package list
        echo 'Refreshing apt package list...'
        sudo apt-get update -q
        echo 'Installing apt packages...'
        # Install Ubuntu packages
        sudo apt-get install -q -y $_pkg_list
        ;;
    * )
        echo "Internal error - unknown package manager"
        exit 2
        ;;
esac
