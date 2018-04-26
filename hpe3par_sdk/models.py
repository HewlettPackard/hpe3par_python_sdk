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

class VirtualVolume(object):

    def __init__(self, object_hash):
        if object_hash is None:
            return
    
        self.additional_states = object_hash.get('additionalStates')

        if object_hash.get('adminSpace'):
            self.admin_space = Space(object_hash['adminSpace'])
        else:
            self.admin_space = None
        
        self.base_id = object_hash.get('baseId')
        
        self.comment = object_hash.get('comment')

        if object_hash.get('capacityEfficiency'):
            self.capacity_efficiency = CapEfficiency(object_hash['capacityEfficiency'])
        else:    
            self.capacity_efficiency = None
        
        self.copy_of = object_hash.get('copyOf')
        
        self.copy_type = object_hash.get('copyType')
        
        self.creation_time8601 = object_hash.get('creationTime8601')
        
        self.creation_time_sec = object_hash.get('creationTimeSec')
        
        self.degraded_states = object_hash.get('degradedStates')
        
        self.domain = object_hash.get('domain')
        
        self.expiration_time8601 = object_hash.get('expirationTime8601')
        
        self.expiration_time_sec = object_hash.get('expirationTimeSec')
        
        self.failed_states = object_hash.get('failedStates')
        
        self.compression_state = object_hash.get('compressionState')
        
        self.deduplication_state = object_hash.get('deduplicationState')
        
        self.id = object_hash.get('id')
        
        self.links = object_hash.get('links')
        
        self.name = object_hash.get('name')
        
        self.parent_id = object_hash.get('parentId')
        
        self.phys_parent_id = object_hash.get('physParentId')
        
        if object_hash.get('policies'):
            self.policies = Policy(object_hash.get('policies'))
        else:
            self.policies = None
        
        self.provisioning_type = object_hash.get('provisioningType')
        
        self.read_only = object_hash.get('readOnly')
        
        self.retention_time8601 = object_hash.get('retentionTime8601')
        
        self.retention_time_sec = object_hash.get('retentionTimeSec')
        
        self.ro_child_id = object_hash.get('roChildId')
        
        self.rw_child_id = object_hash.get('rwChildId')
        
        self.host_write_mib = object_hash.get('hostWriteMiB')
        
        self.total_used_mib = object_hash.get('totalUsedMiB')
        
        self.total_reserved_mib = object_hash.get('totalReservedMiB')
        
        self.size_mib = object_hash.get('sizeMiB')
        
        self.snap_cpg = object_hash.get('snapCPG')
        
        if object_hash.get('snapshotSpace'):
            self.snapshot_space = Space(object_hash.get('snapshotSpace'))
        else:
            self.snapshot_space = None
        
        self.ss_spc_alloc_limit_pct = object_hash.get('ssSpcAllocLimitPct')
        
        self.ss_spc_alloc_warning_pct = object_hash.get('ssSpcAllocWarningPct')
        
        self.state = object_hash.get('state')
        
        self.user_cpg = object_hash.get('userCPG')
        
        if object_hash.get('userSpace'):
            self.user_space = Space(object_hash.get('userSpace'))
        else:
            self.user_space = None
        
        self.usr_spc_alloc_limit_pct = object_hash.get('usrSpcAllocLimitPct')
        
        self.usr_spc_alloc_warning_pct = object_hash.get('usrSpcAllocWarningPct')
        
        self.uuid = object_hash.get('uuid')
        
        self.shared_parent_id = object_hash.get('sharedParentID')
        
        self.udid = object_hash.get('udid')
        
        self.wwn = object_hash.get('wwn')

class Space(object):

    def __init__(self, object_hash):
        if object_hash is None:
            return

        self.reserved_MiB = object_hash.get('reservedMiB')
        
        self.raw_reserved_MiB = object_hash.get('rawReservedMiB')
        
        self.used_MiB = object_hash.get('usedMiB')
        
        self.free_MiB = object_hash.get('freeMiB')

