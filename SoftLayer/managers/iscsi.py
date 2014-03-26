import socket
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

    def _find_item_prices(self, size):
        item_prices = []
        _filter = NestedDict({})
        _filter[
            'itemPrices'][
            'item'][
            'description'] = query_filter(
            '~GB iSCSI SAN Storage')
        _filter['itemPrices']['item']['capacity'] = query_filter('%s' % size)
        iscsi_item_prices = self.client['Product_Package'].getItemPrices(
            id=0,
            filter=_filter.to_dict())
        iscsi_item_prices = sorted(
            iscsi_item_prices,
            key=lambda x: (float(x['item']['capacity']),float(x.get('recurringFee', 0))))
        for price in iscsi_item_prices:
            item_prices.append(price['id'])
        return item_prices

    def find_space(self, size):
        _filter = NestedDict({})
        _filter[
            'itemPrices'][
            'item'][
            'description'] = query_filter(
            '~iSCSI SAN Snapshot Space')
        _filter['itemPrices']['item']['capacity'] = query_filter('>=%s' % size)
        item_prices = self.client['Product_Package'].getItemPrices(
            id=0,
            mask='mask[id,item[capacity]]',
            filter=_filter.to_dict())
        item_prices = sorted(
            item_prices,
            key=lambda x: int(x['item']['capacity']))
        if len(item_prices) == 0:
            return None
        return item_prices[0]['id']

    def build_order(self, price, dc):
        order = {
            'complexType':
            'SoftLayer_Container_Product_Order_Network_Storage_Iscsi',
            'location': dc,
            'packageId': 0,  # storage package
            'prices': [{'id': price}],
            'quantity': 1
        }
        return order
	

    def order_iscsi(self, **kwargs):
        """Places an order for iSCSI volume
        """
	size = kwargs.get('size')
	dc = kwargs.get('dc')
	item_prices = self._find_item_prices(size)
        for price in item_prices:
            iscsi_order = self.build_order(price, dc)
            try:
                self.product_order.verifyOrder(iscsi_order)
                order = self.product_order.placeOrder(iscsi_order)
            except Exception as e:
                continue   # if verifyOrder() fails for perticular item-price-id
            return

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

    def create_snapshot(self, volume_id):
        """ Orders a snapshot for given volume
        """

        self.iscsi.createSnapshot('', id=volume_id)

    def Order_snapshot_space(self, **snapshotSpaceOrder):
        """ Orders a snapshot space for given volume
        """

        self.product_order.verifyOrder(snapshotSpaceOrder)
        order = self.product_order.placeOrder(snapshotSpaceOrder)

    def delete_snapshot(self, snapshot_id):
        """ Deletes the snapshot

        :params: integer snapshot_id: the snapshot ID
        """

        self.iscsi.deleteObject(id=snapshot_id)

    def restore_from_snapshot(self, volume_id, snapshot_id):
        """ Restore the volume to snapshot's contents

        :params: integer snapshot_id: the snapshot ID
        """
        self.iscsi.restoreFromSnapshot(snapshot_id, id = volume_id)
