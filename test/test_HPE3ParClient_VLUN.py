# (c) Copyright 2015 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test class of 3PAR Client handling VLUN."""

from test import HPE3ParClient_base as hpe3parbase
import random
import mock
import unittest
from testconfig import config

from hpe3parclient import client,exceptions



try:
    from urllib.parse import quote
except ImportError:
    from urllib2 import quote

CPG_NAME1 = 'CPG1_VLUN_UNIT_TEST' + hpe3parbase.TIME
CPG_NAME2 = 'CPG2_VLUN_UNIT_TEST' + hpe3parbase.TIME
VOLUME_NAME1 = 'VOLUME1_VLUN_UNIT_TEST' + hpe3parbase.TIME
VOLUME_NAME2 = 'VOLUME2_VLUN_UNIT_TEST' + hpe3parbase.TIME
DOMAIN = 'UNIT_TEST_DOMAIN'
HOST_NAME1 = 'HOST1_VLUN_UNIT_TEST' + hpe3parbase.TIME
HOST_NAME2 = 'HOST2_VLUN_UNIT_TEST' + hpe3parbase.TIME
LUN_0 = 0
LUN_1 = random.randint(1, 10)
LUN_2 = random.randint(1, 10)
PORT={"node": 2,"slot": 2,"cardPort": 4}
# Ensure LUN1 and LUN2 are distinct.
while LUN_2 == LUN_1:
    LUN_2 = random.randint(1, 10)