class CapEfficiency(object):

    def __init__(self, object_hash):
        if object_hash is None:
            return
        
        self.compaction = object_hash.get('compaction')
        
        self.compression = object_hash.get('compression')
        
        self.data_reduction = object_hash.get('dataReduction')
        
        self.over_provisioning = object_hash.get('overProvisioning')
        
        self.deduplication = object_hash.get('deduplication')

class Policy(object):

    def __init__(self, object_hash):
        if object_hash is None:
            return
        
        self.stale_ss = object_hash.get('staleSS')
        
        self.one_host = object_hash.get('oneHost')
        
        self.zero_detect = object_hash.get('zeroDetect')
        
        self.system = object_hash.get('system')
        
        self.caching = object_hash.get('caching')
        
        self.fsvc = object_hash.get('fsvc')
        
        self.host_dif = object_hash.get('hostDIF')

class VolumeSet(object):

    def __init__(self, object_hash):
        if object_hash is None:
            return
        
        self.name = object_hash.get('name')
        
        self.uuid = object_hash.get('uuid')
        
        self.id = object_hash.get('id')
        
        self.comment = object_hash.get('comment')
        
        self.domain = object_hash.get('domain')
        
        self.setmembers = object_hash.get('setmembers')
        
        self.flash_cache_policy = object_hash.get('flashCachePolicy')
        
        self.qos_enabled = object_hash.get('qosEnabled')

class FCPath(object):

    def __init__(self, object_hash):
        if object_hash is None:
            return

        # [type - String]
        # A WWN assigned to the host.
        self.wwn = object_hash.get('wwn')

        # [type - PortPos]
        # The portpos details.
        if object_hash.get('portPos'):
            self.port_pos = PortPos(object_hash.get('portPos'))
        else:
            self.port_pos = None

        # [type - String]
        # HBA firmware version.
        self.firmware_version = object_hash.get('firmwareVersion')

        # [type - String]
        # HBA vendor.
        self.vendor = object_hash.get('vendor')

        # [type - String]
        # HBA model.
        self.model = object_hash.get('model')

        # [type - String]
        # HBA driver version.
        self.driver_version = object_hash.get('driverVersion')

        # [type - String]
        # HBA host speed.
        self.host_speed = object_hash.get('hostSpeed')

class SCSIPath(object):

    def __init__(self, object_hash):
        if object_hash is None:
            return

        # [type - String]
        # An iSCSI name to be assigned to the host.
        self.name = object_hash.get('name')

        # [type - PortPos]
        # The portpos details.
        if object_hash.get('portPos'):
            self.port_pos = PortPos(object_hash['portPos'])
        else:
            self.port_pos = None

        # [type - String]
        # IP address for Remote Copy.
        self.ipaddr = object_hash.get('IPAddr')

        # [type - String]
        # HBA firmware version.
        self.firmware_version = object_hash.get('firmwareVersion')

        # [type - String]
        # HBA vendor.
        self.vendor = object_hash.get('vendor')

        # [type - String]
        # HBA model.
        self.model = object_hash.get('model')

        # [type - String]
        # HBA driver version.
        self.driver_version = object_hash.get('driverVersion')

        # [type - String]
        # HBA host speed.
        self.host_speed = object_hash.get('hostSpeed')

class Agent(object):

    def __init__(self, object_hash):
        if object_hash is None:
            return

        # [type - String]
        # The host name reported by the agent.
        self.reported_name = object_hash.get('reportedName')

        # [type - String]
        # The host agent IP address.
        self.ipaddr = object_hash.get('IPAddr')

        # [type - String]
        # The architecture description of the host agent.
        self.architecture = object_hash.get('architecture')

        # [type - String]
        # Operating system of the host agent.
        self.os = object_hash.get('os')

        # [type - String]
        # The operating system version of the host agent.
        self.os_version = object_hash.get('osVersion')

        # [type - String]
        # The operating system patch level of host agent.
        self.os_patch = object_hash.get('osPatch')

        # [type - String]
        # The multipathing software in use by the host agent.
        self.multi_path_software = object_hash.get('multiPathSoftware')

        # [type - String]
        # The multipathing software version.
        self.multi_path_software_version = object_hash.get('multiPathSoftwareVersion')

        # [type - String]
        # Name of the host cluster of which the host is a member.
        self.cluster_name = object_hash.get('clusterName')

        # [type - String]
        # Host clustering software in use on host.
        self.cluster_software = object_hash.get('clusterSoftware')

        # [type - String]
        # Version of the host clustering software in use.
        self.cluster_version = object_hash.get('clusterVersion')

        # [type - String]
        # Identifier for the cluster.
        self.cluster_id = object_hash.get('clusterId')

        # [type - String]
        # Identifier for the host agent.
        self.hosted = object_hash.get('hosted')


