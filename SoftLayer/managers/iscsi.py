from SoftLayer.utils import NestedDict, query_filter, IdentifierMixin


class ISCSIManager(IdentifierMixin, object):

    """
    Manages iSCSI storages.

    :param SoftLayer.API.Client client: an API client instance
    """

    def __init__(self, client):
        self.configuration = {}
        self.client = client
        self.iscsi = self.client['Network_Storage_Iscsi']
        self.product_order = self.client['Product_Order']
        self.account = self.client['Account']

    def _find_item_prices(self, size, query):
        item_prices = []
        _filter = NestedDict({})
        _filter[
            'itemPrices'][
            'item'][
            'description'] = query_filter(
            query)
        _filter['itemPrices']['item']['capacity'] = query_filter('%s' % size)
        iscsi_item_prices = self.client['Product_Package'].getItemPrices(
            id=0,
            filter=_filter.to_dict())
        iscsi_item_prices = sorted(
            iscsi_item_prices,
            key=lambda x:
            (float(x['item']['capacity']),
                float(x.get('recurringFee', 0))))
        for price in iscsi_item_prices:
            item_prices.append(price['id'])
        return item_prices

    def build_order(self, item_price, dc):
        order = {
            'complexType':
            'SoftLayer_Container_Product_Order_Network_Storage_Iscsi',
            'location': dc,
            'packageId': 0,  # storage package
            'prices': [{'id': item_price[-1]}],
            'quantity': 1
        }
        return order

    def order_iscsi(self, **kwargs):
        """Places an order for iSCSI volume
        """
        size = kwargs.get('size')
        dc = kwargs.get('dc')
        item_price = self._find_item_prices(size, '~GB iSCSI SAN Storage')
        iscsi_order = self.build_order(item_price, dc)
        self.product_order.verifyOrder(iscsi_order)
        self.product_order.placeOrder(iscsi_order)

    def get_iscsi(self, volume_id, **kwargs):
        """ Get details about a iSCSI storage

        :param integer volume_id: the volume ID
        :returns: A dictionary containing a large amount of information about
                  the specified storage.

        """

        if 'mask' not in kwargs:
            items = set([
                'id',
                'serviceResourceName',
                'createDate',
                'nasType',
                'capacityGb',
                'snapshotCapacityGb',
                'mountableFlag',
                'serviceResourceBackendIpAddress',
                'billingItem',
                'notes',
                'username',
                'password'
            ])
            kwargs['mask'] = "mask[%s]" % ','.join(items)
        return self.iscsi.getObject(id=volume_id, **kwargs)

    def cancel_iscsi(self, volume_id, reason='unNeeded', immediate=False):
        """Cancels the given iSCSI volume.

        :param integer volume_id: the volume ID
        """
        iscsi = self.get_iscsi(
            volume_id,
            mask='mask[id,capacityGb,username,password,billingItem[id]]')
        billingItemId = iscsi['billingItem']['id']
        self.client['Billing_Item'].cancelItem(
            immediate,
            True,
            reason,
            id=billingItemId)

    def create_snapshot(self, volume_id, notes='unNeeded'):
        """ Orders a snapshot for given volume

        :param integer volume_id: the volume ID
        """

        self.iscsi.createSnapshot(notes, id=volume_id)

    def order_snapshot_space(self, volume_id, capacity):
        """ Orders a snapshot space for given volume

        :param integer volume_id: the volume ID
        :param integer capacity: capacity in ~GB
        """
        item_price = self._find_item_prices(
            int(capacity), '~iSCSI SAN Snapshot Space')
        result = self.get_iscsi(
            volume_id, mask='mask[id,capacityGb,serviceResource[datacenter]]')
        snapshotSpaceOrder = {
            'complexType':
            'SoftLayer_Container_Product_Order_\
Network_Storage_Iscsi_SnapshotSpace',
            'location': result['serviceResource']['datacenter']['id'],
            'packageId': 0,
            'prices': [{'id': item_price[0]}],
            'quantity': 1,
            'volumeId': volume_id}
        self.product_order.verifyOrder(snapshotSpaceOrder)
        self.product_order.placeOrder(snapshotSpaceOrder)

    def delete_snapshot(self, snapshot_id):
        """ Deletes the snapshot

        :params: integer snapshot_id: the snapshot ID
        """

        self.iscsi.deleteObject(id=snapshot_id)

    def restore_from_snapshot(self, volume_id, snapshot_id):
        """ Restore the volume to snapshot's contents
        :params: imteger volume_id: the volume ID
        :params: integer snapshot_id: the snapshot ID
        """
        self.iscsi.restoreFromSnapshot(snapshot_id, id=volume_id)
