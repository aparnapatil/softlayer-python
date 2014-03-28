"""
    SoftLayer.tests.managers.iscsi_tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import ISCSIManager
from SoftLayer.tests import unittest, FixtureClient
from SoftLayer.tests.fixtures import Network_Storage_Iscsi

from mock import ANY


class ISCSITests(unittest.TestCase):
    def setUp(self):
        self.client = FixtureClient()
        self.iscsi = ISCSIManager(self.client)

    def test_get_iscsi(self):
        result = self.iscsi.get_iscsi(100)
        self.client['Network_Storage_Iscsi'].getObject.assert_called_once_with(
            id=100, mask=ANY)
        self.assertEqual(Network_Storage_Iscsi.getObject, result)

    def test_cancel_iscsi_immediately(self):
        iscsi_id = 6327
        self.iscsi.cancel_iscsi(iscsi_id, immediate=True)
        f = self.client['Billing_Item'].cancelItem
        f.assert_called_once_with(True, True, 'unNeeded', id=iscsi_id)

    def test_cancel_iscsi_without_reason(self):
        iscsi_id = 6327
        self.iscsi.cancel_iscsi(iscsi_id)
        f = self.client['Billing_Item'].cancelItem
        f.assert_called_once_with(False, True, 'unNeeded', id=iscsi_id)

    def test_cancel_iscsi_with_reason(self):
        iscsi_id = 6327
        reason = 'Network Performance'
        self.iscsi.cancel_iscsi(iscsi_id, reason)
        f = self.client['Billing_Item'].cancelItem
        f.assert_called_once_with(False, True, reason, id=iscsi_id)

    def test_order_iscsi_without_recurringFee(self):
        self.iscsi.order_iscsi(test=1, verify=1)
        f = self.client['Product_Order'].placeOrder
        f.assert_called_once_with(
            {'prices': [{'id': 22441}],
             'quantity': 1,
             'location': None,
             'packageId': 0,
             'complexType':
             'SoftLayer_Container_Product_Order_Network_Storage_Iscsi'})

    def test_delete_snapshot(self):
        self.iscsi.delete_snapshot(1)
        self.client[
            'Network_Storage_Iscsi'].deleteObject.assert_called_once_with(id=1)

    def test_create_snapshot(self):
        iscsi_id = 100
        self.iscsi.create_snapshot(iscsi_id, 'unNeeded')
        f = self.client['Network_Storage_Iscsi'].createSnapshot
        f.assert_called_once_with('unNeeded', id=iscsi_id)

    def test_order_snapshot_space(self):
        iscsi_id = 100
        capacity = 20
        self.iscsi.order_snapshot_space(iscsi_id, capacity)
        f = self.client['Product_Order'].placeOrder
        f.assert_called_once_with(
            {'volumeId': 100,
             'location': 138124,
             'packageId': 0,
             'complexType':
             'SoftLayer_Container_\
Product_Order_Network_Storage_Iscsi_SnapshotSpace',
             'prices': [{'id': 22501}],
             'quantity': 1
             })

    def test_restore_from_snapshot(self):
        volume_id = 100
        snapshot_id = 101
        self.iscsi.restore_from_snapshot(volume_id, snapshot_id)
        f = self.client['Network_Storage_Iscsi'].restoreFromSnapshot
        f.assert_called_once_with(101, id=100)