class Descriptors():

    def __init__(self, object_hash):
        if object_hash is None:
            return
        # [type - String]
        self.location = object_hash.get('location')

        # [type - String]
        self.ipaddr = object_hash.get('IPAddr')

        # [type - String]
        # The operating system running on the host.
        self.os = object_hash.get('os')

        # [type - String]
        self.model = object_hash.get('model')

        # [type - String]
        self.contact = object_hash.get('contact')

        # [type - String]
        # Any additional information for the host.
        self.comment = object_hash.get('comment')


class Host(object):

    def __init__(self, object_hash):
        if object_hash is None:
            return

        # [type - Number]
        # Specifies the ID of the host.
        self.id = object_hash.get('id')

        # [type - String]
        # Specifies the name of the host.
        self.name = object_hash.get('name')

        # [type - HPE3PARClient::HostPersona]
        # ID of the persona to assigned to the host.
        self.persona = object_hash.get('persona')

        # [type - Array of FCPath]
        # A host object query response can include an array of one or more FCPaths objects
        self.fcpaths = []

        if object_hash.get('FCPaths') is not None:
            for fc_path in object_hash['FCPaths']:
                self.fcpaths.append(FCPath(fc_path))

        # [type - Array of SCSIPath]
        # A host object query response can include an array of one or more iSCSIPaths objects.
        self.iscsi_paths = []

        if object_hash.get('iSCSIPaths') is not None:
            for iscsi_path in object_hash['iSCSIPaths']:
                self.iscsi_paths.append(SCSIPath(iscsi_path))

        # [type - String]
        # The domain or associated with this host.
        self.domain = object_hash.get('domain')

        # [type - Descriptors]
        # An optional sub-object of the host object for creation and modification
        if object_hash.get('descriptors'):
            self.descriptors = Descriptors(object_hash['descriptors'])
        else:
            self.descriptors = None

        # [type - Agent]
        # Agent object
        if object_hash.get('agent') is not None:
            self.agent = Agent(object_hash['agent'])
        else:
            self.agent = None
        # [type - String]
        # Initiator Chap Name
        self.initiator_chap_name = object_hash.get('initiatorChapName')

        # [type - Boolean]
        # Flag to determine whether or not the chap initiator is enabled.
        self.initiator_chap_enabled = object_hash.get('initiatorChapEnabled')

        # [type - String]
        # Target chap name.
        self.target_chap_name = object_hash.get('targetChapName')

        # [type - Boolean]
        # Flag to determine whether or not the chap target is enabled.
        self.target_chap_enabled = object_hash.get('targetChapEnabled')

        # [type - String]
        # Encrypted CHAP secret of initiator.
        self.initiator_encrypted_chap_secret = object_hash.get('initiatorEncryptedChapSecret')

        # [type - String]
        # Encrypted CHAP secret of target.
        self.target_encrypted_chap_secret = object_hash.get('targetEncryptedChapSecret')