class HPE3ParClientVLUNTestCase(hpe3parbase.HPE3ParClientBaseTestCase):

    def setUp(self):
        super(HPE3ParClientVLUNTestCase, self).setUp()

        try:
            optional = self.CPG_OPTIONS
            self.cl.createCPG(CPG_NAME1, optional)
        except Exception:
            pass
        try:
            optional = self.CPG_OPTIONS
            self.cl.createCPG(CPG_NAME2, optional)
        except Exception:
            pass

        try:
            self.cl.createVolume(VOLUME_NAME1, CPG_NAME1, 1024)
        except Exception:
            pass

        try:
            self.cl.createVolume(VOLUME_NAME2, CPG_NAME2, 1024)
        except Exception:
            pass
        try:
            optional = {'domain': self.DOMAIN}
            self.cl.createHost(HOST_NAME1, None, None, optional)
        except Exception:
            pass
        try:
            optional = {'domain': self.DOMAIN}
            self.cl.createHost(HOST_NAME2, None, None, optional)
        except Exception:
            pass

    def tearDown(self):

        try:
	    print "coming here"
            self.cl.deleteVLUN(VOLUME_NAME1, LUN_1, HOST_NAME1, self.port)
        except Exception:
            pass
        try:
            self.cl.deleteVLUN(VOLUME_NAME1, LUN_1, HOST_NAME2)
        except Exception:
            pass
        try:
            self.cl.deleteVLUN(VOLUME_NAME2, LUN_2, HOST_NAME2)
        except:
            pass
        try:
            self.cl.deleteVLUN(VOLUME_NAME2, LUN_2, HOST_NAME2, self.port)
        except:
            pass
        try:
            self.cl.deleteVolume(VOLUME_NAME1)
        except Exception:
            pass

        try:
            self.cl.deleteVolume(VOLUME_NAME2)
        except Exception:
            pass

        try:
            self.cl.deleteCPG(CPG_NAME1)
        except Exception:
            pass

        try:
            self.cl.deleteCPG(CPG_NAME2)
        except Exception:
            pass

        try:
            self.cl.deleteHost(HOST_NAME1)
        except Exception:
            pass

        try:
            self.cl.deleteHost(HOST_NAME2)
        except Exception:
            pass

        # very last, tear down base class
        super(HPE3ParClientVLUNTestCase, self).tearDown()

    def test_1_create_VLUN(self):
        self.printHeader('create_VLUN')
        # add one
        noVcn = False
        overrideObjectivePriority = True
        #port={"node": 2,"slot": 2,"cardPort": 4}
        self.cl.createVLUN(VOLUME_NAME1, LUN_1, HOST_NAME1, PORT, noVcn,
                           overrideObjectivePriority)
        # check
        vlun1 = self.cl.getVLUN(VOLUME_NAME1)
        self.assertIsNotNone(vlun1)
        volName = vlun1.volume_name
        self.assertEqual(VOLUME_NAME1, volName)
        # add another
        self.cl.createVLUN(VOLUME_NAME2, LUN_2, HOST_NAME2)
        # check
        vlun2 = self.cl.getVLUN(VOLUME_NAME2)
        self.assertIsNotNone(vlun2)
        volName = vlun2.volume_name
        self.assertEqual(VOLUME_NAME2, volName)
        self.printFooter('create_VLUN')

   # def test_1_create_VLUN_tooLarge(self):
        #self.printHeader('create_VLUN_tooLarge')

       # lun = 100000
	#raise exceptions.HTTPBadRequest("Raised something")
	#print self.cl.createVLUN(VOLUME_NAME1, lun, HOST_NAME1, PORT)
       #   Bad request (HTTP 400) 28 - LUN is greater than 16384.
       # self.assertRaisesRegexp(exceptions.HTTPBadRequest,"Bad request (HTTP 400) 28 - LUN is greater than 16384.",self.cl.createVLUN, VOLUME_NAME1, lun, HOST_NAME1, PORT)
	#with self.assertRaises(exceptions.HTTPBadRequest):
        #    self.cl.createVLUN(VOLUME_NAME1, lun, HOST_NAME1, PORT)

       # self.printFooter('create_VLUN_tooLarge')

    def test_1_create_VLUN_volulmeNonExist(self):
        self.printHeader('create_VLUN_volumeNonExist')

        self.assertRaises(exceptions.HTTPNotFound, self.cl.createVLUN,'Some_Volume', LUN_1, HOST_NAME1, PORT)

        self.printFooter('create_VLUN_volumeNonExist')

    def test_1_create_VLUN_badParams(self):
        self.printHeader('create_VLUN_badParams')

        portPos = {'badNode': 1, 'cardPort': 1, 'slot': 2}
        self.assertRaises(exceptions.HTTPBadRequest, self.cl.createVLUN,
                          VOLUME_NAME1, LUN_1, HOST_NAME1, portPos)

        self.printFooter('create_VLUN_badParams')

    def test_1_create_VLUN_with_id_zero(self):
        self.printHeader('create_VLUN_with_id_zero')
        self.cl.createVLUN(VOLUME_NAME1, LUN_0, HOST_NAME1)
        vlun0 = self.cl.getVLUN(VOLUME_NAME1)
        self.assertIsNotNone(vlun0)
        lun = vlun0.lun
        self.assertEqual(LUN_0, lun)
        volName = vlun0.volume_name
        self.assertEqual(VOLUME_NAME1, volName)

        self.printFooter('create_VLUN_with_id_zero')

    def test_2_get_VLUN_bad(self):
        self.printHeader('get_VLUN_bad')
        self.assertRaises(exceptions.HTTPNotFound, self.cl.getVLUN, 'badName')
        self.printFooter('get_VLUN_bad')
    def check_value_in_listof_objects(self, objects_list, key, value):
	print "key"
	print key
        for object in objects_list:
            if key == 'lun':
                if object.lun == value:
	            return True
            if key == 'volumeName':
                if object.volume_name == value:
		    return True

    def test_2_get_VLUNs(self):
        self.printHeader('get_VLUNs')
        # add 2
        noVcn = False
        overrideLowerPriority = True
        self.cl.createVLUN(VOLUME_NAME1, LUN_1, HOST_NAME1,
                           PORT, noVcn, overrideLowerPriority)
        self.cl.createVLUN(VOLUME_NAME2, LUN_2, HOST_NAME2)
        # get all
        vluns = self.cl.getVLUNs()
        print type(vluns)
        v1 = self.cl.getVLUN(VOLUME_NAME1)
        v2 = self.cl.getVLUN(VOLUME_NAME2)
        self.assertTrue(self.check_value_in_listof_objects(vluns, 'lun', v1.lun))
        self.assertTrue(self.check_value_in_listof_objects(vluns, 'volumeName',v1.volume_name))
        self.assertTrue(self.check_value_in_listof_objects(vluns, 'lun', v2.lun))
        self.assertTrue(self.check_value_in_listof_objects(vluns, 'volumeName', v2.volume_name))
        self.printFooter('get_VLUNs')

    def test_3_delete_VLUN_volumeNonExist(self):
        self.printHeader('delete_VLUN_volumeNonExist')

        self.cl.createVLUN(VOLUME_NAME1, LUN_1, HOST_NAME1, PORT)
        self.cl.getVLUN(VOLUME_NAME1)

        self.assertRaises(exceptions.HTTPNotFound, self.cl.deleteVLUN,
                          'UnitTestVolume', LUN_1, HOST_NAME1, PORT)

        self.printFooter('delete_VLUN_volumeNonExist')

    def test_3_delete_VLUN_hostNonExist(self):
        self.printHeader('delete_VLUN_hostNonExist')

        self.cl.createVLUN(VOLUME_NAME1, LUN_1, HOST_NAME1, PORT)
        self.cl.getVLUN(VOLUME_NAME1)

        self.assertRaises(exceptions.HTTPNotFound, self.cl.deleteVLUN,
                          VOLUME_NAME1, LUN_1, 'BoggusHost', PORT)

        self.printFooter('delete_VLUN_hostNonExist')

    def test_3_delete_VLUN_portNonExist(self):
        self.printHeader('delete_VLUN_portNonExist')

        self.cl.createVLUN(VOLUME_NAME2, LUN_2, HOST_NAME2, PORT)
        self.cl.getVLUN(VOLUME_NAME2)

        port = {'node': 8, 'cardPort': 8, 'slot': 8}
        self.assertRaises(
            exceptions.HTTPBadRequest,
            self.cl.deleteVLUN,
            VOLUME_NAME2,
            LUN_2,
            HOST_NAME2,
            port
        )

        self.printFooter("delete_VLUN_portNonExist")

    def test_3_delete_VLUNs(self):
        self.printHeader('delete_VLUNs')

        self.cl.createVLUN(VOLUME_NAME1, LUN_1, HOST_NAME1, PORT)
        self.cl.getVLUN(VOLUME_NAME1)
        self.cl.deleteVLUN(VOLUME_NAME1, LUN_1, HOST_NAME1, PORT)
        self.assertRaises(
            exceptions.HTTPNotFound,
            self.cl.deleteVLUN,
            VOLUME_NAME1,
            LUN_1,
            HOST_NAME1,
            PORT
        )

        self.printFooter('delete_VLUNs')

    def test_4_get_host_VLUNs(self):
       self.printHeader('get_host_vluns')

       self.cl.createVLUN(VOLUME_NAME2, LUN_2, HOST_NAME2)
       self.cl.createVLUN(VOLUME_NAME1, LUN_1, HOST_NAME2)

       host_vluns = self.cl.getHostVLUNs(HOST_NAME2)

       self.assertIn(VOLUME_NAME1,
                     [vlun.volume_name for vlun in host_vluns])
       self.assertIn(VOLUME_NAME2,
                     [vlun.volume_name for vlun in host_vluns])
       self.assertIn(LUN_1, [vlun.lun for vlun in host_vluns])
       self.assertIn(LUN_2, [vlun.lun for vlun in host_vluns])
       self.printFooter('get_host_vluns')

    def test_4_get_host_VLUNs_unknown_host(self):
       self.printHeader('get_host_vluns_unknown_host')

       self.assertRaises(
           exceptions.HTTPNotFound,
           self.cl.getHostVLUNs,
           'bogusHost')
       self.printFooter('get_host_vluns_unknown_host')

    @unittest.skipIf(config['TEST']['unit'].lower() == 'false', "only works with flask server")
    @mock.patch('hpe3parclient.client.HPE3ParClient.getWsApiVersion')
    def test_5_get_VLUN_no_query_support(self, mock_version):
       self.printHeader('get_VLUN_no_query_support')

      # Mock the version number to a version that does not support
      # VLUN querying and then remake the client.
       version = (client.HPE3ParClient
                  .HPE3PAR_WS_MIN_BUILD_VERSION_VLUN_QUERY - 1)
       mock_version.return_value = {'build': version}
       self.cl = client.HPE3ParClient(self.flask_url)

     # Mock the HTTP GET function to track what the call to it was.
       self.cl.http.get = mock.Mock()
       self.cl.http.get.return_value = (
           {},
           {'members': [{'volumeName': VOLUME_NAME1}]}
       )
 
       self.cl.createVLUN(VOLUME_NAME1, LUN_1, HOST_NAME1)
       self.cl.getVLUN(VOLUME_NAME1)

       # Check for the request that happens when VLUN querying is unsupported.
       self.cl.http.get.assert_has_calls([mock.call('/vluns')])

       self.printFooter('get_VLUN_no_query_support')

    @unittest.skipIf(config['TEST']['unit'].lower() == 'false',
                    "only works with flask server")
    @mock.patch('hpe3parclient.client.HPE3ParClient.getWsApiVersion')
    def test_5_get_host_VLUNs_no_query_support(self, mock_version):
       self.printHeader('get_host_VLUNs_no_query_support')

      # Mock the version number to a version that does not support
      # VLUN querying and then remake the client.
       version = (client.HPE3ParClient
                  .HPE3PAR_WS_MIN_BUILD_VERSION_VLUN_QUERY - 1)
       mock_version.return_value = {'build': version}
       self.cl = client.HPE3ParClient(self.flask_url)

       # Mock the HTTP GET function to track what the call to it was.
       self.cl.http.get = mock.Mock()
       self.cl.http.get.return_value = (
           {}, {'members': [{'hostname': HOST_NAME1}]}
       )
  
       self.cl.createVLUN(VOLUME_NAME1, LUN_1, HOST_NAME1)
       self.cl.getHostVLUNs(HOST_NAME1)
 
       # Check for the request that happens when VLUN querying is unsupported.
       self.cl.http.get.assert_has_calls([mock.call('/vluns')])
 
       self.printFooter('get_host_VLUNs_no_query_support')

    @unittest.skipIf(config['TEST']['unit'].lower() == 'false',
                    "only works with flask server")
    @mock.patch('hpe3parclient.client.HPE3ParClient.getWsApiVersion')
    def test_5_get_VLUN_query_support(self, mock_version):
       self.printHeader('get_VLUN_query_support')
 
       # Mock the version number to a version that supports
       # VLUN querying and then remake the client.
       version = client.HPE3ParClient.HPE3PAR_WS_MIN_BUILD_VERSION_VLUN_QUERY
       mock_version.return_value = {'build': version}
       self.cl = client.HPE3ParClient(self.flask_url)

      # Mock the HTTP GET function to track what the call to it was.
       self.cl.http.get = mock.Mock()
       self.cl.http.get.return_value = (
           {},
           {'members': [{'volumeName': VOLUME_NAME1, 'active': True}]}
       )

       self.cl.createVLUN(VOLUME_NAME1, LUN_1, HOST_NAME1)
       self.cl.getVLUN(VOLUME_NAME1)

       # Check for the request that happens when VLUN querying is supported.
       query = '"volumeName EQ %s"' % VOLUME_NAME1
       expected_query = '/vluns?query=%s' % quote(query.encode("utf-8"))
       self.cl.http.get.assert_has_calls([mock.call(expected_query)])

       self.printFooter('get_VLUN_query_support')

    @unittest.skipIf(config['TEST']['unit'].lower() == 'false', "only works with flask server")
    @mock.patch('hpe3parclient.client.HPE3ParClient.getWsApiVersion')
    def test_5_get_host_VLUNs_query_support(self, mock_version):
       self.printHeader('get_host_VLUNs_query_support')

       # Mock the version number to a version that supports
       # VLUN querying and then remake the client.
       version = client.HPE3ParClient.HPE3PAR_WS_MIN_BUILD_VERSION_VLUN_QUERY
       mock_version.return_value = {'build': version}
       self.cl = client.HPE3ParClient(self.flask_url)

       # Mock the HTTP GET function to track what the call to it was.
       self.cl.http.get = mock.Mock()
       self.cl.http.get.return_value = (
           {},
           {'members': [{'hostname': HOST_NAME1, 'active': True}]}
       )

       self.cl.createVLUN(VOLUME_NAME1, LUN_1, HOST_NAME1)
       self.cl.getHostVLUNs(HOST_NAME1)

       # Check for the request that happens when VLUN querying is supported.
       query = '"hostname EQ %s"' % HOST_NAME1
       expected_query = '/vluns?query=%s' % quote(query.encode("utf-8"))
       self.cl.http.get.assert_has_calls([mock.call(expected_query)])

       self.printFooter('get_host_VLUNs_query_support')

# testing
# suite = unittest.TestLoader().loadTestsFromTestCase(
#     HPE3ParClientVLUNTestCase)
# unittest.TextTestRunner(verbosity=2).run(suite)
