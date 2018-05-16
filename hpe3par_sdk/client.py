# (C) Copyright 2018 Hewlett Packard Enterprise Development LP
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from hpe3parclient import client
from hpe3parclient import exceptions
from hpe3parclient import http
from distutils.version import StrictVersion

from models import FlashCache
from models import VirtualVolume
from models import Task
from models import HostSet
from models import Host
from models import VLUN
from models import Port
from models import CPG
from models import LDLayoutCapacity
from models import VolumeSet
from models import QoSRule


import time


class HPE3ParClient(object):

    WSAPI_MIN_SUPPORTED_VERSION = '1.5.0'
    WSAPI_MIN_VERSION_VLUN_QUERY_SUPPORT = '1.4.2'
    WSAPI_MIN_VERSION_COMPRESSION_SUPPORT = '1.6.0'

    TUNE_VOLUME = 6
    TPVV = 1
    FPVV = 2
    TDVV = 3

    # Map of raid type enum and associated set sizes
    RAID_MAP = {'R0': {'raid_value': 1, 'set_sizes': [1]},
                'R1': {'raid_value': 2, 'set_sizes': [2, 3, 4]},
                'R5': {'raid_value': 3, 'set_sizes': [3, 4, 5, 6, 7, 8, 9]},
                'R6': {'raid_value': 4, 'set_sizes': [6, 8, 10, 12, 16]}
                }

    # Disk types
    FC = 1
    NL = 2
    SSD = 3

    # CPG High Availability
    PORT = 1
    CAGE = 2
    MAG = 3

    # Host Persona
    GENERIC = 1
    GENERIC_ALUA = 2
    GENERIC_LEGACY = 3
    HPUX_LEGACY = 4
    AIX_LEGACY = 5
    EGENERA = 6
    ONTAP_LEGACY = 7
    VMWARE = 8
    OPENVMS = 9
    HPUX = 10
    WINDOWS_SERVER = 11
    
    # QoS priority Enumeration
    class QOSPriority:
        LOW = 1
        NORMAL = 2
        HIGH = 3
    
    # Task Priority Enumeration
    class TaskPriority:
        HIGH = 1
        MEDIUM = 2
        LOW = 3
  
    # Qos Zero None Operation
    ZERO = 1
    NOLIMIT = 2

    # QoS target Type
    VVSET = 1
    SYS = 2
    
    VLUN_QUERY_SUPPORTED = False
    HOST_AND_VV_SET_FILTER_SUPPORTED = False
    
    CURRENT_WSAPI_VERSION = None

    """ The 3PAR REST API Client.

    :param api_url: The url to the WSAPI service on 3PAR
                    ie. http://<3par server>:8080/api/v1
    :type api_url: str

    """

    def __init__(self, api_url, debug=False, secure=False, timeout=None,
                 suppress_ssl_warnings=False):
        self.api_url = api_url
        self.client = client.HPE3ParClient(api_url, debug, secure, timeout, suppress_ssl_warnings)
        self.check_WSAPI_version()
        
    
    def check_WSAPI_version(self):
        try:
            api_version = self.getWsApiVersion()
            self.compare_version(api_version)
        except Exception as exception:
            ex_message = str(exception)
            if ex_message and 'SSL Certificate Verification Failed' in ex_message:
                raise exceptions.SSLCertFailed()
            else:
                msg = """Error: %s - Error communicating with 3PAR WSAPI. 
Check proxy settings. If error persists, either the
3PAR WSAPI is not running OR the version of the WSAPI is
not supported.""" % (ex_message)
                raise exceptions.ConnectionError(msg)
                
    def compare_version(self, api_version):
        self.CURRENT_WSAPI_VERSION = '{}.{}.{}'.format(api_version['major'], api_version['minor'], api_version['revision'])
        if StrictVersion(self.CURRENT_WSAPI_VERSION) < StrictVersion(self.WSAPI_MIN_SUPPORTED_VERSION):
            err_msg = 'Unsupported 3PAR WS API version %s, min supported version is %s' % (self.CURRENT_WSAPI_VERSION, self.WSAPI_MIN_SUPPORTED_VERSION)
            raise exceptions.UnsupportedVersion(err_msg)
            
        if StrictVersion(self.CURRENT_WSAPI_VERSION) >= StrictVersion(self.WSAPI_MIN_VERSION_VLUN_QUERY_SUPPORT):
            self.VLUN_QUERY_SUPPORTED = True
            
        if StrictVersion(self.CURRENT_WSAPI_VERSION) >=  StrictVersion(self.WSAPI_MIN_VERSION_COMPRESSION_SUPPORT):
            self.HOST_AND_VV_SET_FILTER_SUPPORTED = True
            

    def setSSHOptions(self, ip, login, password, port=22,
                      conn_timeout=None, privatekey=None,
                      **kwargs):
        """Set SSH Options for ssh calls.

        This is used to set the SSH credentials for calls
        that use SSH instead of REST HTTP.

        """
        self.client.setSSHOptions(ip, login, password, port, conn_timeout, privatekey)

    def _run(self, cmd):
        return self.client._run(cmd)

    def getWsApiVersion(self):
        """Get the 3PAR WS API version.

        :returns: Version dict

        """
        return self.client.getWsApiVersion()

    def debug_rest(self, flag):
        """This is useful for debugging requests to 3PAR.

        :param flag: set to True to enable debugging
        :type flag: bool

        """
        self.client.debug_rest(flag)

    def login(self, username, password, optional=None):
        """This authenticates against the 3PAR wsapi server and creates a
           session.

        :param username: The username
        :type username: str
        :param password: The Password
        :type password: str

        :returns: None

        """
        self.client.login(username, password, optional)

    def logout(self):
        """This destroys the session and logs out from the 3PAR server.
           The SSH connection to the 3PAR server is also closed.

        :returns: None

        """
        try:
            self.client.logout()
        #Making logout idempotent by not throwing HTTP Forbidden error
        except exceptions.HTTPForbidden:
            pass
        except Exception:
            raise Exception

    def getStorageSystemInfo(self):
        """Get the Storage System Information

        :returns: Dictionary of Storage System Info

        """
        return self.client.getStorageSystemInfo()

    def getWSAPIConfigurationInfo(self):
        """Get the WSAPI Configuration Information.

        :returns: Dictionary of WSAPI configurations

        """
        return self.client.getWSAPIConfigurationInfo()

    def getOverallSystemCapacity(self):
        """Get the overall system capacity for the 3PAR server.

        :returns: Dictionary of system capacity information

        .. code-block:: python

            capacity = {
              "allCapacity": {                        # Overall system capacity
                                                      # includes FC, NL, SSD
                                                      # device types
                "totalMiB": 20054016,                 # Total system capacity
                                                      # in MiB
                "allocated": {                        # Allocated space info
                  "totalAllocatedMiB": 12535808,      # Total allocated
                                                      # capacity
                  "volumes": {                        # Volume capacity info
                    "totalVolumesMiB": 10919936,      # Total capacity
                                                      # allocated to volumes
                    "nonCPGsMiB": 0,                  # Total non-CPG capacity
                    "nonCPGUserMiB": 0,               # The capacity allocated
                                                      # to non-CPG user space
                    "nonCPGSnapshotMiB": 0,           # The capacity allocated
                                                      # to non-CPG snapshot
                                                      # volumes
                    "nonCPGAdminMiB": 0,              # The capacity allocated
                                                      # to non-CPG
                                                      # administrative volumes
                    "CPGsMiB": 10919936,              # Total capacity
                                                      # allocated to CPGs
                    "CPGUserMiB": 7205538,            # User CPG space
                    "CPGUserUsedMiB": 7092550,        # The CPG allocated to
                                                      # user space that is
                                                      # in use
                    "CPGUserUnusedMiB": 112988,       # The CPG allocated to
                                                      # user space that is not
                                                      # in use
                    "CPGSnapshotMiB": 2411870,        # Snapshot CPG space
                    "CPGSnapshotUsedMiB": 210256,     # CPG allocated to
                                                      # snapshot that is in use
                    "CPGSnapshotUnusedMiB": 2201614,  # CPG allocated to
                                                      # snapshot space that is
                                                      # not in use
                    "CPGAdminMiB": 1302528,           # Administrative volume
                                                      # CPG space
                    "CPGAdminUsedMiB": 115200,        # The CPG allocated to
                                                      # administrative space
                                                      # that is in use
                    "CPGAdminUnusedMiB": 1187328,     # The CPG allocated to
                                                      # administrative space
                                                      # that is not in use
                    "unmappedMiB": 0                  # Allocated volume space
                                                      # that is unmapped
                  },
                  "system": {                    # System capacity info
                     "totalSystemMiB": 1615872,  # System space capacity
                     "internalMiB": 780288,      # The system capacity
                                                 # allocated to internal
                                                 # resources
                     "spareMiB": 835584,         # Total spare capacity
                     "spareUsedMiB": 0,          # The system capacity
                                                 # allocated to spare resources
                                                 # in use
                     "spareUnusedMiB": 835584    # The system capacity
                                                 # allocated to spare resources
                                                 # that are unused
                    }
                },
                  "freeMiB": 7518208,             # Free capacity
                  "freeInitializedMiB": 7518208,  # Free initialized capacity
                  "freeUninitializedMiB": 0,      # Free uninitialized capacity
                  "unavailableCapacityMiB": 0,    # Unavailable capacity in MiB
                  "failedCapacityMiB": 0          # Failed capacity in MiB
              },
              "FCCapacity": {   # System capacity from FC devices only
                  ...           # Same structure as above
              },
              "NLCapacity": {   # System capacity from NL devices only
                  ...           # Same structure as above
              },
              "SSDCapacity": {  # System capacity from SSD devices only
                  ...           # Same structure as above
              }
            }

        """
        return self.client.getOverallSystemCapacity()

    def createFlashCache(self, sizeInGib, mode):
        """Creates a new FlashCache

        :param sizeInGib: Specifies the node pair size of the Flash Cache on
                          the system.
        :type: int
        :param: mode    : Simulator: 1
                          Real: 2 (default)
        :type: int

        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - NO_SPACE - Not enough space is available for the operation.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_EXCEEDS_RANGE - A JSON input object contains a
            name-value pair with a numeric value that exceeds the expected
            range. Flash Cache exceeds the expected range. The HTTP ref member
            contains the name.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
           - EXISTENT_FLASH_CACHE - The Flash Cache already exists.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - FLASH_CACHE_NOT_SUPPORTED - Flash Cache is not supported.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_FLASH_CACHE_SIZE - Invalid Flash Cache size. The size must
            be a multiple of 16 G.
        """
        return self.client.createFlashCache(sizeInGib, mode)

    def getFlashCache(self):
        """Get information about flash cache on the 3Par array.

        :returns: list of Hosts
        """
        return FlashCache(self.client.getFlashCache())

    def deleteFlashCache(self):
        """Deletes an existing Flash Cache

        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - FLASH_CACHE_IS_BEING_REMOVED - Unable to delete the Flash Cache,
            the Flash Cache is being removed.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - FLASH_CACHE_NOT_SUPPORTED - Flash Cache is not supported on this
            system.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
           - NON_EXISTENT_FLASH_CACHE - The Flash Cache does not exist.
        """
        return self.client.deleteFlashCache()

    # Volume methods
    def getVolumes(self):
        """Get the list of Volumes

        :returns: list of Volumes

        """
        volumes = []
        volumes_list = self.client.getVolumes()['members']
        for volume in volumes_list:
            volumes.append(VirtualVolume(volume))
        return volumes

    def getVolume(self, name):
        """Get information about a volume.

        :param name: The name of the volume to find
        :type name: str

        :returns: volume
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOL - volume doesn't exist

        """
        return VirtualVolume(self.client.getVolume(name))

    def createVolume(self, name, cpgName, sizeMiB, optional=None):
        """Create a new volume.

        :param name: the name of the volume
        :type name: str
        :param cpgName: the name of the destination CPG
        :type cpgName: str
        :param sizeMiB: size in MiB for the volume
        :type sizeMiB: int
        :param optional: dict of other optional items
        :type optional: dict

        .. code-block:: python

            optional = {
             'id': 12,                    # Volume ID. If not specified, next
                                          # available is chosen
             'comment': 'some comment',   # Additional information up to 511
                                          # characters
             'policies: {                 # Specifies VV policies
                'staleSS': False,         # True allows stale snapshots.
                'oneHost': True,          # True constrains volume export to
                                          # single host or host cluster
                'zeroDetect': True,       # True requests Storage System to
                                          # scan for zeros in incoming write
                                          # data
                'system': False,          # True special volume used by system
                                          # False is normal user volume
                'caching': True},         # Read-only. True indicates write &
                                          # read caching & read ahead enabled
             'snapCPG': 'CPG name',       # CPG Used for snapshots
             'ssSpcAllocWarningPct': 12,  # Snapshot space allocation warning
             'ssSpcAllocLimitPct': 22,    # Snapshot space allocation limit
             'tpvv': True,                # True: Create TPVV
                                          # False (default) Create FPVV
             'usrSpcAllocWarningPct': 22, # Enable user space allocation
                                          # warning
             'usrSpcAllocLimitPct': 22,   # User space allocation limit
             'expirationHours': 256,      # Relative time from now to expire
                                          # volume (max 43,800 hours)
             'retentionHours': 256        # Relative time from now to retain
                                          # volume (max 43,800 hours)
            }

        :returns: List of Volumes

        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT - Invalid Parameter
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - TOO_LARGE - Volume size above limit
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - NO_SPACE - Not Enough space is available
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - PERM_DENIED - Permission denied
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - EXISTENT_SV - Volume Exists already

        """
        if optional is not None and self.CURRENT_WSAPI_VERSION < self.WSAPI_MIN_VERSION_COMPRESSION_SUPPORT:
            if 'compression' in optional.keys():
                del optional['compression']
        return self.client.createVolume(name, cpgName, sizeMiB, optional)

    def deleteVolume(self, name):
        """Delete a volume.

        :param name: the name of the volume
        :type name: str

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOL - The volume does not exist
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - PERM_DENIED - Permission denied
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RETAINED - Volume retention time has not expired
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - HAS_RO_CHILD - Volume has read-only child
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - HAS_CHILD - The volume has a child volume
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - IN_USE - The volume is in use by VV set, VLUN, etc

        """
        try:
            self.client.removeVolumeMetaData(name,'type')
        except:
            pass
        return self.client.deleteVolume(name)

    def modifyVolume(self, name, volumeMods, app_type=None):
        """Modify a volume.

        :param name: the name of the volume
        :type name: str
        :param volumeMods: dictionary of volume attributes to change
        :type volumeMods: dict
        .. code-block:: python

            volumeMods = {
             'newName': 'newName',         # New volume name
             'comment': 'some comment',    # New volume comment
             'snapCPG': 'CPG name',        # Snapshot CPG name
             'policies: {                  # Specifies VV policies
                'staleSS': False,          # True allows stale snapshots.
                'oneHost': True,           # True constrains volume export to
                                           # single host or host cluster
                'zeroDetect': True,        # True requests Storage System to
                                           # scan for zeros in incoming write
                                           # data
                'system': False,           # True special volume used by system
                                           # False is normal user volume
                'caching': True},          # Read-only. True indicates write &
                                           # read caching & read ahead enabled
             'ssSpcAllocWarningPct': 12,   # Snapshot space allocation warning
             'ssSpcAllocLimitPct': 22,     # Snapshot space allocation limit
             'tpvv': True,                 # True: Create TPVV
                                           # False: (default) Create FPVV
             'usrSpcAllocWarningPct': 22,  # Enable user space allocation
                                           # warning
             'usrSpcAllocLimitPct': 22,    # User space allocation limit
             'userCPG': 'User CPG name',   # User CPG name
             'expirationHours': 256,       # Relative time from now to expire
                                           # volume (max 43,800 hours)
             'retentionHours': 256,        # Relative time from now to retain
                                           # volume (max 43,800 hours)
             'rmSsSpcAllocWarning': False, # True removes snapshot space
                                           # allocation warning.
                                           # False sets it when value > 0
             'rmUsrSpcAllocWarwaning': False, # True removes user space
                                           #  allocation warning.
                                           # False sets it when value > 0
             'rmExpTime': False,           # True resets expiration time to 0.
                                           # False sets it when value > 0
             'rmSsSpcAllocLimit': False,   # True removes snapshot space
                                           # allocation limit.
                                           # False sets it when value > 0
             'rmUsrSpcAllocLimit': False   # True removes user space
                                           # allocation limit.
                                           # False sets it when value > 0
            }

        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_WARN_GT_LIMIT - Allocation warning level is higher than
            the limit.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_USR_ALRT_NON_TPVV - User space allocation alerts are
            valid only with a TPVV.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_RETAIN_GT_EXPIRE - Retention time is greater than
            expiration time.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_VV_POLICY - Invalid policy specification (for example,
            caching or system is set to true).
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_EXCEEDS_LENGTH - Invalid input: string length exceeds
            limit.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_TIME - Invalid time specified.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_MODIFY_USR_CPG_TPVV - usr_cpg cannot be modified
            on a TPVV.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - UNLICENSED_FEATURE - Retention time cannot be modified on a
            system without the Virtual Lock license.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - CPG_NOT_IN_SAME_DOMAIN - Snap CPG is not in the same domain as
            the user CPG.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_PEER_VOLUME - Cannot modify a peer volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPInternalServerError`
            - INT_SERV_ERR - Metadata of the VV is corrupted.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_SYS_VOLUME - Cannot modify retention time on a
            system volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_INTERNAL_VOLUME - Cannot modify an internal
            volume
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_VOLUME_NOT_DEFINED_ALL_NODES - Cannot modify a
            volume until the volume is defined on all volumes.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INVALID_OPERATION_VV_ONLINE_COPY_IN_PROGRESS - Cannot modify a
            volume when an online copy for that volume is in progress.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INVALID_OPERATION_VV_VOLUME_CONV_IN_PROGRESS - Cannot modify a
            volume in the middle of a conversion operation.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INVALID_OPERATION_VV_SNAPSPACE_NOT_MOVED_TO_CPG - Snapshot space
            of a volume needs to be moved to a CPG before the user space.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_VOLUME_ACCOUNTING_IN_PROGRESS - The volume
            cannot be renamed until snapshot accounting has finished.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_ZERO_DETECT_TPVV - The zero_detect policy can be
            used only on TPVVs.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_CPG_ON_SNAPSHOT - CPG cannot be assigned to a
            snapshot.

        """
        return self.client.modifyVolume(name, volumeMods, app_type)

    def growVolume(self, name, amount):
        """Grow an existing volume by 'amount' Mebibytes.

        :param name: the name of the volume
        :type name: str
        :param amount: the additional size in MiB to add, rounded up to the
                       next chunklet size (e.g. 256 or 1000 MiB)
        :type amount: int

        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_NOT_IN_SAME_DOMAIN - The volume is not in the same domain.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOL - The volume does not exist.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_UNSUPPORTED_VV_TYPE - Invalid operation: Cannot
            grow this type of volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_TUNE_IN_PROGRESS - Invalid operation: Volume
            tuning is in progress.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_EXCEEDS_LENGTH - Invalid input: String length exceeds
            limit.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_VV_GROW_SIZE - Invalid grow size.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_NEW_SIZE_EXCEEDS_CPG_LIMIT - New volume size exceeds CPG limit
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_INTERNAL_VOLUME - This operation is not allowed
            on an internal volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_VOLUME_CONV_IN_PROGRESS - Invalid operation: VV
            conversion is in progress.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_VOLUME_COPY_IN_PROGRESS - Invalid operation:
            online copy is in progress.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_CLEANUP_IN_PROGRESS - Internal volume cleanup is
            in progress.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_IS_BEING_REMOVED - The volume is being removed.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_IN_INCONSISTENT_STATE - The volume has an internal consistency
            error.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_SIZE_CANNOT_REDUCE - New volume size is smaller than the
            current size.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_NEW_SIZE_EXCEEDS_LIMITS - New volume size exceeds the limit.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_SA_SD_SPACE_REMOVED - Invalid operation: Volume
            SA/SD space is being removed.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_IS_BUSY - Invalid operation: Volume is currently
            busy.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_NOT_STARTED - Volume is not started.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_IS_PCOPY - Invalid operation: Volume is a
            physical copy.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_NOT_IN_NORMAL_STATE - Volume state is not normal
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_PROMOTE_IN_PROGRESS - Invalid operation: Volume
            promotion is in progress.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_PARENT_OF_PCOPY - Invalid operation: Volume is
            the parent of physical copy.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - NO_SPACE - Insufficent space for requested operation.

        """
        return self.client.growVolume(name, amount)

    def copyVolume(self, src_name, dest_name, dest_cpg, optional=None):
        """Copy/Clone a volume.

        :param src_name: the source volume name
        :type src_name: str
        :param dest_name: the destination volume name
        :type dest_name: str
        :param dest_cpg: the destination CPG
        :type dest_cpg: str
        :param optional: Dictionary of optional params
        :type optional: dict

        .. code-block:: python

            optional = {
                'online': False,                # should physical copy be
                                                # performed online?
                'tpvv': False,                  # use thin provisioned space
                                                # for destination
                                                # (online copy only)
                'snapCPG': 'OpenStack_SnapCPG', # snapshot CPG for the
                                                # destination
                                                # (online copy only)
                'saveSnapshot': False,          # save the snapshot of the
                                                # source volume
                'priority': 1                   # taskPriorityEnum (does not
                                                # apply to online copy)
            }

        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_ILLEGAL_CHAR - Invalid VV name or CPG name.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_CPG - The CPG does not exists.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - CPG_NOT_IN SAME_DOMAIN - The CPG is not in the current domain.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOL - The volume does not exist
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_NOT_IN_SAME_DOMAIN - The volume is not in the same domain.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_BAD_ENUM_VALUE - The priority value in not in the valid
            range(1-3).
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - EXISTENT_VOLUME - The volume already exists.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_SYS_VOLUME - The operation is not allowed on a
            system volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_NON_BASE_VOLUME - The destination volume is not a
            base volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_IN_REMOTE_COPY - The destination volume is involved
            in a remote copy.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_EXPORTED - The volume is exported.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_COPY_TO_SELF - The destination volume is the
            same as the parent.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_READONLY_SNAPSHOT - The parent volume is a
            read-only snapshot.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_COPY_TO_BASE - The destination volume is the
            base volume of a parent volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_VOLUME_CONV_IN_PROGRESS  - The volume is in a
            conversion operation.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_NO_SNAPSHOT_ALLOWED - The parent volume must
            allow snapshots.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_ONLINE_COPY_IN_PROGRESS  - The volume is the
            target of an online copy.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_CLEANUP_IN_PROGRESS - Cleanup of internal volume
            for the volume is in progress.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_CIRCULAR_COPY - The parent volume is a copy of
            the destination volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_PEER_VOLUME - The operation is not allowed on a
            peer volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_INTERNAL_VOLUME - The operation is not allowed
            on an internal volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_IS_BEING_REMOVED - The volume is being removed.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_NOT_IN_NORMAL_STATE - The volume is not in the
            normal state.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_IN_INCONSISTENT_STATE - The volume has an internal consistency
            error.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_PCOPY_IN_PROGRESS  - The destination volume has
            a physical copy in progress.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_FAILED_ONLINE_COPY  - Online copying of the
            destination volume has failed.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_COPY_PARENT_TOO_BIG - The size of the parent
            volume is larger than the size of the destination volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_NO_PARENT - The volume has no physical parent.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - IN_USE - The resynchronization snapshot is in a stale state.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_IN_STALE_STATE - The volume is in a stale state.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VVCOPY - Physical copy not found.

        """
        if optional is not None and self.CURRENT_WSAPI_VERSION < self.WSAPI_MIN_VERSION_COMPRESSION_SUPPORT:
            for attribute in ['compression', 'allowRemoteCopyParent', 'skipZero']:
                if attribute in optional.keys():
                    del optional[attribute]
        return self.client.copyVolume(src_name, dest_name, dest_cpg, optional)

    def isOnlinePhysicalCopy(self, name):
        """Is the volume being created by process of online copy?

        :param name: the name of the volume
        :type name: str

        """
        return self.client.isOnlinePhysicalCopy(name)

    def stopOnlinePhysicalCopy(self, name):
        """Stopping a online physical copy operation.

        :param name: the name of the volume
        :type name: str

        """
        return self.client.stopOnlinePhysicalCopy(name)

    def getAllTasks(self):
        """Get the list of all Tasks

        :returns: list of all Tasks

        """
        Tasks = []
        tasks_list = self.client.getAllTasks()['members']
        for tasks in tasks_list:
            Tasks.append(Task(tasks))
        return Tasks

    def getTask(self, taskId):
        """Get the status of a task.

        :param taskId: the task id
        :type taskId: int

        :returns: the status of the task

        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_BELOW_RANGE - Bad Request Task ID must be a positive
            value.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_EXCEEDS_RANGE - Bad Request Task ID is too large.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_TASK - Task with the specified task ID does not
            exist.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_WRONG_TYPE - Task ID is not an integer.

        """
        return Task(self.client.getTask(taskId))

    def _findTask(self, name, active=True):
        return self.client._findTask(name, active)

    def waitForTaskToEnd(self, taskId, pollRateSecs=15):
        task = self.getTask(taskId)
        while task is not None:  # loop begin
            state = task.status
            if state == client.HPE3ParClient.TASK_DONE:
                break
            elif state == client.HPE3ParClient.TASK_CANCELLED:
                break
            elif state == client.HPE3ParClient.TASK_FAILED:
                msg = "Task '%s' has FAILED!!!" % task.taskId
                raise msg
            elif state == client.HPE3ParClient.TASK_ACTIVE:
                time.sleep(pollRateSecs)
                task = self.getTask(task.task_id)

        # Return the Task Result
        if (task is not None and task.status is not None and
                task.status == 'DONE'):
            return True
        else:
            return False

    def _convert_cli_output_to_collection_like_wsapi(self, cli_output):
        """Convert CLI output into a response that looks the WS-API would.

        Use the first line as coma-separated headers.
        Build dictionaries for the remaining lines using the headers as keys.
        Return a dictionary with total and members (the dictionaries).

        If there isn't enough data for headers and data then
        total is 0 and members is an empty list.

        If you need more validity checking, you might want to do it before this
        generic routine.  It does minimal checking.

        :param cli_output: The result from the CLI (i.e. from ssh.run(cmd)).
                           The first row is headers. Following rows are data.
        :type cli_output: list

        .. code-block:: python

            # Example 1: Typical CLI output with header row and data rows.
            cli_output =
                [
                    'InstallTime,Id,Package,Version',
                    '2013-08-21 18:06:45 PDT,MU2,Complete,3.1.2.422',
                    '2013-10-10 15:20:05 PDT,MU3,Complete,3.1.2.484',
                    '2014-01-30 11:34:20 PST,DEVEL,Complete,3.1.3.170',
                    '2014-03-26 13:59:42 PDT,GA,Complete,3.1.3.202',
                    '2014-06-06 14:46:56 PDT,MU1,Complete,3.1.3.230'
                ]

            # Example 2: Example CLI output for an empty result.
            cli_output = ['No patch is applied to the system.']

        :returns: dict with total and members. members is list of dicts using
                  header for keys and data for values.
        :rtype: dict

        .. code-block:: python

            # Example 1: Converted to total and members list of dictionaries.
            ret = {
                'total': 5,
                'members': [
                    {
                        'Package': 'Complete',
                        'Version': '3.1.2.422',
                        'InstallTime': '2013-08-21 18:06:45 PDT',
                        'Id': 'MU2'
                    },
                    {
                        'Package': 'Complete',
                        'Version': '3.1.2.484',
                        'InstallTime': '2013-10-10 15:20:05 PDT',
                        'Id': 'MU3'
                    },
                    {
                        'Package': 'Complete',
                        'Version': '3.1.3.170',
                        'InstallTime': '2014-01-30 11:34:20 PST',
                        'Id': 'DEVEL'
                    },
                    {
                        'Package': 'Complete',
                        'Version': '3.1.3.202',
                        'InstallTime': '2014-03-26 13:59:42 PDT',
                        'Id': 'GA'
                    },
                    {
                        'Package': 'Complete',
                        'Version': '3.1.3.230',
                        'InstallTime': '2014-06-06 14:46:56 PDT',
                        'Id': 'MU1'
                    }
                ]
            }

            # Example 2: No data rows, so zero members.
            ret = {'total': 0, 'members': []}

        """
        return self.client._convert_cli_output_to_collection_like_wsapi(
            cli_output)

    def getPatches(self, history=True):
        """Get all the patches currently affecting the system.

        :param history: Specify the history of all patches and updates applied
                        to the system.
        :returns: dict with total and members
                  (see convert_cli_output_to_collection_like_wsapi())

        """
        return self.client.getPatches(history)

    def getPatch(self, patch_id):
        """Get details on a specified patch ID if it has been applied to the
           system.

        :param patch_id:  The ID of the patch.
        :returns: list of str (raw lines of CLI output as strings)

        """
        return self.client.getPatch(patch_id)

    def promoteVirtualCopy(self, snapshot, optional=None):
        """Revert a volume to snapshot.
        :param snapshot: the snapshot name
        :type snapshot: str
        :param optional: Dictionary of optional params
        :type optional: dict
        .. code-block:: python
            optional = {
                'online': False,                # should execute promote
                                                # operation on online volume?
                'allowRemoteCopyParent': 'False',
                                                # allow promote operation if
                                                # volume is in remote copy
                                                # volume group?
                'priority': 1                   # taskPriorityEnum (does not
                                                # apply to online copy)
            }
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_NOT_STARTED - Volume is not started.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_IS_BEING_REMOVED - The volume is being removed.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_IN_STALE_STATE - The volume is in a stale state.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_CANNOT_STOP_ONLINE_PROMOTE - The online
            promote cannot be stopped.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_BASE_VOLUME - The volume is a base volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_PCOPY_IN_PROGRESS - The destination volume has
            a physical copy in progress.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_PARENT_PCOPY_IN_PROGRESS - The parent is involved
            in a physical copy.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_TUNE_IN_PROGRESS - Volume tuning is in
            progress.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_IN_REMOTE_COPY - The volume is involved in
            Remote Copy.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_PARENT_VV_EXPORTED - Parent volume is exported.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_EXPORTED - Parent volume is exported.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_PROMOTE_TARGET_NOT_BASE_VV - The promote target is
            not a base volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_PARENT_SIZE_HAS_INCREASED - The parent volume size
            has increased.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_PARAM_CONFLICT - Parameters cannot be present at
            the same time.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_IS_BUSY - Volume is currently busy.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_PROMOTE_IN_PROGRESS - Volume promotion is in
            progress.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_PROMOTE_IS_NOT_IN_PROGRESS - Volume promotion
            is not in progress.
        """
        if optional is not None and self.CURRENT_WSAPI_VERSION < self.WSAPI_MIN_VERSION_COMPRESSION_SUPPORT:
            if 'allowRemoteCopyParent' in optional.keys():
                del optional['allowRemoteCopyParent']
        return self.client.promoteVirtualCopy(snapshot, optional)

    def stopOfflinePhysicalCopy(self, name):
        """Stopping a offline physical copy operation.

        :param name: the name of the volume
        :type name: str

        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_ILLEGAL_CHAR - Invalid VV name or CPG name.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_CPG - The CPG does not exists.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - CPG_NOT_IN SAME_DOMAIN - The CPG is not in the current domain.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOL - The volume does not exist
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_NOT_IN_SAME_DOMAIN - The volume is not in the same domain.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_BAD_ENUM_VALUE - The priority value in not in the valid
            range(1-3).
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - EXISTENT_VOLUME - The volume already exists.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_SYS_VOLUME - The operation is not allowed on a
            system volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_NON_BASE_VOLUME - The destination volume is not a
            base volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_IN_REMOTE_COPY - The destination volume is involved
            in a remote copy.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_EXPORTED - The volume is exported.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_COPY_TO_SELF - The destination volume is the
            same as the parent.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_READONLY_SNAPSHOT - The parent volume is a
            read-only snapshot.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_COPY_TO_BASE - The destination volume is the
            base volume of a parent volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_VOLUME_CONV_IN_PROGRESS  - The volume is in a
            conversion operation.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_NO_SNAPSHOT_ALLOWED - The parent volume must
            allow snapshots.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_ONLINE_COPY_IN_PROGRESS  - The volume is the
            target of an online copy.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_CLEANUP_IN_PROGRESS - Cleanup of internal volume
            for the volume is in progress.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_CIRCULAR_COPY - The parent volume is a copy of
            the destination volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_PEER_VOLUME - The operation is not allowed on a
            peer volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_INTERNAL_VOLUME - The operation is not allowed
            on an internal volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_IS_BEING_REMOVED - The volume is being removed.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_NOT_IN_NORMAL_STATE - The volume is not in the
            normal state.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_IN_INCONSISTENT_STATE - The volume has an internal consistency
            error.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_PCOPY_IN_PROGRESS  - The destination volume has
            a physical copy in progress.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_FAILED_ONLINE_COPY  - Online copying of the
            destination volume has failed.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_COPY_PARENT_TOO_BIG - The size of the parent
            volume is larger than the size of the destination volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_NO_PARENT - The volume has no physical parent.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - IN_USE - The resynchronization snapshot is in a stale state.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_IN_STALE_STATE - The volume is in a stale state.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VVCOPY - Physical copy not found.

        """
        return self.client.stopOfflinePhysicalCopy(name)
        
    def resyncPhysicalCopy(self, volume_name):
        """Resynchronizes a physical copy.

        :param name - The name of the volume
        :type - string
        """
        return self.client.resyncPhysicalCopy(volume_name)

    def createSnapshot(self, name, copyOfName, optional=None):
        """Create a snapshot of an existing Volume.

        :param name: Name of the Snapshot
        :type name: str
        :param copyOfName: The volume you want to snapshot
        :type copyOfName: str
        :param optional: Dictionary of optional params
        :type optional: dict

        .. code-block:: python

            optional = {
                'id': 12,                   # Specifies the ID of the volume,
                                            # next by default
                'comment': "some comment",
                'readOnly': True,           # Read Only
                'expirationHours': 36,      # time from now to expire
                'retentionHours': 12        # time from now to expire
            }

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOL - The volume does not exist
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - PERM_DENIED - Permission denied

        """
        if optional is not None and self.CURRENT_WSAPI_VERSION < self.WSAPI_MIN_VERSION_COMPRESSION_SUPPORT:
            if 'allowRemoteCopyParent' in optional.keys():
                del optional['allowRemoteCopyParent']
        return self.client.createSnapshot(name, copyOfName, optional)

    # Host Set methods
    def findHostSet(self, name):
        """
        Find the Host Set name for a host.

        :param name: the host name
        :type name: str
        """
        return self.client.findHostSet(name)

    def getHostSets(self):
        """
        Get information about every Host Set on the 3Par array

        :returns: list of Host Sets
        """
        host_list = []
        hosts = self.client.getHostSets()['members']
        for host in hosts:
            host_list.append(HostSet(host))
        return host_list

    def getHostSet(self, name):
        """
        Get information about a Host Set

        :param name: The name of the Host Set to find
        :type name: str

        :returns: host set dict
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_SET - The set does not exist
        """
        return HostSet(self.client.getHostSet(name))

    def createHostSet(self, name, domain=None, comment=None, setmembers=None):
        """
        This creates a new host set

        :param name: the host set to create
        :type set_name: str
        :param domain: the domain where the set lives
        :type domain: str
        :param comment: a comment for the host set
        :type comment: str
        :param setmembers: the hosts to add to the host set, the existence
        of the host will not be checked
        :type setmembers: list of str
        :returns: id of host set created
        :rtype: str

        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - EXISTENT_SET - The set already exits.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - MEMBER_IN_DOMAINSET - The host is in a domain set.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - MEMBER_IN_SET - The object is already part of the set.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - MEMBER_NOT_IN_SAME_DOMAIN - Objects must be in the same domain
            to perform this operation.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_HOST - The host does not exists.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_DUP_NAME - Invalid input (duplicate name).
        """
        return self.client.createHostSet(name, domain, comment, setmembers)

    def deleteHostSet(self, name):
        """
        This removes a host set.

        :param name: the host set to remove
        :type name: str

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_SET - The set does not exists.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - EXPORTED_VLUN - The host set has exported VLUNs.
        """
        self.client.deleteHostSet(name)

    def modifyHostSet(self, name, action=None, newName=None, comment=None,
                      setmembers=None):
        """
        This modifies a host set by adding or removing a hosts from the set.
        It's action is based on the enums SET_MEM_ADD or SET_MEM_REMOVE.

        :param name: the host set name
        :type name: str
        :param action: add or remove host(s) from the set
        :type action: enum
        :param newName: new name of set
        :type newName: str
        :param comment: new comment for the set
        :type comment: str
        :param setmembers: the host(s) to add to the set, the existence of the
                           host(s) will not be checked
        :type setmembers: list str

        :returns: headers - dict of HTTP Response headers.  Upon successful
                  modification of a host set HTTP code 200 OK is returned and
                  the URI of the updated host set will be returned in the
                  location portion of the headers.
        :returns: body - the body of the response.  None if successful.

        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - EXISTENT_SET - The set already exits.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_SET - The set does not exists.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - MEMBER_IN_DOMAINSET - The host is in a domain set.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - MEMBER_IN_SET - The object is already part of the set.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - MEMBER_NOT_IN_SET - The object is not part of the set.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - MEMBER_NOT_IN_SAME_DOMAIN - Objects must be in the same domain
            to perform this operation.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_DUP_NAME - Invalid input (duplicate name).
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_PARAM_CONFLICT - Invalid input (parameters cannot be
            present at the same time).
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_ILLEGAL_CHAR - Invalid contains one or more illegal
            characters.
        """
        return self.client.modifyHostSet(name, action, newName, comment,
                                         setmembers)

    def addHostToHostSet(self, set_name, name):
        """
        This adds a host to a host set.

        :param set_name: the host set name
        :type set_name: str
        :param name: the host name to add
        :type name: str

        :returns: headers - dict of HTTP Response headers.  Upon successful
                  modification of a host set HTTP code 200 OK is returned and
                  the URI of the updated host set will be returned in the
                  location portion of the headers.
        :returns: body - the body of the response.  None if successful.
        """
        return self.client.addHostToHostSet(set_name, name)

    def removeHostFromHostSet(self, set_name, name):
        """
        Remove a host from a host set.

        :param set_name: the host set name
        :type set_name: str
        :param name: the host name to remove
        :type name: str

        :returns: headers - dict of HTTP Response headers.  Upon successful
                  modification of a host set HTTP code 200 OK is returned and
                  the URI of the updated host set will be returned in the
                  location portion of the headers.
        :returns: body - the body of the response.  None if successful.
        """
        return self.client.removeHostFromHostSet(set_name, name)

    def removeHostFromItsHostSet(self, name):
        """
        Remove a host from its host set if it is a member of one.

        :param name: the host name to remove
        :type name: str

        :returns: None if host has no host set, else (headers, body)
        :returns: headers - dict of HTTP Response headers.  Upon successful
                  modification of a host set HTTP code 200 OK is returned and
                  the URI of the updated host set will be returned in the
                  location portion of the headers.
        :returns: body - the body of the response.  None if successful.
        """
        return self.client.removeHostFromItsHostSet(name)

    def getHosts(self):
        """Get information about every Host on the 3Par array.

        :returns: list of Hosts
        """
        host_list = []
        hosts = self.client.getHosts()['members']
        for host in hosts:
            host_list.append(Host(host))
        return host_list

    def getHost(self, name):
        """Get information about a Host.

        :param name: The name of the Host to find
        :type name: str

        :returns: host dict
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_HOST - HOST doesn't exist

        """
        return Host(self.client.getHost(name))

    def createHost(self, name, iscsiNames=None, FCWwns=None, optional=None):
        """Create a new Host entry.

        :param name: The name of the host
        :type name: str
        :param iscsiNames: Array if iscsi iqns
        :type name: array
        :param FCWwns: Array if Fibre Channel World Wide Names
        :type name: array
        :param optional: The optional stuff
        :type optional: dict

        .. code-block:: python

            optional = {
                'persona': 1,                   # ID of the persona to assign
                                                # to the host.
                                                # 3.1.3 default: Generic-ALUA
                                                # 3.1.2 default: General
                'domain': 'myDomain',           # Create the host in the
                                                # specified domain, or default
                                                # domain if unspecified.
                'forceTearDown': False,         # If True, force to tear down
                                                # low-priority VLUN exports.
                'descriptors':
                    {'location': 'earth',       # The host's location
                     'IPAddr': '10.10.10.10',   # The host's IP address
                     'os': 'linux',             # The operating system running
                                                # on the host.
                     'model': 'ex',             # The host's model
                     'contact': 'Smith',        # The host's owner and contact
                     'comment': "Joe's box"}    # Additional host information
            }

        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - PERM_DENIED - Permission denied
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_MISSING_REQUIRED - Name not specified.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_PARAM_CONFLICT - FCWWNs and iSCSINames are both
            specified.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_EXCEEDS_LENGTH - Host name, domain name, or iSCSI name
            is too long.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_EMPTY_STR - Input string (for domain name, iSCSI name,
            etc.) is empty.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_ILLEGAL_CHAR - Any error from host-name or domain-name
            parsing.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_TOO_MANY_WWN_OR_iSCSI - More than 1024 WWNs or iSCSI
            names are specified.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_WRONG_TYPE - The length of WWN is not 16. WWN
            specification contains non-hexadecimal digit.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - EXISTENT_PATH - host WWN/iSCSI name already used by another host
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - EXISTENT_HOST - host name is already used.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - NO_SPACE - No space to create host.

        """
        return self.client.createHost(name, iscsiNames, FCWwns, optional)

    def modifyHost(self, name, mod_request):
        """Modify an existing Host entry.

        :param name: The name of the host
        :type name: str
        :param mod_request: Objects for Host Modification Request
        :type mod_request: dict

        .. code-block:: python

            mod_request = {
                'newName': 'myNewName',         # New name of the host
                'pathOperation': 1,             # If adding, adds the WWN or
                                                # iSCSI name to the existing
                                                # host.
                'FCWWNs': [],                   # One or more WWN to set for
                                                # the host.
                'iSCSINames': [],               # One or more iSCSI names to
                                                # set for the host.
                'forcePathRemoval': False,      # If True, remove SSN(s) or
                                                # iSCSI(s) even if there are
                                                # VLUNs exported to host
                'persona': 1,                   # ID of the persona to modify
                                                # the host's persona to.
                'descriptors':
                    {'location': 'earth',       # The host's location
                     'IPAddr': '10.10.10.10',   # The host's IP address
                     'os': 'linux',             # The operating system running
                                                # on the host.
                     'model': 'ex',             # The host's model
                     'contact': 'Smith',        # The host's owner and contact
                     'comment': 'Joes box'}     # Additional host information
                'chapOperation': HOST_EDIT_ADD, # Add or remove
                'chapOperationMode': CHAP_INITIATOR, # Initator or target
                'chapName': 'MyChapName',       # The chap name
                'chapSecret': 'xyz',            # The chap secret for the host
                                                # or the target
                'chapSecretHex': False,         # If True, the chapSecret is
                                                # treated as Hex.
                'chapRemoveTargetOnly': True    # If True, then remove target
                                                # chap only
            }

        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT - Missing host name.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_PARAM_CONFLICT - Both iSCSINames & FCWWNs are
            specified. (lot of other possibilities)
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_ONE_REQUIRED - iSCSINames or FCWwns missing.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_ONE_REQUIRED - No path operation specified.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_BAD_ENUM_VALUE - Invalid enum value.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_MISSING_REQUIRED - Required fields missing.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_EXCEEDS_LENGTH - Host descriptor argument length, new
            host name, or iSCSI name is too long.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_ILLEGAL_CHAR - Error parsing host or iSCSI name.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - EXISTENT_HOST - New host name is already used.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_HOST - Host to be modified does not exist.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_TOO_MANY_WWN_OR_iSCSI - More than 1024 WWNs or iSCSI
            names are specified.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_WRONG_TYPE - Input value is of the wrong type.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - EXISTENT_PATH - WWN or iSCSI name is already claimed by other
            host.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_BAD_LENGTH - CHAP hex secret length is not 16 bytes, or
            chap ASCII secret length is not 12 to 16 characters.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NO_INITIATOR_CHAP - Setting target CHAP without initiator CHAP.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_CHAP - Remove non-existing CHAP.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - NON_UNIQUE_CHAP_SECRET - CHAP secret is not unique.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - EXPORTED_VLUN - Setting persona with active export; remove a host
            path on an active export.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - NON_EXISTENT_PATH - Remove a non-existing path.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - LUN_HOSTPERSONA_CONFLICT - LUN number and persona capability
            conflict.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_DUP_PATH - Duplicate path specified.

        """
        return self.client.modifyHost(name, mod_request)

    def deleteHost(self, name):
        """Delete a Host.

        :param name: Host Name
        :type name: str

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_HOST - HOST Not Found
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            -  IN_USE - The HOST Cannot be removed because it's in use.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - PERM_DENIED - Permission denied

        """
        self.client.deleteHost(name)

    def findHost(self, iqn=None, wwn=None):
        """Find a host from an iSCSI initiator or FC WWN.

        :param iqn: lookup based on iSCSI initiator
        :type iqn: str
        :param wwn: lookup based on WWN
        :type wwn: str

        """
        return self.client.findHost(iqn, wwn)

    def queryHost(self, iqns=None, wwns=None):
        """Find a host from an iSCSI initiator or FC WWN.

        :param iqns: lookup based on iSCSI initiator list
        :type iqns: list
        :param wwns: lookup based on WWN list
        :type wwns: list

        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT - Invalid URI syntax.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_HOST - HOST Not Found
        :raises: :class:`~hpe3parclient.exceptions.HTTPInternalServerError`
            - INTERNAL_SERVER_ERR - Internal server error.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_ILLEGAL_CHAR - Host name contains invalid character.

        """
        host_list = []
        hosts = self.client.queryHost(iqns, wwns)['members']
        for host in hosts:
            host_list.append(Host(host))
        return host_list

    def getHostVLUNs(self, hostName):
        """Get all of the VLUNs on a specific Host.

        :param hostName: Host name
        :type hostNane: str

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_HOST - HOST Not Found

        """
        vlun_list = []
        vluns = self.client.getHostVLUNs(hostName)
        for vlun in vluns:
            vlun_list.append(VLUN(vlun))
        return vlun_list

    # PORT Methods
    def getPorts(self):
        """Get the list of ports on the 3PAR.

        :returns: list of Ports

        """
        port_list = []
        ports = self.client.getPorts()['members']
        for port in ports:
            port_list.append(Port(port))
        return port_list

    def _getProtocolPorts(self, protocol, state=None):
        port_list = []
        ports = self.client._getProtocolPorts(protocol, state)
        for port in ports:
            port_list.append(Port(port))
        return port_list

    def getFCPorts(self, state=None):
        """Get a list of Fibre Channel Ports.

        :returns: list of Fibre Channel Ports

        """
        fc_port_list = []
        ports = self.client.getFCPorts(state)
        for port in ports:
            fc_port_list.append(Port(port))
        return fc_port_list

    def getiSCSIPorts(self, state=None):
        """Get a list of iSCSI Ports.

        :returns: list of iSCSI Ports

        """
        iscsi_port_list = []
        ports = self.client.getiSCSIPorts(state)
        for port in ports:
            iscsi_port_list.append(Port(port))
        return iscsi_port_list

    def getIPPorts(self, state=None):
        """Get a list of IP Ports.

        :returns: list of IP Ports

        """
        ip_port_list = []
        ports = self.client.getIPPorts(state)
        for port in ports:
            ip_port_list.append(Port(port))
        return ip_port_list

    # CPG methods
    def getCPGs(self):
        """Get entire list of CPGs.

        :returns: list of cpgs

        """
        cpg_list = []
        cpgs = self.client.getCPGs()['members']
        for cpg in cpgs:
            cpg_list.append(CPG(cpg))
        return cpg_list

    def getCPG(self, name):
        """Get information about a CPG.

        :param name: The name of the CPG to find
        :type name: str

        :returns: cpg dict
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            -  NON_EXISTENT_CPG - CPG doesn't exist

        """
        return CPG(self.client.getCPG(name))

    def getCPGAvailableSpace(self, name):
        """Get available space information about a CPG.

        :param name: The name of the CPG to find
        :type name: str

        :returns: Available space dict

        .. code-block:: python

            info = {
                "rawFreeMiB": 1000000,    # Raw free capacity in MiB
                "usableFreeMiB": 5000     # LD free capacity in MiB
            }

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_CPG - CPG Not Found

        """
        return LDLayoutCapacity(self.client.getCPGAvailableSpace(name))

    def createCPG(self, name, optional=None):
        """Create a CPG.

        :param name: CPG Name
        :type name: str
        :param optional: Optional parameters
        :type optional: dict

        .. code-block:: python

            optional = {
                'growthIncrementMiB': 100,    # Growth increment in MiB for
                                              # each auto-grown operation
                'growthLimitMiB': 1024,       # Auto-grow operation is limited
                                              # to specified storage amount
                'usedLDWarningAlertMiB': 200, # Threshold to trigger warning
                                              # of used logical disk space
                'domain': 'MyDomain',         # Name of the domain object
                'LDLayout': {
                    'RAIDType': 1,            # Disk Raid Type
                    'setSize': 100,           # Size in number of chunklets
                    'HA': 0,                  # Layout supports failure of
                                              # one port pair (1),
                                              # one cage (2),
                                              # or one magazine (3)
                    'chunkletPosPref': 2,     # Chunklet location perference
                                              # characteristics.
                                              # Lowest Number/Fastest transfer
                                              # = 1
                                              # Higher Number/Slower transfer
                                              # = 2
                    'diskPatterns': []}       # Patterns for candidate disks
            }

        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT Invalid URI Syntax.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - NON_EXISTENT_DOMAIN - Domain doesn't exist.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - NO_SPACE - Not Enough space is available.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - BAD_CPG_PATTERN  A Pattern in a CPG specifies illegal values.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - PERM_DENIED - Permission denied
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - EXISTENT_CPG - CPG Exists already

        """
        return self.client.createCPG(name, optional)

    def deleteCPG(self, name):
        """Delete a CPG.

        :param name: CPG Name
        :type name: str

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_CPG - CPG Not Found
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            -  IN_USE - The CPG Cannot be removed because it's in use.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - PERM_DENIED - Permission denied

        """
        self.client.deleteCPG(name)

    # VLUN methods
    #
    # Virtual-LUN, or VLUN, is a pairing between a virtual volume and a
    # logical unit number (LUN), expressed as either a VLUN template or
    # an active VLUN.
    # A VLUN template sets up an association between a virtual volume and a
    # LUN-host, LUN-port, or LUN-host-port combination by establishing the
    # export rule or the manner in which the Volume is exported.

    def getVLUNs(self):
        """Get VLUNs.

        :returns: Array of VLUNs

        """
        vlun_list = []
        vluns = self.client.getVLUNs()['members']
        for vlun in vluns:
            vlun_list.append(VLUN(vlun))
        return vlun_list

    def getVLUN(self, volumeName):
        """Get information about a VLUN.

        :param volumeName: The volume name of the VLUN to find
        :type name: str

        :returns: VLUN

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            -  NON_EXISTENT_VLUN - VLUN doesn't exist

        """
        return VLUN(self.client.getVLUN(volumeName))

    def createVLUN(self, volumeName, lun=None, hostname=None, portPos=None,
                   noVcn=None, overrideLowerPriority=None, auto=False):
        """Create a new VLUN.

        When creating a VLUN, the volumeName is required. The lun member is
        not required if auto is set to True.
        Either hostname or portPos (or both in the case of matched sets) is
        also required.  The noVcn and overrideLowerPriority members are
        optional.

        :param volumeName: Name of the volume to be exported
        :type volumeName: str
        :param lun: The new LUN id
        :type lun: int
        :param hostname:  Name of the host which the volume is to be exported.
        :type hostname: str
        :param portPos: 'portPos' (dict) - System port of VLUN exported to. It
                        includes node number, slot number, and card port number
        :type portPos: dict
        .. code-block:: python

            portPos = {'node': 1,   # System node (0-7)
                       'slot': 2,   # PCI bus slot in the node (0-5)
                       'port': 1}   # Port number on the FC card (0-4)

        :param noVcn: A VLUN change notification (VCN) not be issued after
                      export (-novcn). Default: False.
        :type noVcn: bool
        :param overrideLowerPriority: Existing lower priority VLUNs will
                be overridden (-ovrd). Use only if hostname member exists.
                Default: False.
        :type overrideLowerPriority: bool

        :returns: the location of the VLUN

        """

        return self.client.createVLUN(volumeName, lun, hostname, portPos,
                                      noVcn, overrideLowerPriority, auto)

    def deleteVLUN(self, volumeName, lunID, hostname=None, port=None):
        """Delete a VLUN.

        :param volumeName: the volume name of the VLUN
        :type name: str
        :param lunID: The LUN ID
        :type lunID: int
        :param hostname: Name of the host which the volume is exported.
                         For VLUN of port type,the value is empty
        :type hostname: str
        :param port: Specifies the system port of the VLUN export.  It includes
                     the system node number, PCI bus slot number, and card port
                     number on the FC card in the format
                     <node>:<slot>:<cardPort>
        :type port: dict
        .. code-block:: python

            port = {'node': 1,   # System node (0-7)
                    'slot': 2,   # PCI bus slot in the node (0-5)
                    'port': 1}   # Port number on the FC card (0-4)

        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_MISSING_REQUIRED - Incomplete VLUN info. Missing
            volumeName or lun, or both hostname and port.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_PORT_SELECTION - Specified port is invalid.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_EXCEEDS_RANGE - The LUN specified exceeds expected
            range.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_HOST - The host does not exist
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VLUN - The VLUN does not exist
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_PORT - The port does not exist
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - PERM_DENIED - Permission denied
        """

        self.client.deleteVLUN(volumeName, lunID, hostname, port)

    # VolumeSet methods
    def findVolumeSet(self, name):
        """
        Find the first Volume Set that contains a target volume.  If a
        volume set other than the first one found is desired use
        findAllVolumeSets and search the results.

        :param name: the volume name
        :type name: str

        :returns: The name of the first volume set that contains the target
        volume, otherwise None.
        """
        return self.client.findVolumeSet(name)

    def findAllVolumeSets(self, name):
        """
        Return a list of every Volume Set the given volume is a part of.
        The list can contain zero, one, or multiple items.

        :param name: the volume name
        :type name: str

        :returns: a list of Volume Set dicts

        .. code-block:: python

            vvset_names = [{
                'name': "volume_set_1",       # The name of the volume set
                'comment': 'Samplet VVSet',   # The volume set's comment
                'domain': 'my_domain',        # The volume set's domain
                'setmembers': ['V1', 'V2']    # List of strings containing
                                              # the volumes that are members
                                              # of this volume set
            },
            ...
            ]

        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_IN_INCONSISTENT_STATE - Internal inconsistency error in vol
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_IS_BEING_REMOVED - The volume is being removed
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOLUME - The volume does not exists
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_SYS_VOLUME - Illegal op on system vol
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_INTERNAL_VOLUME - Illegal op on internal vol
        """
        volume_set_list = []
        volume_sets = self.client.findAllVolumeSets(name)
        for volume_set in volume_sets:
            volume_set_list.append(VolumeSet(volume_set))
        return volume_set_list

    def getVolumeSets(self):
        """
        Get Volume Sets

        :returns: Array of Volume Sets
        """
        volume_set_list = []
        volume_sets = self.client.getVolumeSets()['members']
        for volume_set in volume_sets:
            volume_set_list.append(VolumeSet(volume_set))
        return volume_set_list

    def getVolumeSet(self, name):
        """
        Get information about a Volume Set

        :param name: The name of the Volume Set to find
        :type name: str

        :returns: Volume Set

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_SET - The set doesn't exist
        """
        return VolumeSet(self.client.getVolumeSet(name))

    def createVolumeSet(self, name, domain=None, comment=None,
                        setmembers=None):
        """
        This creates a new volume set

        :param name: the volume set to create
        :type set_name: str
        :param domain: the domain where the set lives
        :type domain: str
        :param comment: the comment for on the vv set
        :type comment: str
        :param setmembers: the vv to add to the set, the existence of the vv
        will not be checked
        :type setmembers: array

        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - EXISTENT_SET - The set already exits.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - MEMBER_IN_DOMAINSET - The host is in a domain set.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - MEMBER_IN_SET - The object is already part of the set.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - MEMBER_NOT_IN_SAME_DOMAIN - Objects must be in the same domain to
            perform this operation.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_IN_INCONSISTENT_STATE - The volume has an internal
            inconsistency error.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_IS_BEING_REMOVED - The volume is being removed.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOLUME - The volume does not exists.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_HOST - The host does not exists.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_SYS_VOLUME - The operation is not allowed on a
            system volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_INTERNAL_VOLUME - The operation is not allowed
            on an internal volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_DUP_NAME - Invalid input (duplicate name).
        """
        self.client.createVolumeSet(
            name, domain, comment, setmembers)

    def deleteVolumeSet(self, name):
        """
        This removes a volume set. You must clear all QOS rules before a volume
        set can be deleted.

        :param name: the volume set to remove
        :type name: str

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_SET - The set does not exists.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - EXPORTED_VLUN - The host set has exported VLUNs. The VV set was
            exported.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - VVSET_QOS_TARGET - The object is already part of the set.
        """
        self.client.deleteVolumeSet(name)

    def modifyVolumeSet(self, name, action=None, newName=None, comment=None,
                        flashCachePolicy=None, setmembers=None):
        """
        This modifies a volume set by adding or remove a volume from the volume
        set. It's actions is based on the enums SET_MEM_ADD or SET_MEM_REMOVE.

        :param action: add or remove volume from the set
        :type action: enum
        :param name: the volume set name
        :type name: str
        :param newName: new name of set
        :type newName: str
        :param comment: the comment for on the vv set
        :type comment: str
        :param flashCachePolicy: the flash-cache policy for the vv set
        :type comment: FLASH_CACHED_ENABLED or FLASH_CACHE_DISABLED
        :param setmembers: the vv to add to the set, the existence of the vv
                           will not be checked
        :type setmembers: array

        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - EXISTENT_SET - The set already exits.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_SET - The set does not exists.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - MEMBER_IN_DOMAINSET - The host is in a domain set.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - MEMBER_IN_SET - The object is already part of the set.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - MEMBER_NOT_IN_SET - The object is not part of the set.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - MEMBER_NOT_IN_SAME_DOMAIN - Objects must be in the same domain to
            perform this operation.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_IN_INCONSISTENT_STATE - The volume has an internal
            inconsistency error.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_IS_BEING_REMOVED - The volume is being removed.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOLUME - The volume does not exists.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_SYS_VOLUME - The operation is not allowed on a
            system volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_INTERNAL_VOLUME - The operation is not allowed
            on an internal volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_DUP_NAME - Invalid input (duplicate name).
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_PARAM_CONFLICT - Invalid input (parameters cannot be
            present at the same time).
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_ILLEGAL_CHAR - Invalid contains one or more illegal
            characters.
        """
        return self.client.modifyVolumeSet(name, action, newName, comment,
                                           flashCachePolicy, setmembers)

    # QoS Priority Optimization methods
    def addVolumeToVolumeSet(self, set_name, name):
        """
        This adds a volume to a volume set

        :param set_name: the volume set name
        :type set_name: str
        :param name: the volume name to add
        :type name: str
        """
        return self.client.addVolumeToVolumeSet(set_name, name)

    def removeVolumeFromVolumeSet(self, set_name, name):
        """
        Remove a volume from a volume set

        :param set_name: the volume set name
        :type set_name: str
        :param name: the volume name to add
        :type name: str
        """
        return self.client.removeVolumeFromVolumeSet(set_name, name)

    def createSnapshotOfVolumeSet(self, name, copyOfName, optional=None):
        """Create a snapshot of an existing Volume Set.

        :param name: Name of the Snapshot. The vvname pattern is described in
                     "VV Name Patterns" in the HPE 3PAR Command Line Interface
                     Reference, which is available at the following
                     website: http://www.hp.com/go/storage/docs
        :type name: str
        :param copyOfName: The volume set you want to snapshot
        :type copyOfName: str
        :param optional: Dictionary of optional params
        :type optional: dict

        .. code-block:: python

            optional = {
                'id': 12,                   # Specifies ID of the volume set
                                            # set, next by default
                'comment': "some comment",
                'readOnly': True,           # Read Only
                'expirationHours': 36,      # time from now to expire
                'retentionHours': 12        # time from now to expire
            }

        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INVALID_INPUT_VV_PATTERN - Invalid volume pattern specified
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_SET - The set does not exist
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - EMPTY_SET - The set is empty
        :raises: :class:`~hpe3parclient.exceptions.HTTPServiceUnavailable`
            - VV_LIMIT_REACHED - Maximum number of volumes reached
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOL - The storage volume does not exist
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_IS_BEING_REMOVED - The volume is being removed
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_READONLY_TO_READONLY_SNAP - Creating a
            read-only copy from a read-only volume is not permitted
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - NO_SNAP_CPG - No snapshot CPG has been configured for the volume
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_DUP_NAME - Invalid input (duplicate name).
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_SNAP_PARENT_SAME_BASE - Two parent
            snapshots share thesame base volume
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_ONLINE_COPY_IN_PROGRESS - Invalid
            operation. Online copyis in progress
        :raises: :class:`~hpe3parclient.exceptions.HTTPServiceUnavailable`
            - VV_ID_LIMIT_REACHED - Max number of volumeIDs has been reached
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOLUME - The volume does not exists
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_IN_STALE_STATE - The volume is in a stale state.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_NOT_STARTED - Volume is not started
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_UNAVAILABLE - The volume is not accessible
        :raises: :class:`~hpe3parclient.exceptions.HTTPServiceUnavailable`
            - SNAPSHOT_LIMIT_REACHED - Max number of snapshots has been reached
        :raises: :class:`~hpe3parclient.exceptions.HTTPServiceUnavailable`
            - CPG_ALLOCATION_WARNING_REACHED - The CPG has reached the
            allocation warning
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_VOLUME_CONV_IN_PROGRESS - Invalid operation: VV
            conversion is in progress.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_CLEANUP_IN_PROGRESS - Internal volume cleanup is
            in progress.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_PEER_VOLUME - Cannot modify a peer volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - INV_OPERATION_VV_ONLINE_COPY_IN_PROGRESS  - The volume is the
            target of an online copy.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_INTERNAL_VOLUME - Illegal op on internal vol
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - EXISTENT_ID - An ID exists
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_NOT_IN_NORMAL_STATE - Volume state is not normal
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - VV_IN_INCONSISTENT_STATE - Internal inconsistency error in vol
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_RETAIN_GT_EXPIRE - Retention time is greater than
            expiration time.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_TIME - Invalid time specified.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_SNAPSHOT_NOT_SAME_TYPE - Some snapshots in the
            volume set are read-only, some are read-write
        """
        return self.client.createSnapshotOfVolumeSet(name, copyOfName,
                                                     optional)

    # QoS Priority Optimization methods
    def setQOSRule(self, set_name, max_io=None, max_bw=None):
        """
        Set a QOS Rule on a volume set

        :param set_name: the volume set name for the rule.
        :type set_name: str
        :param max_io: the maximum IOPS value
        :type max_io: int
        :param max_bw: The maximum Bandwidth
        :type max_bw:
        """
        self.client.setQOSRule(set_name, max_io, max_bw)

    def queryQoSRules(self):
        """
        Get QoS Rules

        :returns: Array of QoS Rules
        """
        qos_rules_list = []
        qos_rules = self.client.queryQoSRules()['members']
        for qos_rule in qos_rules:
            qos_rules_list.append(QoSRule(qos_rule))
        return qos_rules_list

    def queryQoSRule(self, targetName, targetType='vvset'):
        """
        Query a QoS rule

        :param targetType: target type is vvset or sys
        :type targetType: str
        :param targetName: the name of the target. When targetType is sys,
                           target name must be sys:all_others.
        :type targetName: str

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
           - NON_EXISTENT_QOS_RULE - QoS rule does not exist.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
           - INV_INPUT_ILLEGAL_CHAR - Illegal character in the input.
        """
        return QoSRule(self.client.queryQoSRule(targetName, targetType))

    def createQoSRules(self, targetName, qosRules,
                       target_type=client.HPE3ParClient.TARGET_TYPE_VVSET):
        """
        Create QOS rules

        The QoS rule can be applied to VV sets. By using sys:all_others,
        you can apply the rule to all volumes in the system for which no
        QoS rule has been defined.

        ioMinGoal and ioMaxLimit must be used together to set I/O limits.
        Similarly, bwMinGoalKB and bwMaxLimitKB must be used together.

        If ioMaxLimitOP is set to 2 (no limit), ioMinGoalOP must also be
        to set to 2 (zero), and vice versa. They cannot be set to
        'none' individually. Similarly, if bwMaxLimitOP is set to 2 (no
        limit), then bwMinGoalOP must also be set to 2.

        If ioMaxLimitOP is set to 1 (no limit), ioMinGoalOP must also be
        to set to 1 (zero) and vice versa. Similarly, if bwMaxLimitOP is
        set to 1 (zero), then bwMinGoalOP must also be set to 1.

        The ioMinGoalOP and ioMaxLimitOP fields take precedence over
        the ioMinGoal and ioMaxLimit fields.

        The bwMinGoalOP and bwMaxLimitOP fields take precedence over
        the bwMinGoalKB and bwMaxLimitKB fields

        :param target_type: Type of QoS target, either enum
                            TARGET_TYPE_VVS or TARGET_TYPE_SYS.
        :type target_type: enum
        :param targetName: the name of the target object on which the QoS
                           rule will be created.
        :type targetName: str
        :param qosRules: QoS options
        :type qosRules: dict

        .. code-block:: python

            qosRules = {
                'priority': 2,         # priority enum
                'bwMinGoalKB': 1024,   # bandwidth rate minimum goal in
                                       #   kilobytes per second
                'bwMaxLimitKB': 1024,  # bandwidth rate maximum limit in
                                       #   kilobytes per second
                'ioMinGoal': 10000,    # I/O-per-second minimum goal
                'ioMaxLimit': 2000000, # I/0-per-second maximum limit
                'enable': True,        # QoS rule for target enabled?
                'bwMinGoalOP': 1,      # zero none operation enum, when set to
                                       #   1, bandwidth minimum goal is 0
                                       # when set to 2, the bandwidth mimumum
                                       #   goal is none (NoLimit)
                'bwMaxLimitOP': 1,     # zero none operation enum, when set to
                                       #   1, bandwidth maximum limit is 0
                                       # when set to 2, the bandwidth maximum
                                       #   limit is none (NoLimit)
                'ioMinGoalOP': 1,      # zero none operation enum, when set to
                                       #   1, I/O minimum goal is 0
                                       # when set to 2, the I/O minimum goal is
                                       #   none (NoLimit)
                'ioMaxLimitOP': 1,     # zero none operation enum, when set to
                                       #   1, I/O maximum limit is 0
                                       # when set to 2, the I/O maximum limit
                                       #   is none (NoLimit)
                'latencyGoal': 5000,   # Latency goal in milliseconds
                'defaultLatency': False # Use latencyGoal or defaultLatency?
            }

        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
          - INV_INPUT_EXCEEDS_RANGE - Invalid input: number exceeds expected
          range.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
          - NON_EXISTENT_QOS_RULE - QoS rule does not exists.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
          - INV_INPUT_ILLEGAL_CHAR - Illegal character in the input.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
          - EXISTENT_QOS_RULE - QoS rule already exists.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
          - INV_INPUT_MIN_GOAL_GRT_MAX_LIMIT - I/O-per-second maximum limit
          should be greater than the minimum goal.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
          - INV_INPUT_BW_MIN_GOAL_GRT_MAX_LIMIT - Bandwidth maximum limit
          should be greater than the mimimum goal.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
          - INV_INPUT_BELOW_RANGE - I/O-per-second limit is below range.
          Bandwidth limit is below range.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
          - UNLICENSED_FEATURE - The system is not licensed for QoS.
        """
        if qosRules is not None and self.CURRENT_WSAPI_VERSION < self.WSAPI_MIN_SUPPORTED_VERSION:
            if 'latencyGoaluSecs' in qos_rules.keys():
                del qos_rules['latencyGoaluSecs']
        return self.client.createQoSRules(targetName, qosRules, target_type)

    def modifyQoSRules(self, targetName, qosRules, targetType='vvset'):
        """
        Modify an existing QOS rules

        The QoS rule can be applied to VV sets. By using sys:all_others,
        you can apply the rule to all volumes in the system for which no
        QoS rule has been defined.

        ioMinGoal and ioMaxLimit must be used together to set I/O limits.
        Similarly, bwMinGoalKB and bwMaxLimitKB must be used together.

        If ioMaxLimitOP is set to 2 (no limit), ioMinGoalOP must also be
        to set to 2 (zero), and vice versa. They cannot be set to
        'none' individually. Similarly, if bwMaxLimitOP is set to 2 (no
        limit), then bwMinGoalOP must also be set to 2.

        If ioMaxLimitOP is set to 1 (no limit), ioMinGoalOP must also be
        to set to 1 (zero) and vice versa. Similarly, if bwMaxLimitOP is
        set to 1 (zero), then bwMinGoalOP must also be set to 1.

        The ioMinGoalOP and ioMaxLimitOP fields take precedence over
        the ioMinGoal and ioMaxLimit fields.

        The bwMinGoalOP and bwMaxLimitOP fields take precedence over
        the bwMinGoalKB and bwMaxLimitKB fields

        :param targetName: the name of the target object on which the QoS
                           rule will be created.
        :type targetName: str
        :param targetType: Type of QoS target, either vvset or sys
        :type targetType: str
        :param qosRules: QoS options
        :type qosRules: dict

        .. code-block:: python

            qosRules = {
                'priority': 2,         # priority enum
                'bwMinGoalKB': 1024,   # bandwidth rate minimum goal in
                                       # kilobytes per second
                'bwMaxLimitKB': 1024,  # bandwidth rate maximum limit in
                                       # kilobytes per second
                'ioMinGoal': 10000,    # I/O-per-second minimum goal.
                'ioMaxLimit': 2000000, # I/0-per-second maximum limit
                'enable': True,        # QoS rule for target enabled?
                'bwMinGoalOP': 1,      # zero none operation enum, when set to
                                       # 1, bandwidth minimum goal is 0
                                       # when set to 2, the bandwidth minimum
                                       # goal is none (NoLimit)
                'bwMaxLimitOP': 1,     # zero none operation enum, when set to
                                       # 1, bandwidth maximum limit is 0
                                       # when set to 2, the bandwidth maximum
                                       # limit is none (NoLimit)
                'ioMinGoalOP': 1,      # zero none operation enum, when set to
                                       # 1, I/O minimum goal minimum goal is 0
                                       # when set to 2, the I/O minimum goal is
                                       # none (NoLimit)
                'ioMaxLimitOP': 1,     # zero none operation enum, when set to
                                       # 1, I/O maximum limit is 0
                                       # when set to 2, the I/O maximum limit
                                       # is none (NoLimit)
                'latencyGoal': 5000,   # Latency goal in milliseconds
                'defaultLatency': False # Use latencyGoal or defaultLatency?
            }

        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            INV_INPUT_EXCEEDS_RANGE - Invalid input: number exceeds expected
            range.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            NON_EXISTENT_QOS_RULE - QoS rule does not exists.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            INV_INPUT_ILLEGAL_CHAR - Illegal character in the input.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            EXISTENT_QOS_RULE - QoS rule already exists.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            INV_INPUT_IO_MIN_GOAL_GRT_MAX_LIMIT - I/O-per-second maximum limit
            should be greater than the minimum goal.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            INV_INPUT_BW_MIN_GOAL_GRT_MAX_LIMIT - Bandwidth maximum limit
            should be greater than the minimum goal.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            INV_INPUT_BELOW_RANGE - I/O-per-second limit is below
            range. Bandwidth limit is below range.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
                     UNLICENSED_FEATURE - The system is not licensed for QoS.
        """
        if qosRules is not None and self.CURRENT_WSAPI_VERSION < self.WSAPI_MIN_SUPPORTED_VERSION:
            if 'latencyGoaluSecs' in qos_rules.keys():
                del qos_rules['latencyGoaluSecs']
        return self.client.modifyQoSRules(targetName, qosRules, targetType)

    def deleteQoSRules(self, targetName, targetType='vvset'):
        """Clear and Delete QoS rules.

        :param targetType: target type is vvset or sys
        :type targetType: str
        :param targetName: the name of the target. When targetType is sys,
                           target name must be sys:all_others.
        :type targetName: str

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound` -
                        NON_EXISTENT_QOS_RULE - QoS rule does not exist.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest` -
                        INV_INPUT_ILLEGAL_CHAR - Illegal character in the input

        """
        return self.client.deleteQoSRules(targetName, targetType)

    def setVolumeMetaData(self, name, key, value):
        """This is used to set a key/value pair metadata into a volume.
        If the key already exists on the volume the value will be updated.

        :param name: the volume name
        :type name: str
        :param key: the metadata key name
        :type key: str
        :param value: the metadata value
        :type value: str


        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_EXCEEDS_LENGTH - Invalid input: string length exceeds
            limit.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_MISSING_REQUIRED - Required fields missing
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_UNREC_NAME - Unrecognized name
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_ILLEGAL_CHAR - Illegal character in input
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOL - The volume does not exist

        """
        return self.client.setVolumeMetaData(name, key, value)

    def getVolumeMetaData(self, name, key):
        """This is used to get a key/value pair metadata from a volume.

        :param name: the volume name
        :type name: str
        :param key: the metadata key name
        :type key: str

        :returns: dict with the requested key's data.

        .. code-block:: python

            data = {
                # time of creation in seconds format
                'creationTimeSec': 1406074222
                # the date/time the key was added
                'date_added': 'Mon Jul 14 16:09:36 PDT 2014',
                'value': 'data'     # the value associated with the key
                'key': 'key_name'   # the key name
                # time of creation in date format
                'creationTime8601': '2014-07-22T17:10:22-07:00'
            }

        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_ILLEGAL_CHAR - Illegal character in input
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOL - The volume does not exist
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_OBJECT_KEY - Object key does not exist

        """
        return self.client.getVolumeMetaData(name, key)

    def getAllVolumeMetaData(self, name):
        """This is used to get all key/value pair metadata from a volume.

        :param name: the volume name
        :type name: str

        :returns: dict with all keys and associated data.

        .. code-block:: python

            keys = {
                'total': 2,
                'members': [
                    {
                        # time of creation in seconds format
                        'creationTimeSec': 1406074222
                        # the date/time the key was added
                        'date_added': 'Mon Jul 14 16:09:36 PDT 2014',
                        'value': 'data'     # the value associated with the key
                        'key': 'key_name'   # the key name
                        # time of creation in date format
                        'creationTime8601': '2014-07-22T17:10:22-07:00'
                    },
                    {
                        # time of creation in seconds format
                        'creationTimeSec': 1406074222
                        # the date/time the key was added
                        'date_added': 'Mon Jul 14 16:09:36 PDT 2014',
                        'value': 'data'     # the value associated with the key
                        'key': 'key_name_2' # the key name
                        # time of creation in date format
                        'creationTime8601': '2014-07-22T17:10:22-07:00'
                    }
                ]
            }

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOL - The volume does not exist

        """
        return self.client.getAllVolumeMetaData(name)

    def removeVolumeMetaData(self, name, key):
        """This is used to remove a metadata key/value pair from a volume.

        :param name: the volume name
        :type name: str
        :param key: the metadata key name
        :type key: str

        :returns: None

        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_ILLEGAL_CHAR - Illegal character in input
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOL - The volume does not exist
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_OBJECT_KEY - Object key does not exist

        """
        return self.client.removeVolumeMetaData(name, key)

    def findVolumeMetaData(self, name, key, value):
        """Determines whether a volume contains a specific key/value pair.

        :param name: the volume name
        :type name: str
        :param key: the metadata key name
        :type key: str
        :param value: the metadata value
        :type value: str

        :returns: bool

        """
        return self.client.findVolumeMetaData(name, key, value)

    def getRemoteCopyInfo(self):
        """
        Querying Overall Remote-Copy Information

        :returns: Overall Remote Copy Information
        """
        return self.client.getRemoteCopyInfo()

    def getRemoteCopyGroups(self):
        """
        Returns information on all Remote Copy Groups

        :returns: list of Remote Copy Groups

        """
        return self.client.getRemoteCopyGroups()

    def getRemoteCopyGroup(self, name):
        """
        Returns information on one Remote Copy Group

        :param name: the remote copy group name
        :type name: str

        :returns: Remote Copy Group

        """
        return self.client.getRemoteCopyGroup(name)

    def createRemoteCopyGroup(self, name, targets, optional=None):
        """
        Creates a remote copy group

        :param name: the remote copy group name
        :type name: str
        :param targets: Specifies the attributes of the target of the
                        remote-copy group.
        :type targets: list
        :param optional: dict of other optional items
        :type optional: dict

        .. code-block:: python

            targets = [
                {
                    "targetName": "name",      # Target name associated with
                                               # the remote-copy group to be
                                               # created
                    "mode": 2,                 # Specifies the volume group
                                               # mode.
                                               # 1 - The remote-copy group mode
                                               #     is synchronous.
                                               # 2 - The remote-copy group mode
                                               #     is periodic.
                                               # 3 - The remote-copy group mode
                                               #     is periodic.
                                               # 4 - Remote-copy group mode is
                                               #     asynchronous.
                    "userCPG": "SOME_CPG",     # Specifies the user CPG
                                               # that will be used for
                                               # volumes that are
                                               # autocreated on the
                                               # target.
                    "snapCPG": "SOME_SNAP_CPG" # Specifies the snap CPG
                                               # that will be used for
                                               # volumes that are
                                               # autocreated on the
                                               # target.
                }
            ]

            optional = {
                "localSnapCPG" : "SNAP_CPG",   # Specifies the local snap
                                               # CPG that will be used for
                                               # volumes that are autocreated.
                "localUserCPG" : "SOME_CPG",   # Specifies the local user
                                               # CPG that will be used for
                                               # volumes that are autocreated.
                "domain" : "some-domain"       # Specifies the attributes of
                                               # the target of the
                                               # remote-copy group.
            }

        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_ILLEGAL_CHAR - Invalid character in the remote-copy
            group or volume name.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - EXISTENT_RCOPY_GROUP - The remote-copy group already exists.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - RCOPY_GROUP_TOO_MANY_TARGETS - Too many remote-copy group targets
            have been specified.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_BAD_ENUM_VALUE - The mode is not valid.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - RCOPY_GROUP_TARGET_NOT_UNIQUE - The remote-copy group target is
            not unique.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_IS_NOT_READY - The remote-copy configuration is not ready
            for commands.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_MODE_NOT_SUPPORTED - The remote-copy group mode is
            not supported.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - RCOPY_GROUP_MAX_GROUP_REACHED_PERIODIC - The maximum number of
            remote-copy groups in periodic mode has been reached.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - RCOPY_GROUP_MAX_GROUP_REACHED_PERIODIC - The maximum number of
            remote-copy groups in periodic mode has been reached.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_SECONDARY_GROUP_MORE_THAN_ONE_BACKUP_TARGET -
            Secondary groups should have only one target that is not a
            backup.
        :raises: :class:`~hpe3parclient.exceptions.HTTPServiceUnavailable`
            - RCOPY_GROUP_MORE_THAN_ONE_SYNC_TARGET - Remote-copy groups can
            have no more than one synchronous-mode target.
        :raises: :class:`~hpe3parclient.exceptions.HTTPServiceUnavailable`
            - RCOPY_GROUP_MORE_THAN_ONE_PERIODIC_TARGET - Remote-copy groups
            can have no more than one periodic-mode target.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_ONE_TO_ONE_CONFIG_FOR_MIXED_MODE - Mixed mode is
            supported in a 1-to-1 remote-copy configuration.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_INV_TARGET - The specified target is not a target of
            the remote-copy group.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotImplemented`
            - RCOPY_TARGET_IN_PEER_PERSISTENCE_SYNC_GROUP_ONLY - The
            remote-copy target is configured with peer persistence; only
            synchronous groups can be added.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotImplemented`
            - RCOPY_TARGET_MODE_NOT_SUPPORTED - The remote-copy target
            mode is not supported.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotImplemented`
            - RCOPY_TARGET_MULTI_TARGET_NOT_SUPPORTED - The remote-copy target
            was created in an earlier version of the HP 3PAR OS that does not
            support multiple targets.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotImplemented`
            - RCOPY_TARGET_VOL_AUTO_CREATION_NOT_SUPPORTED - The remote-copy
            target is in an older version of the HP 3PAR OS that does not
            support autocreation of
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - RCOPY_GROUP_MIXED_MODES_ON_ONE_TARGET - Remote-copy groups
            with different modes on a single target are not supported.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_CPG - The CPG does not exists.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - CPG_NOT_IN_SAME_DOMAIN - Snap CPG is not in the same domain as
            the user CPG.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - NON_EXISTENT_DOMAIN - Domain doesn't exist.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_HAS_NO_CPG - No CPG has been defined for the
            remote-copy group on the target.
        :raises: :class:`~hpe3parclient.exceptions.HTTPServiceUnavailable`
            - RCOPY_MAX_SYNC_TARGET_REACHED - The maximum number of remote-copy
            synchronous targets has been reached.
        :raises: :class:`~hpe3parclient.exceptions.HTTPServiceUnavailable`
            - RCOPY_MAX_PERIODIC_TARGET_REACHED - The maximum number of
            remote-copy periodic targets has been reached.
        """
        return self.client.createRemoteCopyGroup(name, targets, optional)

    def removeRemoteCopyGroup(self, name, keep_snap=False):
        """
        Deletes a remote copy group

        :param name: the remote copy group name
        :type name: str
        :param keep_snap: used to retain the local volume resynchronization
                          snapshot. NOTE: to retain the snapshot pass 'true'
                          to keep_snap
        :type keep_snap: bool

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_RCOPY_GROUP - The remote-copy group does not exist.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_STARTED - The remote-copy group has already been
            started.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_IS_BUSY - The remote-copy group is currently busy;
            retry later.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_TARGET_IS_NOT_READY - The remote-copy group target is not
            ready.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_OPERATION_ONLY_ON_PRIMARY_SIDE - The operation
            should be performed only on the primary side.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_RENAME_RESYNC_SNAPSHOT_FAILED - Renaming of the
            remote-copy group resynchronization snapshot failed.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_IN_FAILOVER_STATE - The remote-copy group is in
            failover state; both the source system and the target system
            are in the primary state.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - RCOPY_GROUP_TARGET_VOLUME_MISMATCH - Secondary group on target
            system has a mismatched volume configuration.
        """
        return self.client.removeRemoteCopyGroup(name, keep_snap)

    def modifyRemoteCopyGroup(self, name, optional=None):
        """
        Modifies a remote copy group

        :param name: the remote copy group name
        :type name: str
        :param optional: dict of other optional items
        :type optional: dict

        .. code-block:: python

            optional = {
                "localUserCPG": "CPG",      # Specifies the local user
                                            # CPG that will be used for
                                            # autocreated volumes.
                "localSnapCPG": "SNAP_CPG", # Specifies the local snap
                                            # CPG that will be used for
                                            # autocreated volumes.
                "targets": targets,         # Specifies the attributes of
                                            # the remote-copy group
                                            # target.
                "unsetUserCPG": False,      # If True, this option
                                            # unsets the localUserCPG and
                                            # remoteUserCPG of the
                                            # remote-copy group.
                "unsetSnapCPG": Flase       # If True, this option
                                            # unsets the localSnapCPG and
                                            # remoteSnapCPG of the
                                            # remote-copy group.
            }

            targets = [
                {
                    "targetName": "name",        # Specifies the target name
                                                 # associated with the
                                                 # remote-copy group to be
                                                 # created.
                    "remoteUserCPG": "CPG",      # Specifies the user CPG
                                                 # on the target that will be
                                                 # used for autocreated
                                                 # volumes.
                    "remoteSnapCPG": "SNAP_CPG", # Specifies the snap CPG
                                                 # on the target that will be
                                                 # used for autocreated
                                                 # volumes.
                    "syncPeriod": 300,           # Specifies that asynchronous
                                                 # periodic remote-copy groups
                                                 # should be synchronized
                                                 # periodically to the
                                                 # <period_value>.
                                                 # Range is 300 - 31622400
                                                 # seconds (1 year).
                    "rmSyncPeriod": False,       # If True, this option
                                                 # resets the syncPeriod
                                                 # time to 0 (zero).
                                                 # If False, the
                                                 # syncPeriod value is 0
                                                 # (zero), then Ignore.
                                                 # If False, and the
                                                 # syncPeriod value is
                                                 # positive, then then the
                                                 # synchronizaiton period
                                                 # is set.
                    "mode": 2,                   # Volume group mode. Can be
                                                 # either synchronous or
                                                 # periodic.
                                                 # 1 - The remote-copy group
                                                 #     mode is synchronous.
                                                 # 2 - The remote-copy group
                                                 #     mode is periodic.
                                                 # 3 - The remote-copy group
                                                 #     mode is periodic.
                                                 # 4 - Remote-copy group mode
                                                 #     is asynchronous.
                    "snapFrequency": 300,        # Async mode only. Specifies
                                                 # the interval in seconds at
                                                 # which Remote Copy takes
                                                 # coordinated snapshots. Range
                                                 # is 300-31622400 seconds
                                                 # (1 year).
                    "rmSnapFrequency": False,    # If True, this option resets
                                                 # the snapFrequency time
                                                 # rmSnapFrequency to 0 (zero).
                                                 # If False and the
                                                 # snapFrequency value is 0
                                                 # (zero), then Ignore. If
                                                 # False, and the snapFrequency
                                                 # value is positive, sets the
                                                 # snapFrequency value.
                    "policies": policies         # The policy assigned to
                                                 # the remote-copy group.
                }
            ]

            policies = {
                "autoRecover": False,       # If the remote copy is stopped
                                            # as a result of links going
                                            # down, the remote-copy group
                                            # can be automatically
                                            # restarted after the links
                                            # come back up.
                "overPeriodAlert": False,   # If synchronization of an
                                            # asynchronous periodic
                                            # remote-copy group takes
                                            # longer to complete than its
                                            # synchronization period, an
                                            # alert is generated.
                "autoFailover": False,      # Automatic failover on a
                                            # remote-copy group.
                "pathManagement": False     # Automatic failover on a
                                            # remote-copy group.
            }

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_RCOPY_GROUP - The remote-copy group does not exist.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_OPERATION_ONLY_ON_PRIMARY_SIDE - The operation should
            be performed only on the primary side.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_IS_NOT_PERIODIC - Target in group is not periodic.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_INV_POLICY_FOR_PERIODIC_GROUP - Invalid policy for a
            periodic group.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_INV_POLICY_FOR_SYNC_GROUP - Invalid policy for a
            synchronous target.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_CPG - The CPG does not exists.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_INV_TARGET - The specified target is not a target of
            the remote-copy group.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - CPG_NOT_IN_SAME_DOMAIN - Snap CPG is not in the same domain as
            the user CPG.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_BELOW_RANGE - The minimum allowable period is 300
            seconds.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - INV_INPUT_EXCEEDS_RANGE - Invalid input: the period is too long.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_STARTED - The remote-copy group has already been
            started.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_INV_OPERATION_ON_MULTIPLE_TARGETS - The operation is
            not supported on multiple targets.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - RCOPY_GROUP_TARGET_NOT_UNIQUE - The remote-copy group target is
            not unique.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_INV_TARGET_NUMBER - The wrong number of targets is
            specified for the remote-copy group.
        """
        return self.client.modifyRemoteCopyGroup(name, optional)

    def addVolumeToRemoteCopyGroup(self, name, volumeName, targets,
                                   optional=None):
        """
        Adds a volume to a remote copy group

        :param name: Name of the remote copy group
        :type name: string
        :param volumeName: Specifies the name of the existing virtual
                           volume to be admitted to an existing remote-copy
                           group.
        :type volumeName: string
        :param targets: Specifies the attributes of the target of the
                        remote-copy group.
        :type targets: list
        :param optional: dict of other optional items
        :type optional: dict

        .. code-block:: python

            targets = [
                {
                    "targetName": "name",            # The target name
                                                     # associated with this
                                                     # group.
                    "secVolumeName": "sec_vol_name"  # Specifies the name of
                                                     # the secondary volume
                                                     # on the target system.
                }
            ]

            optional = {
                "snapshotName": "snapshot_name", # The optional read-only
                                                 # snapshotName is a
                                                 # starting snapshot when
                                                 # the group is started
                                                 # without performing a
                                                 # full resynchronization.
                                                 # Instead, for
                                                 # synchronized groups,
                                                 # the volume
                                                 # synchronizes deltas
                                                 # between this
                                                 # snapshotName and
                                                 # the base volume. For
                                                 # periodic groups, the
                                                 # volume synchronizes
                                                 # deltas between this
                                                 # snapshotName and a
                                                 # snapshot of the base.
                "volumeAutoCreation": False,     # If set to true, the
                                                 # secondary volumes
                                                 # should be created
                                                 # automatically on the
                                                 # target using the CPG
                                                 # associated with the
                                                 # remote-copy group on
                                                 # that target.
                "skipInitialSync": False         # If set to true, the
                                                 # volume should skip the
                                                 # initial sync. This is
                                                 # for the admission of
                                                 # volumes that have
                                                 # been pre-synced with
                                                 # the target volume.
            }

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_RCOPY_GROUP - The remote-copy group does not exist.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOL - volume doesn't exist
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_SNAPSHOT - The specified snapshot does not exist.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_SNAPSHOT_IS_RW - The specified snapshot can only be
            read-only.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_VOL_IS_RO - The volume to be admitted to the
            remote-copy group cannot be read-only.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_HAS_NO_CPG - No CPG has been defined for the
            remote-copy group on the target.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - RCOPY_GROUP_EXISTENT_VOL - The specified volume is
            already in the remote-copy group.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - RCOPY_GROUP_EXISTENT_VOL_ON_TARGET - The specified secondary
            volume to be automatically created already exists on the target.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_INV_TARGET - The specified target is not a target of
            the remote-copy group.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_VOL_SIZE_NOT_MATCH - The size of the volume added to
            the remote-copy group does not match the size of the volume on
            the target.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - RCOPY_GROUP_NON_EXISTENT_VOL_ON_TARGET - The specified secondary
            volume does not exist on the target.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_VOL_NO_SNAPSHOT_SPACE - The volume to be admitted
            into the remote-copy group requires that snapshot space be
            allocated.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_TARGET_VOL_NO_SNAPSHOT_SPACE - The specified
            secondary volumes on the target require snapshot space.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_VOL_IS_PHYSICAL_COPY - A physical copy cannot
            be added to a remote-copy group
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_MAX_VOL_REACHED_PERIODIC - The number of
            periodic-mode volumes on the system has reached the limit.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_MAX_VOL_REACHED_SYNC - The number of
            synchronous-mode volumes on the system has reached the limit.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_MAX_VOL_REACHED - The number of volumes on the
            system has reached the limit.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_IS_NOT_READY - The remote-copy configuration is not ready
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_VOL_INTERNAL_CONSISTENCY_ERR - The volume to be
            admitted into the remote-copy group has an internal consistency
            error.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_IS_BEING_REMOVED - The volume to be admitted into the
            remote-copy group is being removed.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUPSNAPSHOT_PARENT_MISMATCH - The names of the snapshot
            and its parent do not match.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_TARGET_VOL_EXPORTED - Secondary volumes cannot be
            admitted when they are exported.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_VOL_IS_PEER_PROVISIONED - A peer-provisioned volume
            cannot be admitted into a remote-copy group.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_VOL_ONLINE_CONVERSION - Online volume conversions do
            not support remote copy.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_VOL_ONLINE_PROMOTE - Online volume promotes do not
            support remote copy.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_VOL_ONLINE_COPY - Online volume copies do not support
            remote copy.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_VOL_CLEAN_UP - Cleanup of internal volume is in
            progress.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_VOL_IS_INTERNAL - Internal volumes cannot be admitted
            into a remote-copy group.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_VOL_NOT_IN_SAME_DOMAIN - The remote-copy group has a
            different domain than the volume.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_STARTED - The remote-copy group has already been
            started.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_IS_BUSY - The remote-copy group is currently busy;
            retry later.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_VOL_IN_OTHER_GROUP - The volume is already in
            another remote-copy group.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_INV_TARGET_NUMBER - The wrong number of targets is
            specified for the remote-copy group.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_INV_TARGET - The specified target is not a target of
            the remote-copy group.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_NOT_SUPPORT_VOL_ID - The target for the remote-copy
            group does not support volume IDs.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_IS_SELF_MIRRORED - The target is self-mirrored.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_TARGET_VOL_IS_RO - The remote-copy target volume
            cannot be read-only.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_OPERATION_ONLY_ON_PRIMARY_SIDE - The operation should
            be performed only on the primary side.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_TARGET_IS_NOT_READY - The remote-copy group target is not
            ready.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotImplemented`
            - RCOPY_UNSUPPORTED_TARGET_VERSION - The target HP 3PAR OS version
            is not supported.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_MULTIPLE_VOL_IN_SAME_FAMILY - A remote-copy group
            cannot contain multiple volumes in the same family tree.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_MULTIPLE_RW_SNAPSHOT_IN_SAME_FAMILY - Only one
            read/write snapshot in the same family can be added to a
            remote-copy group.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_SYNC_SNAPSHOT_IN_MULTIPLE_TARGET - A synchronization
            snapshot cannot be set with multiple targets.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_ADD_VOL_FAILED - Failed to add volume to the
            remote-copy group.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_ADD_VOL_FAILED_PARTIAL - Adding volume to
            remote-copy group succeeded on some targets.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_SET_AUTO_CREATED - The set was created
            automatically Members cannot be added or removed.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_SECONDARY_DOES_NOT_MATCH_PRIMARY - The remote-copy
            group is in the failover state. Both systems are in the primary
            state.
        """
        return self.client.addVolumeToRemoteCopyGroup(name, volumeName,
                                                      targets, optional)

    def removeVolumeFromRemoteCopyGroup(self, name, volumeName,
                                        optional=None,
                                        removeFromTarget=False):
        """
        Removes a volume from a remote copy group

        :param name: Name of the remote copy group
        :type name: string
        :param volumeName: Specifies the name of the existing virtual
                           volume to be admitted to an existing remote-copy
                           group.
        :type volumeName: string
        :param optional: dict of other optional items
        :type optional: dict

        .. code-block:: python

            optional = {
                "keepSnap": False  # If true, the resynchronization
                                   # snapshot of the local volume is
                                   # retained.
            }

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_RCOPY_GROUP - The remote-copy group does not exist.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_VOL - volume doesn't exist
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_IS_NOT_READY - The remote-copy configuration is not ready
            for commands.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_STARTED - The remote-copy group has already been
            started.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_IS_BUSY - The remote-copy group is currently busy;
            retry later.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - RCOPY_GROUP_VOL_NOT_IN_GROUP - The volume is not in the
            remote-copy group.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_RENAME_RESYNC_SNAPSHOT_FAILED - Renaming of the
            remote-copy group resynchronization snapshot failed.
        :raises: :class:`~hpe3parclient.exceptions.HTTPConflict`
            - RCOPY_GROUP_CREATED_MIRROR_CONFIG_OFF - The remote-copy group was
            created when the configuration mirroring policy was turned off on
            the target. However, this policy is now turned on. In order to
            dismiss a volume from the remote-copy group, the configuration
            mirroring policy must be turned off. Retry after turning the
            policy off.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_OPERATION_ONLY_ON_PRIMARY_SIDE - The operation should
            be performed only on the primary side.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_TARGET_IS_NOT_READY - The remote-copy group target is
            not ready.
        """
        return self.client.removeVolumeFromRemoteCopyGroup(name, volumeName,
                                                           optional,
                                                           removeFromTarget)

    def startRemoteCopy(self, name, optional=None):
        """
        Starts a remote copy

        :param name: Name of the remote copy group
        :type name: string
        :param optional: dict of other optional items
        :type optional: dict

        .. code-block:: python

            # All the volumes in the group must be specified. While specifying
            # the pair, the starting snapshot is optional. If it is not
            # specified, a full resynchronization of the volume is performed.
            startingSnapshots = [
                {
                    "volumeName": "vol_name",    # Volume name
                    "snapshotName": "snap_name"  # Snapshot name
                }
            ]

            optional = {
                "skipInitialSync": False,    # If True, the volume
                                             # should skip the initial
                                             # synchronization and
                                             # sets the volumes to
                                             # a synchronized state.
                "targetName": "target_name", # The target name associated
                                             # with this group.
                "startingSnapshots": startingSnapshots
            }

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_RCOPY_GROUP - The remote-copy group does not exist.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_INV_TARGET - The specified target is not a target of
            the remote-copy group.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_STARTED - The remote-copy group has already been
            started.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - RCOPY_GROUP_EMPTY - The remote-copy group must contain volumes
            before being started.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_OPERATION_ONLY_ON_PRIMARY_SIDE - The operation
            should be performed only on the primary side.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - RCOPY_TARGET_NOT_SPECIFIED - A target must be specified to
            complete this operation.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - RCOPY_GROUP_NOT_ALL_VOLUMES_SPECIFIED - All the volumes in the
            remote-copy group must be specified to complete this operation.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - RCOPY_GROUP_EXISTENT_VOL_WWN_ON_TARGET - Secondary volume WWN
            already exists on the target.
        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - RCOPY_GROUP_VOLUME_ALREADY_SYNCED - Volume is already
            synchronized.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - RCOPY_GROUP_INCORRECT_SNAPSHOT_OR_VOLUME_SPECIFIED - An incorrect
            starting snapshot or volume was specified, or the snapshot or
            volume does not exist.
        """
        return self.client.startRemoteCopy(name, optional)

    def stopRemoteCopy(self, name, optional=None):
        """
        Stops a remote copy

        :param name: Name of the remote copy group
        :type name: string
        :param optional: dict of other optional items
        :type optional: dict

        .. code-block:: python

            optional = {
                "noSnapshot": False,        # If true, this option turns
                                            # off creation of snapshots
                                            # in synchronous and
                                            # periodic modes, and
                                            # deletes the current
                                            # synchronization snapshots.
                "targetName": "target_name" # The target name associated
                                            # with this group
            }

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_RCOPY_GROUP - The remote-copy group does not exist.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_TARGET_IS_NOT_READY - The remote-copy group target is not
            ready.
        """
        return self.client.stopRemoteCopy(name, optional)

    def synchronizeRemoteCopyGroup(self, name, optional=None):
        """
        Synchronizing a remote copy group

        :param name: Name of the remote copy group
        :type name: string
        :param optional: dict of other optional items
        :type optional: dict

        .. code-block:: python

            optional = {
                "noResyncSnapshot": False,   # If true, does not save
                                             # the resynchronization
                                             # snapshot. Applicable
                                             # only to remote-copy
                                             # groups in asychronous
                                             # periodic mode.
                "targetName": "target_name", # The target name
                                             # assoicated with the
                                             # remote-copy group.
                "fullSync": False            # If true, this option
                                             # forces a full
                                             # synchronization of the
                                             # remote-copy group, even
                                             # if the volumes are
                                             # already synchronized.
                                             # This option, which
                                             # applies only to volume
                                             # groups in synchronous
                                             # mode, can be used to
                                             # resynchronize volumes
                                             # that have become
                                             # inconsistent.
            }

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_RCOPY_GROUP - The remote-copy group does not exist.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_OPERATION_ONLY_ON_PRIMARY_SIDE - The operation
            should be performed only on the primary side.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - UNLICENSED_FEATURE - The system is not licensed for this feature.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_INV_TARGET - The specified target is not a target of
            the remote-copy group.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_TARGET_IS_NOT_READY - The remote-copy group target is not
            ready.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_INVOLVED_IN_SYNCHRONIZATION - The remote-copy group
            is already involved in synchronization.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_STARTED - The remote-copy group has already been
            started.
        """
        return self.client.synchronizeRemoteCopyGroup(name, optional)

    def recoverRemoteCopyGroupFromDisaster(self, name, action, optional=None):
        """
        Recovers a remote copy group from a disaster

        :param name: Name of the remote copy group
        :type name: string
        :param action: Specifies the action to be taken on the specified group.
                       The action may be any of values 6 through 11:
                       * RC_ACTION_CHANGE_DIRECTION - Changes the current
                       direction of the remote-copy groups.
                       * RC_ACTION_CHANGE_TO_PRIMARY - Changes the secondary
                       groups to primary groups on the active system.
                       * RC_ACTION_MIGRATE_GROUP - Migrates the remote-copy
                       group from the primary system to the secondary system
                       without impacting I/O.
                       * RC_ACTION_CHANGE_TO_SECONDARY - Changes the primary
                       remote-copy group on the backup system to the
                       secondary remote-copy group.
                       * RC_ACTION_CHANGE_TO_NATURUAL_DIRECTION - Changes all
                       remote-copy groups to their natural direction and
                       starts them.
                       * RC_ACTION_OVERRIDE_FAIL_SAFE - Overrides the failsafe
                       state that is applied to the remote-copy group.
        :type action: int
        :param optional: dict of other optional items
        :type optional: dict

        .. code-block:: python

            optional = {
                "targetName": "target_name",  # The target name
                                              # associated with this
                                              # group.
                "skipStart": False,           # If true, groups are not
                                              # started after role reversal
                                              # is completed. Valid for
                                              # only FAILOVER, RECOVER,
                                              # and RESTORE operations.
                "skipSync": False,            # If true, the groups are
                                              # not synchronized after
                                              # role reversal is
                                              # completed. Valid only for
                                              # FAILOVER, RECOVER, and
                                              # RESTORE operations.
                "discardNewData": False,      # If true and the group
                                              # has multiple targets,
                                              # don't check other targets
                                              # of the group to see if
                                              # newer data should be
                                              # pushed from them.
                                              # Valid only for FAILOVER
                                              # operation.
                "skipPromote": False,         # If true, the snapshots of
                                              # the groups that are
                                              # switched from secondary
                                              # to primary are not
                                              # promoted to the base
                                              # volume. Valid only for
                                              # FAILOVER and REVERSE
                                              # operations.
                "noSnapshot": False,          # If true, the snapshots
                                              # are not taken of the
                                              # groups that are switched
                                              # from secondary to
                                              # primary. Valid for
                                              # FAILOVER, REVERSE, and
                                              # RESTORE operations.
                "stopGroups": False,          # If true, the groups are
                                              # stopped before performing
                                              # the reverse operation.
                                              # Valid only for REVERSE
                                              # operation.
                "localGroupsDirection": False # If true, the group's
                                              # direction is changed only
                                              # on the system where the
                                              # operation is run. Valid
                                              # only for REVERSE operation
            }

        :raises: :class:`~hpe3parclient.exceptions.HTTPNotFound`
            - NON_EXISTENT_RCOPY_GROUP - The remote-copy group does not exist.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - UNLICENSED_FEATURE - System is not licensed for this feature.
        :raises: :class:`~hpe3parclient.exceptions.HTTPBadRequest`
            - RCOPY_GROUP_INV_TARGET - Specified target is not in remote copy
            group.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_INPUT_MISSING_REQUIRED - Group has multiple targets.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_RCOPY_GROUP_ROLE_CONFLICT - Group is not in correct
            role for this operation.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_INV_OPERATION_ON_MULTIPLE_TARGETS - The operation is
            not supported on multiple targets.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_NOT_STOPPED - Remote copy group is not stopped.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_RCOPY_GROUP_ROLE_CONFLICT - Group is not in correct
            role for this operation.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_NOT_STARTED - Remote copy not started.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_INPUT_PARAM_CONFLICT - Parameters cannot be present at the
            same time.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - INV_OPERATION_VV_PROMOTE_IN_PROGRESS - Volume promotion is
            in progress.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_IS_BUSY - Remote copy group is currently busy.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_STARTED - Remote copy group has already been started.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_EMPTY - Remote copy group does not contain any
            volumes.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_OPERATION_ONLY_ON_PRIMARY_SIDE - Operation should
            only be issued on primary side.
        :raises: :class:`~hpe3parclient.exceptions.HTTPForbidden`
            - RCOPY_GROUP_OPERATION_ONLY_ON_SECONDARY_SIDE - Operation should
            only be issued on secondary side.
        """
        return self.client.recoverRemoteCopyGroupFromDisaster(name, action,
                                                              optional)

    def toggleRemoteCopyConfigMirror(self, target, mirror_config=True):
        """
        Used to toggle config mirroring policies on a target device.

        :param target: The 3PAR target name to enable/disable config mirroring.
        :type target: string
        :param mirror_config: Specifies whether to enable or disable config
                              mirroring.
        :type mirror_config: bool
        """
        self.client.toggleRemoteCopyConfigMirror(target, mirror_config)

    def getVolumeSnapshots(self, name):
        """
        Shows all snapshots associated with a given volume.

        :param name: The volume name
        :type name: str

        :returns: List of snapshot names
        """
        return self.client.getVolumeSnapshots(name)

    def _mergeDict(self, dict1, dict2):
        """
        Safely merge 2 dictionaries together

        :param dict1: The first dictionary
        :type dict1: dict
        :param dict2: The second dictionary
        :type dict2: dict

        :returns: dict

        :raises Exception: dict1, dict2 is not a dictionary
        """
        return self.client._mergeDict(dict1, dict2)

    def _get_next_word(self, s, search_string):
        """Return the next word.

        Search 's' for 'search_string', if found return the word preceding
        'search_string' from 's'.
        """
        return self.client._get_next_word(s, search_string)

    def getCPGStatData(self, name, interval='daily', history='7d'):
        """
        Requests CPG performance data at a sampling rate (interval) for a
        given length of time to sample (history)

        :param name: a valid CPG name
        :type name: str
        :param interval: hourly, or daily
        :type interval: str
        :param history: xm for x minutes, xh for x hours, or xd for x days
                        (e.g. 30m, 1.5h, 7d)
        :type history: str

        :returns: dict

        :raises: :class:`~hpe3parclient.exceptions.SrstatldException`
            - srstatld gives invalid output
        """
        return self.client.getCPGStatData(name, interval, history)

    def _format_srstatld_output(self, out):
        """
        Formats the output of the 3PAR CLI command srstatld
        Takes the total read/write value when possible

        :param out: the output of srstatld
        :type out: list

        :returns: dict
        """
        return self.client._format_srstatld_output(out)

    def tuneVolume(self, volName, tune_operation, optional=None):
        info = { 'action': self.TUNE_VOLUME, 'tuneOperation': tune_operation }

        if optional is not None and self.CURRENT_WSAPI_VERSION < self.WSAPI_MIN_VERSION_COMPRESSION_SUPPORT:
            if 'compression' in optional.keys():
                del optional['compression']
        if optional:
            info = self.client._mergeDict(info, optional)
        response, body = self.client.http.put(
            '/volumes/%s' % volName, body=info)
        return self.getTask(body['taskid'])

    def cpgExists(self, name):
        try:
            self.getCPG(name)
        except exceptions.HTTPNotFound:
            return False
        return True

    def volumeExists(self, name):
        try:
            self.getVolume(name)
        except exceptions.HTTPNotFound:
            return False
        return True

    def hostExists(self, name):
        try:
            self.getHost(name)
        except exceptions.HTTPNotFound:
            return False
        return True

    def hostSetExists(self, name):
        try:
            self.getHostSet(name)
        except exceptions.HTTPNotFound:
            return False
        return True

    def volumeSetExists(self, name):
        try:
            self.getVolumeSet(name)
        except exceptions.HTTPNotFound:
            return False
        return True

    def vlunExists(self, volume_name, lunid, hostname, port):
        try:
            vlun_id = ''
            if volume_name is not None:
                vlun_id = volume_name
            if lunid is not None:
                vlun_id = "%s,%s" % (vlun_id, lunid)
            if hostname is not None:
                vlun_id = '%s,%s' % (vlun_id, hostname)
            if port is not None:
                if hostname is None:
                    vlun_id = '%s,' % vlun_id

                vlun_id = '%s,%s:%s:%s' % (vlun_id, str(port['node']), str(
                    port['slot']), str(port['cardPort']))
            if ((volume_name is None or len(volume_name) == 0) or
                    lunid is None and (hostname is None or port is None)):
                raise Exception("Some or all parameters are missing : \
volume_name, lunid, hostname or port")
            self.client.http.get('/vluns/%s' % vlun_id)
        except exceptions.HTTPNotFound:
            return False
        return True

    def qosRuleExists(self, targetName, targetType):
        try:
            self.queryQoSRule(targetName, targetType)
        except exceptions.HTTPNotFound:
            return False
        return True

    def flashCacheExists(self):
        try:
            self.getFlashCache()
        except exceptions.HTTPNotFound:
            return False
        return True

    def onlinePhysicalCopyExists(self, src_name, phy_copy_name):
        try:
            if self.volumeExists(src_name) and self.volumeExists(phy_copy_name) and self._findTask(phy_copy_name,True) != None:
                return True
        except exceptions.HTTPNotFound:
            return False
        return False
        
    def offlinePhysicalCopyExists(self, src_name, phy_copy_name):
        try:
            if self.volumeExists(src_name) and self.volumeExists(phy_copy_name) and self._findTask(src_name + "-*" + phy_copy_name, True) != None:
                return True
        except exceptions.HTTPNotFound:
            return False
        return False
      
    #Takes a list of host setmembers and adds them to a hostset
    def addHostsToHostSet(self, name, setmembers):
        self.client.modifyHostSet(
            name, action=client.HPE3ParClient.SET_MEM_ADD,
            setmembers=setmembers)

    # Takes a list of host setmembers and removes them from a hostset
    def removeHostsFromHostSet(self, name, setmembers):
        self.client.modifyHostSet(
            name, action=client.HPE3ParClient.SET_MEM_REMOVE,
            setmembers=setmembers)

    # Takes a list of volume setmembers and adds them to a volumeset
    def addVolumesToVolumeSet(self, name, setmembers):
        self.client.modifyVolumeSet(
            name, action=client.HPE3ParClient.SET_MEM_ADD,
            setmembers=setmembers)

    # Takes a list of volume setmembers and removes them from a volumeset
    def removeVolumesFromVolumeSet(self, name, setmembers):
        self.client.modifyVolumeSet(
            name, action=client.HPE3ParClient.SET_MEM_REMOVE,
            setmembers=setmembers)