class QoSRule():
    def __init__(self, object_hash):
        if object_hash is None:
            return
        # [type - Number]
        # ID of the QoS target.
        self.id = object_hash.get('id')

        # [type - HPE3PARClient::QoStargetType]
        # Type of QoS target.
        self.type = object_hash.get('type')

        # [type - String]
        # Name of the target
        self.name = object_hash.get('name')

        # [type - String]
        # Name of the domain.
        self.domain = object_hash.get('domain')

        # [type - Boolean]
        # QoS state of the target.
        self.enabled = object_hash.get('enabled')

        # [type - HPE3PARClient::QoSpriorityEnumeration]
        # QoS priority.
        self.priority = object_hash.get('priority')

        # [type - Number]
        # Bandwidth minimum goal in kilobytes per second.
        self.bw_min_goal_kb = object_hash.get('bwMinGoalKB')

        # [type - Number]
        # Bandwidth maximum limit in kilobytes per second.
        self.bw_max_limit_kb = object_hash.get('bwMaxLimitKB')

        # [type - Number]
        # I/O-per-second minimum goal.
        self.io_min_goal = object_hash.get('ioMinGoal')

        # [type - Number]
        # I/O-per-second maximum limit.
        self.io_max_limit = object_hash.get('ioMaxLimit')

        # [type - Number]
        # Latency goal in milliseconds.
        self.latency_goal = object_hash.get('latencyGoal')

        # [type - Number]
        # Latency goal in microseconds.
        self.latency_goal_usecs = object_hash.get('latencyGoaluSecs')


class PortPos(object):

    def __init__(self, object_hash):
        if object_hash is None:
            return
        # [type - Number]
        # System node.
        self.node = object_hash.get('node')
        # [type - Number]
        # PCI bus slot in the node.
        self.slot = object_hash.get('slot')
        # [type - Number]
        # Port number on the FC card.
        self.card_port = object_hash.get('cardPort')

class VLUN(object):
    def __init__(self, object_hash):
        if object_hash is None:
            return
        # [type - Number]
        # Exported LUN value.
        self.lun = object_hash.get('lun')

        # [type - String]
        # Name of exported virtual volume name or VV-set name.
        self.volume_name = object_hash.get('volumeName')

        # [type - String]
        # Host name or host set name to which the VLUN is exported.
        self.hostname = object_hash.get('hostname')

        # [type - String]
        # Host WWN, or iSCSI name, or SAS address; depends on port type.
        self.remote_name = object_hash.get('remoteName')

        # [type - PortPos]
        # System port of VLUN exported to. It includes node number, slot number, and cardPort number.
        if object_hash.get('portPos'):
            self.port_pos = PortPos(object_hash.get('portPos'))
        else:
            self.port_pos = None

        # [type - HPE3PARClient::VlunType]
        # VLUN type.
        self.type = object_hash.get('type')

        # [type - String]
        # WWN of exported volume. If a VV set is exported, this value is null.
        self.volume_wwn = object_hash.get('volumeWWN')

        # [type - HPE3PARClient::VlunMultipathing]
        # Multipathing method in use.
        self.multipathing = object_hash.get('multipathing')

        # [type - HPE3PARClient::VLUNfailedPathPol]
        # Failed path monitoring method.
        self.failed_path_pol = object_hash.get('failedPathPol')

        # [type - Number]
        # Monitoring interval in seconds after which the host checks for failed paths.
        self.failed_path_interval = object_hash.get('failedPathInterval')

        # [type - String]
        # The device name for this VLUN on the host.
        self.host_device_name = object_hash.get('hostDeviceName')

        # [type - Boolean]
        # Specified if the VLUN is an active VLUN or a VLUN template.
        self.active = object_hash.get('active')

class Usage(object):

    def __init__(self, object_hash):
        if object_hash is None:
            return

        # [type - Number]
        # Total logical disk space in MiB.
        self.total_MiB = object_hash.get('totalMiB')

        # [type - Number]
        # Total physical (raw) logical disk space in MiB.
        self.raw_total_MiB = object_hash.get('rawTotalMiB')

        # [type - Number]
        # Amount of logical disk used, in MiB.
        self.used_MiB = object_hash.get('usedMiB')

        # [type - Number]
        # Amount of physical (raw) logical disk used, in MiB.
        self.raw_used_MiB = object_hash.get('rawUsedMiB')


