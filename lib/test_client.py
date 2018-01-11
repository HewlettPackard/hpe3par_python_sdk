from client import HPE3ParClient
from pprint import pprint

client_obj=HPE3ParClient("https://15.213.67.205:8080/api/v1")
client_obj.setSSHOptions('15.213.67.205', 'vro_user', 'vro_user')
client_obj.login("vro_user", "vro_user")
pprint(vars(client_obj.queryQoSRules()[3]))
#pprint(vars(client_obj.queryQoSRule('test_pattern1')))
#pprint(vars(client_obj.findAllVolumeSets('SS_Rec_VV_3DCPP.6')[0]))
#pprint(client_obj.findVolumeSet('SS_Rec_VV_3DCPP.6'))
#pprint(vars(client_obj.getVolumeSets()[4]))
#pprint(vars(client_obj.getVolumeSet('vv_rcgnew')))
#pprint(vars(client_obj.getPorts()[9]))
#pprint(vars(client_obj._getProtocolPorts(1)[0]))
#pprint(vars(client_obj.getFCPorts()[0]))
#pprint(vars(client_obj.getIPPorts()[0]))
#pprint(vars(client_obj.getiSCSIPorts()[0]))
#pprint(vars(client_obj.getHostSets()[3]))
#pprint(vars(client_obj.getHostSet('hostset5')))
#pprint(vars(client_obj.getHosts()[0].fcpaths[0]))
#pprint(vars(client_obj.getHosts()[7].iscsi_paths[0]))
#pprint(vars(client_obj.queryHost(['iqn.1991-05.com.microsoft:dmmtw2k8x64n009'], ['50014380242C1506'])[1]))
#pprint(vars(client_obj.getVLUNs()[0]))
#pprint(vars(client_obj.getHostVLUNs('ESX_234')[3]))
# pprint(vars(client_obj.getCPGs()[0]))
# pprint(vars(client_obj.getCPG('FC_r1')))
# pprint(vars(client_obj.getCPGAvailableSpace('cpg_convert').capacitefficiency))
#pprint(client_obj.getVolume('rmc-0024751-ro-170817180340183').name)
#pprint(client_obj.getHostSets()[0].setmembers)
#pprint(client_obj._findTask('name'))
client_obj.logout()
