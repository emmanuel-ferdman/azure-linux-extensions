import platform
from error_codes import *
from errors      import error_info
from helpers     import find_vm_bits, find_vm_distro
import install.supported_distros as supported_distros

    
def format_alternate_versions(supported_dist, versions):
    """
    print out warning if running the wrong version of OS
    """
    last = versions.pop()
    if (versions == []):
        s = "{0}".format(last)
    else:
        s = "{0} or {1}".format(', '.join(versions), last)
    return s


def check_vm_supported(vm_dist, vm_ver):
    if platform.machine() == 'aarch64':
        supported_dists = supported_distros.supported_dists_aarch64
    else:
        supported_dists = supported_distros.supported_dists_x86_64

    vm_supported = False

    # find VM distribution in supported list
    vm_supported_dist = None
    for supported_dist in (supported_dists.keys()):
        if (not vm_dist.lower().startswith(supported_dist)):
            continue
        vm_supported_dist = supported_dist
        # check if version is supported
        vm_ver_split = vm_ver.split('.')
        for supported_ver in (supported_dists[supported_dist]):
            supported_ver_split = supported_ver.split('.')
            vm_ver_match = True
            # try matching VM version with supported version
            for (idx, supported_ver_num) in enumerate(supported_ver_split):
                try:
                    supported_ver_num = int(supported_ver_num)
                    vm_ver_num = int(vm_ver_split[idx])
                    if (vm_ver_num is not supported_ver_num):
                        vm_ver_match = False
                        break
                except (IndexError, ValueError) as e:
                    vm_ver_match = False
                    break
                
            # check if successful in matching
            if (vm_ver_match):
                vm_supported = True
                break

        # check if any version successful in matching
        if (vm_supported):
            return NO_ERROR

    # VM distribution is supported, but not current version
    if (vm_supported_dist != None):
        versions = supported_dists[vm_supported_dist]
        alt_vers = format_alternate_versions(vm_supported_dist, versions)
        error_info.append((vm_dist, vm_ver, alt_vers))
        return ERR_OS_VER

    # VM distribution isn't supported
    else:
        error_info.append((vm_dist,))
        return ERR_OS


def check_os():
    if platform.machine() == 'x86_64':
        cpu_bits = find_vm_bits()
        if (not cpu_bits == '64-bit'):
            return ERR_BITS

    # get OS version
    (vm_dist, vm_ver, e) = find_vm_distro()
    if (vm_dist == None or vm_ver == None):
        error_info.append((e,))
        return ERR_FINDING_OS
    
    # check if OS version is supported
    return check_vm_supported(vm_dist, vm_ver)