class GrowthParams(object):

    def __init__(self, object_hash):
        if object_hash is not None:
            return

        # [type - Number]
        # Threshold of used logical disk space, when exceeded, results in a warning alert.
        self.warning_MiB = object_hash.get('warningMiB')

        # [type - Number]
        # The auto-grow operation is limited to the specified storage amount that sets the growth limit.
        self.limit_MiB = object_hash.get('limitMiB')

        # [type - Number]
        # The growth increment, the amount of logical disk storage created on each auto-grow operation.
        self.increment_MiB = object_hash.get('incrementMiB')

        # [type - LDLayout]
        # Logical disk types for this CPG.
        self.ld_layout = LDLayout(object_hash.get('LDLayout'))


class PrivateSpace(object):

    def __init__(self, object_hash):
        if object_hash is not None:
            return

        # [type - Number]
        # Base space in MiB.
        self.base = object_hash.get('base')

        # [type - Number]
        # Raw base space in MiB.
        self.raw_base = object_hash.get('rawBase')

        # [type - Number]
        # snapshot space in MiB.
        self.snapshot = object_hash.get('snapshot')

        # [type - Number]
        # Raw snapshot space in MiB.
        self.raw_snapshot = object_hash.get('rawSnapshot')

class CPG(object):

    def __init__(self, object_hash):
        if not object_hash:
            return

        # [type - Number]
        # Cpg ID.
        self.id = object_hash.get('id')

        # [type - String]
        # The UUID that was automatically assigned to the Cpg at creation.
        self.uuid = object_hash.get('uuid')

        # [type - String]
        # Cpg name.
        self.name = object_hash.get('name')

        # [type - String]
        # Domain to which the Cpg belongs.
        self.domain = object_hash.get('domain')

        # [type - Number]
        # Percentage usage at which to issue an alert.
        self.warning_pct = object_hash.get('warningPct')

        # [type - Number]
        # Number of TPVVs allocated in the Cpg.
        self.num_tpvvs = object_hash.get('numTPVVs')

        # [type - Number]
        # Number of FPVVs allocated in the Cpg.
        self.num_fpvvs = object_hash.get('numFPVVs')

        # [type - Number]
        # Number of TDVVs created in the Cpg.
        self.num_tdvvs = object_hash.get('numTDVVs')

        # [type - Usage]
        # User data space usage.
        if object_hash.get('UsrUsage') is not None:
            self.usr_usage = Usage(object_hash.get('UsrUsage'))
        else:
            self.usr_usage = None

        # [type - Usage]
        # Snap-shot administration usage.
        if object_hash.get('SAUsage') is not None:
            self.sausage = Usage(object_hash.get('SAUsage'))
        else:
            self.sausage = None

        # [type - Usage]
        # Snap-shot data space usage.
        if object_hash.get('SDUsage') is not None:
            self.sdusage = Usage(object_hash.get('SDUsage'))
        else:
            self.sdusage = None

        # [type - GrowthParams]
        # Snap-shot administration space autogrowth parameters.
        if object_hash.get('SAGrowth') is not None:
            self.sagrowth = GrowthParams(object_hash.get('SAGrowth'))
        else:
            self.sagrowth = None

        # [type - GrowthParams]
        # Snap-shot data space auto-growth parameters.
        if object_hash.get('SDGrowth') is not None:
            self.sdgrowth = GrowthParams(object_hash.get('SDGrowth'))
        else:
            self.sdgrowth = None

        # [type - Number]
        # Overall state of the Cpg.- HPE3PARClient::CPGState
        self.state = object_hash.get('state')

        # [type - Number]
        # Detailed state of the Cpg. - HPE3PARClient::CPGState
        self.failed_states = object_hash.get('failedStates')

        # [type - Number]
        # Detailed state of the Cpg. - HPE3PARClient::CPGState
        self.degraded_states = object_hash.get('degradedStates')

        # [type - Number]
        # Detailed state of the Cpg. - HPE3PARClient::CPGState
        self.additional_states = object_hash.get('additionalStates')

        # [type - Boolean]
        # Enables (true) or disables (false) Cpg deduplication capability.
        self.dedup_capable = object_hash.get('dedupCapable')

        # [type - Number]
        # Shared Cpg space in MiB
        self.shared_space_MiB = object_hash.get('sharedSpaceMiB')

        # [type - Number]
        # Free Cpg space in MiB
        self.free_space_MiB = object_hash.get('freeSpaceMiB')

        # [type - Number]
        # Total Cpg space in MiB
        self.total_space_MiB = object_hash.get('totalSpaceMiB')

        # [type - Number]
        # Raw shared space in MiB
        self.raw_shared_space_MiB = object_hash.get('rawSharedSpaceMiB')

        # [type - Number]
        # Raw free space in MiB
        self.raw_free_space_MiB = object_hash.get('rawFreeSpaceMiB')

        # [type - Number]
        # Raw total space in MiB
        self.raw_total_space_MiB = object_hash.get('rawTotalSpaceMiB')

        # [type - Number]
        # Deduplication version used by volumes in the Cpg.
        self.tdvv_version = object_hash.get('tdvvVersion')

        # [type - Number]
        # Maximum size of the deduplication store Volume in the Cpg.
        self.dds_rsvd_MiB = object_hash.get('ddsRsvdMiB')


        # [type - PrivateSpace]
        # Private Cpg space in MiB
        if object_hash.get('privateSpaceMiB') is not None:
            self.private_space_MiB = PrivateSpace(object_hash.get('privateSpaceMiB'))
        else:
            self.private_space_MiB = None

