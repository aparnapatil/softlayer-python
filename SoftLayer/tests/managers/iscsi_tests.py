"""
    SoftLayer.tests.managers.iscsi_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import ISCSIManager
from SoftLayer.tests import unittest, FixtureClient
from SoftLayer.tests.fixtures import Network_Storage_Iscsi, Billing_Item, Product_Package

from mock import MagicMock, ANY, call, patch


class ISCSITests(unittest.TestCase):

    def setUp(self):
        self.client = FixtureClient()
        self.iscsi = ISCSIManager(self.client)

    def test_get_iscsi(self):
	result = self.iscsi.get_iscsi(100)
	self.client['Network_Storage_Iscsi'].getObject.assert_called_once_with(id=100, mask=ANY)
	self.assertEqual(Network_Storage_Iscsi.getObject, result)

    def test_cancel_iscsi_immediately(self):
	iscsi_id=6327
	result = self.iscsi.cancel_iscsi(iscsi_id,immediate=True)
	f = self.client['Billing_Item'].cancelItem
	f.assert_called_once_with(True,True,'unNeeded',id=iscsi_id)
	
    def test_cancel_iscsi_without_reason(self):
	iscsi_id=6327
	result = self.iscsi.cancel_iscsi(iscsi_id)
	f = self.client['Billing_Item'].cancelItem
	f.assert_called_once_with(False,True,'unNeeded',id=iscsi_id)
	#self.assertEqual(result,Billing_Item.cancelItem)

    def test_cancel_iscsi_with_reason(self):
	iscsi_id=6327
	reason='Network Performance'
	result = self.iscsi.cancel_iscsi(iscsi_id,reason)
	f = self.client['Billing_Item'].cancelItem
        f.assert_called_once_with(False,True,reason,id=iscsi_id)
        #self.assertEqual(result,Billing_Item.cancelItem)

    #@patch('SoftLayer.managers.iscsi.ISCSIManager.build_order')
    def test_order_iscsi(self):
	#create_dict.return_value = {'test': 1, 'verify': 1}
	self.iscsi.order_iscsi(test=1, verify=1)
	#create_dict.assert_called_once_with(test=1, verify=1)
	f = self.client['Product_Order'].placeOrder
        f.assert_called_once_with({'test': 1, 'verify': 1})
	    