class LDLayout(object):

    def __init__(self, object_hash):
        if not object_hash:
            return

        # [type - Number]
        # Specifies the RAID type for the logical disk. - HPE3PARClient::CPGRAIDType
        self.raidtype = object_hash.get('RAIDType')

        # [type - Number]
        # Specifies the set size in the number of chunklets.
        self.set_size = object_hash.get('setSize')

        # [type - Number]
        # Specifies that the layout must support the failure of one port pair, one cage, or one magazine. - HPE3PARClient::CPGHA
        self.ha = object_hash.get('HA')

        # [type - Number]
        # Specifies the chunklet location preference characteristics. - HPE3PARClient::CPGChunkletPosPref
        self.chunklet_pos_pref = object_hash.get('chunkletPosPref')

        # [type - Array of DiskPattern objects]
        # Specifies patterns for candidate disks.
        self.disk_patterns = []
        if object_hash.get('diskPatterns') is not None:
            for disk_pattern in object_hash['diskPatterns']:
                self.disk_patterns.apppend(DiskPattern(disk_pattern))


class DiskPattern(object):

    def __init__(self, object_hash):
        if not object_hash:
            return

        # [type - String]
        # Specifies one or more nodes. Nodes are identified by one or more integers. Multiple nodes are separated with a single comma (1,2,3). A range of nodes is separated with a hyphen (0 7). The primary path of the disks must be on the specified node number.
        self.node_list = object_hash.get('nodeList')

        # [type - String]
        # Specifies one or more PCI slots. Slots are identified by one or more integers. Multiple slots are separated with a single comma (1,2,3). A range of slots is separated with a hyphen (0 7). The primary path of the disks must be on the specified PCI slot number(s).
        self.slot_list = object_hash.get('slotList')

        # # Specifies one or more ports. Ports are identified by one or more integers. Multiple ports are separated with a single comma (1,2,3). A range of ports is separated with a hyphen (04). The primary path of the disks must be on the specified port number(s).
        # attr_accessor :port_list
        self.port_list = object_hash.get('portList')

        # # [type - String]
        # # Specifies one or more drive cages. Drive cages are identified by one or more integers. Multiple drive cages are separated with a single comma (1,2,3). A range of drive cages is separated with a hyphen (0 3). The specified drive cage(s) must contain disks.
        self.cage_list = object_hash.get('cageList')


        # # [type - String]
        # # Specifies one or more drive magazines. Drive magazines are identified by one or more integers. Multiple drive magazines are separated with a single comma (1,2,3). A range of drive magazines is separated with a hyphen (07). The specified magazine(s) must contain disks.
        self.mag_list = object_hash.get('magList')

        # # [type - String]
        # # Specifies one or more disk positions within a drive magazine. Disk positions are identified by one or more integers. Multiple disk positions are separated with a single comma (1,2,3). A range of disk positions is separated with a hyphen (0 3). The specified portion(s) must contain disks.
        self.disk_pos_list = object_hash.get('diskPosList')

        # # [type - String]
        # # Specifies one or more physical disks. Disks are identified by one or more integers. Multiple disks are separated with a single comma (1,2,3). A range of disks is separated with a hyphen (0 3). Disks must match the specified ID(s).
        # attr_accessor :disk_list
        self.disk_list = object_hash.get('diskList')
        
        # # [type - Number]
        # # Specifies that physical disks with total chunklets less than the number specified be selected.
        self.total_chunklets_greater_than = object_hash.get('totalChunkletsGreaterThan')

        # # [type - Number]
        # # Specifies that physical disks with total chunklets less than the number specified be selected.
        self.total_chunklets_less_than = object_hash.get('totalChunkletsLessThan')

        # # [type - Number]
        # # Specifies that physical disks with free chunklets greater than the number specified be selected.
        self.free_chunklets_greater_than = object_hash.get('freeChunkletsGreaterThan')

        # # [type - Number]
        # # Specifies that physical disks with free chunklets greater than the number specified be selected.
        # attr_accessor :free_chunklets_less_than
        self.free_chunklets_less_than = object_hash.get('freeChunkletsLessThan')

        # # [type - array of string]
        # # Specifies that PDs identified by their models are selected.
        self.disk_models = object_hash.get('diskModels')

        # # [type - Number]
        # # Specifies that physical disks must have the specified device type. - HPE3PARClient::CPGDiskType
        self.disk_type = object_hash.get('diskType')

        # [type - Number]
        # Disks must be of the specified speed.
        self.rpm = object_hash.get('RPM')
        
class Task(object):
    
    def __init__(self, object_hash):
        if object_hash is None:
            return
    
        self.task_id = object_hash.get('id')
    
        self.status = object_hash.get('status')
    
        self.name = object_hash.get('name')
    
        self.type = object_hash.get('type')

class HostSet(object):

    def __init__(self, object_hash):
        if object_hash is None:
            return
        
        self.name = object_hash.get('name')
        
        self.uuid = object_hash.get('uuid')
        
        self.id = object_hash.get('id')
        
        self.comment = object_hash.get('comment')
        
        self.domain = object_hash.get('domain')
        
        self.setmembers = object_hash.get('setmembers')
        
class LDLayoutCapacity(object):

    def __init__(self, object_hash):
        if object_hash is None:
            return

        self.rawfree_in_mib = object_hash.get('rawFreeMiB')
        
        self.usable_free_in_mib = object_hash.get('usableFreeMiB')
        
        self.overprovisioned_virtualsize_in_mib = object_hash.get('overProvisionedVirtualSizeMiB')

        self.overprovisioned_used_in_mib = object_hash.get('overProvisionedUsedMiB')
        
        self.overprovisioned_allocated_in_mib = object_hash.get('overProvisionedAllocatedMiB')
        
        self.overprovisioned_free_in_mib = object_hash.get('overProvisionedFreeMiB')
        
        self.capacitefficiency = CapEfficiency(object_hash.get('capacityEfficiency'))

class ISCSIPortInfo(object):

    def __init__(self, object_hash):
        if not object_hash:
            return
        
        # [type - String]
        # iSCSI port only, not included in the JSON object for other ports.
        self.ip_addr = object_hash.get('ipAddr')
        
        # [type - String]
        # iSCSI port only, not included in the JSON object for other ports.
        self.iscsi_name = object_hash.get('iSCSIName')
        
        # [type - String]
        # Netmask for Ethernet port.
        self.netmask = object_hash.get('netmask')
        
        # [type - String]
        # IP address of the gateway.
        self.gateway = object_hash.get('gateway')
        
        # [type - Number]
        # MTU size in bytes.
        self.mtu = object_hash.get('mtu')
        
        # [type - Boolean]
        # Send Targets Group Tag of the iSCSI target
        self.stgt = object_hash.get('stgt')
        
        # [type - Number]
        # TCP port number for the iSNS server.
        self.isns_port = object_hash.get('iSNSPort')
        
        # [type - String]
        # iSNS server IP address.
        self.isns_addr = object_hash.get('iSNSAddr')
        
        # [type - String]
        # Data transfer rate for the iSCSI port
        self.rate = object_hash.get('rate')
        
        # [type - Number]
        # Target portal group tag.
        self.tpgt = object_hash.get('tpgt')
        
        # [type - Boolean]
        # Indicates whether the port supports VLANs.
        self.vlans = object_hash.get('vlans')

class Port(object):

    def __init__(self, object_hash):
        if not object_hash:
            return

        # [type - PortPos]
        # port n:s:p.
        if object_hash.get('portPos'):
            self.port_pos = PortPos(object_hash.get('portPos'))
        else:
            self.port_pos = None

        # [type - HPE3PARClient::PortMode]
        # port mode.
        self.mode = object_hash.get('mode')

        # [type - HPE3PARClient::PortLinkState]
        # port link state.
        self.linkState = object_hash.get('linkState')

        # [type - String]
        # Node WWN that is unique across all ports.
        self.nodewwn = object_hash.get('nodeWWN')

        # [type - String]
        # port WWN for FCoE and FC ports. Not included in JSON for other ports.
        self.portwwn = object_hash.get('portWWN')

        # [type - HPE3PARClient::PortConnType]
        # port connection type.
        self.type = object_hash.get('type')

        # [type - String]
        # Hardware address for RCIP and iSCSI ports. Not included in JSON for other ports.
        self.hwaddr = object_hash.get('HWAddr')

        # [type - HPE3PARClient::PortProtocol]
        # Indicates the port protocol type.
        self.protocol = object_hash.get('protocol')

        # [type - String]
        # Configurable, human-readable label identifying the HBA port. Maximum length is 15 characters.
        self.label = object_hash.get('label')

        # [type - Arry of string]
        # Array of device name (cage0, host1, etc.) of the device connected to the port.
        self.device = object_hash.get('device')

        # [type - PortPos]
        # Location of failover partner port in <Node><Slot><Port> format.
        if object_hash.get('partnerPos') is not None:
            self.partner_pos = PortPos(object_hash.get('partnerPos'))
        else:
            self.partner_pos = None

        # [type - HPE3PARClient::PortFailOverState]
        # The state of the failover operation, shown for the two ports indicated in the N:S:P and Partner columns.
        self.failover_state = object_hash.get('failoverState')

        # [type - String]
        # For RCIP and iSCSI ports only; not included in the JSON object for other ports.
        self.ip_addr = object_hash.get('IPAddr')

        # [type - String]
        # For iSCSI port only; not included in the JSON object for other ports.
        self.iscsi_name = object_hash.get('iSCSIName')

        # [type - String]
        # Ethernet node MAC address.
        self.enode_macaddr = object_hash.get('enodeMACAddr')

        # [type - String]
        # PFC mask.
        self.pfcmask = object_hash.get('pfcMask')

        # [type - ISCSIPortInfo]
        # Contains information related to iSCSI port properties.
        if object_hash.get('iSCSIPortInfo') is not None:
            self.iscsi_portinfo = ISCSIPortInfo(object_hash.get('iSCSIPortInfo'))
        else:
            self.iscsi_portinfo = None

class FlashCache(object):

    def __init__(self, object_hash):
        if not object_hash:
            return

        # [type - Number 1: Simulator 2: Real]
        # Encrypted CHAP secret of target.
        self.mode = object_hash.get('mode')

        # [type - Number]
        # The total size of the Flash Cache on the entire system. This might differ from the sizeGib input in the create Flash Cache request if the system has more than two nodes.
        self.sizeGiB = object_hash.get('sizeGiB')

        # [type - HPE3PARClient::CPGState]
        # State of flash cache
        self.state = object_hash.get('state')

        # [type - Number]
        # The used size of the Flash Cache.
        self.usedSizeGiB = object_hash.get('usedSizeGiB')
