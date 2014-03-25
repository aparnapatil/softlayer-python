"""
usage: sl iscsi [<command>] [<args>...] [options]

Manage iSCSI targets

The available commands are:
  list                 List iSCSI targets
  create               Create iSCSI target
  detail               Output details about iSCSI
  cancel               cancel iSCSI target
  order_snapshot_space Orders space for snapshots
  create_snapshot      Create snapshot of iSCSI
  delete_snapshot      Delete iSCSI snapshot
  restore_volume       Restores volume from existing snapshot
  list_snapshots       List Snapshots of given iscsi

"""
from SoftLayer.utils import lookup
from SoftLayer.CLI import (
    CLIRunnable, Table, no_going_back, confirm, mb_to_gb, listing,
    FormattedItem)
from SoftLayer.CLI.helpers import (
    CLIAbort, ArgumentError, InvalidInput, NestedDict, blank, resolve_id, KeyValueTable,
    update_with_template_args, FALSE_VALUES, export_to_template,
    active_txn, transaction_status)
from SoftLayer import iSCSIManager


class ListISCSI(CLIRunnable):

    """
    usage: sl iscsi list [options]

List iSCSI accounts
"""
    action = 'list'

    def execute(self, args):
        account = self.client['Account']

        iscsi = account.getIscsiNetworkStorage(
            mask='eventCount,serviceResource[datacenter.name]')
        iscsi = [NestedDict(n) for n in iscsi]

        t = Table([
            'id',
            'datacenter',
            'size',
            'username',
            'password',
            'server'
        ])

        for n in iscsi:
            t.add_row([
                n['id'],
                n['serviceResource']['datacenter'].get('name', blank()),
                FormattedItem(
                    n.get('capacityGb', blank()),
                    "%dGB" % n.get('capacityGb', 0)),
                n.get('username', blank()),
                n.get('password', blank()),
                n.get('serviceResourceBackendIpAddress', blank())])

        return t


class CreateiSCSI(CLIRunnable):

    """
    usage: sl iscsi create --size=SIZE --dc=DC [options]

Order/create an iSCSI storage.

Required:
 --size=SIZE  Size
 --dc=DC   Datacenter
"""
    action = 'create'
    options = ['confirm']
    required_params = ['--size', '--dc']

    def execute(self, args):
        iscsi = iSCSIManager(self.client)

        self._validate_create_args(args)

	size, location = self._parse_create_args(args)
	location = self._get_location_id(location)
        items = iscsi.find_items(int(size))

        iscsi.order_iscsi(items, size, location)

    def _validate_create_args(self, args):
	invalid_args = [k for k in self.required_params if args.get(k) is None]
        if invalid_args:
            raise ArgumentError('Missing required options: %s'
                                % ','.join(invalid_args))

    def _parse_create_args(self, args):

        size = int(args['--size'])
        location = str(args['--dc'])
        return size, location

    def _get_location_id(self, location):
        datacenters = self.client['Location_Datacenter'].getDatacenters(
            mask='mask[longName,id,name]')
        for dc in datacenters:
            if dc['name'] == location:
                self.location = dc['id']
                return self.location
	raise InvalidInput('Inavlid datacenter name: %s'
                                % location)


class CanceliSCSI(CLIRunnable):

    """
usage: sl iscsi [--immediate] [--reason] cancel <identifier> [options]

Cancel iSCSI Storage

options :
--immediate  Cancels the iSCSI immediately (instead of on the billing
             anniversary)
--reason     Reason for cancellation

Prompt Options:
-y, --really  Confirm all prompt actions
"""
    action = 'cancel'
    options = ['confirm']

    def execute(self, args):
        iscsi = iSCSIManager(self.client)
        iscsi_id = resolve_id(
            iscsi.resolve_ids,
            args.get('<identifier>'),
            'iSCSI')
        immediate = args.get('--immediate', False)
        reason = args.get('--reason', str('No longer needed'))

        if args['--really'] or no_going_back(iscsi_id):
            iscsi.cancel_iscsi(iscsi_id, reason, immediate)
        else:
            CLIAbort('Aborted')


class IscsiDetails(CLIRunnable):

    """
usage: sl iscsi detail [--passwords] <identifier> [options]

Get details for a iSCSI

Options:
  --passwords  Show passwords


"""
    action = 'detail'

    def execute(self, args):
        iscsi = iSCSIManager(self.client)
        t = KeyValueTable(['Name', 'Value'])
        t.align['Name'] = 'r'
        t.align['Value'] = 'l'

        iscsi_id = resolve_id(
            iscsi.resolve_ids,
            args.get('<identifier>'),
            'iSCSI')
        result = iscsi.get_iscsi(iscsi_id)
        result = NestedDict(result)

        t.add_row(['id', result['id']])
        t.add_row(['serviceResourceName', result['serviceResourceName']])
        t.add_row(['createDate', result['createDate']])
        t.add_row(['nasType', result['nasType']])
        t.add_row(['capacityGb', result['capacityGb']])
        if result['snapshotCapacityGb']:
        	t.add_row(['snapshotCapacityGb', result['snapshotCapacityGb']])
	t.add_row(['mountableFlag', result['mountableFlag']])
        t.add_row(['serviceResourceBackendIpAddress', result['serviceResourceBackendIpAddress']])
        t.add_row(['price', result['billingItem']['recurringFee']])
        t.add_row(['BillingItemId', result['billingItem']['id']])
        if result.get('notes'):
            t.add_row(['notes', result['notes']])

        if args.get('--passwords'):
            pass_table = Table(['username', 'password'])
            pass_table.add_row([result['username'], result['password']])
            t.add_row(['users', pass_table])

        return t


class IscsiCreateSnapshot(CLIRunnable):

    """
usage: sl iscsi create_snapshot <identifier> [options]

create an iSCSI snapshot.

"""
    action = 'create_snapshot'

    def execute(self, args):
        iscsi = iSCSIManager(self.client)
        iscsi_id = resolve_id(iscsi.resolve_ids,
                              args.get('<identifier>'),
                              'iSCSI')
        iscsi.create_snapshot(iscsi_id)


class OrderIscsiSpace(CLIRunnable):

    """
usage: sl iscsi order_snapshot_space [--capacity=Capacity...] [options]

Order iSCSI snapshot space.

Required :
--capacity = Snapshot Capacity
"""

    action = 'order_snapshot_space'
    required_params = ['--capacity']

    def execute(self, args):
        iscsi = iSCSIManager(self.client)
	invalid_args = [k for k in self.required_params if args.get(k) is None]
        if invalid_args:
            raise ArgumentError('Missing required options: %s'
                                % ','.join(invalid_args))
        iscsi_id = resolve_id(
            iscsi.resolve_ids,
            args.get('<identifier>'),
            'iSCSI')
        item_price = iscsi.find_space(int(args['--capacity'][0]))
        result = iscsi.get_iscsi(
            iscsi_id,
            mask='mask[id,capacityGb,serviceResource[datacenter]]')
        snapshotSpaceOrder = {
            'complexType':
            'SoftLayer_Container_Product_Order_Network_Storage_Iscsi_SnapshotSpace',
            'location': result['serviceResource']['datacenter']['id'],
            'packageId': 0,
            'prices': [{'id': item_price}],
            'quantity': 1,
            'volumeId': iscsi_id}
        iscsi.Order_snapshot_space(**snapshotSpaceOrder)


class IscsiDeleteSnapshot(CLIRunnable):

    """
usage: sl iscsi delete_snapshot <identifier> [options]

Delete iSCSI snapshot.

"""
    action = 'delete_snapshot'

    def execute(self, args):
        iscsi = iSCSIManager(self.client)
        snapshot_id = resolve_id(
            iscsi.resolve_ids,
            args.get('<identifier>'),
            'Snapshot')
        iscsi.delete_snapshot(snapshot_id)


class RestoreVolumefromSnapshot(CLIRunnable):

    """
usage: sl iscsi restore_volume <identifier>

restores volume from existing snapshot.

"""
    action = 'restore_volume'

    def execute(self, args):
        iscsi = iSCSIManager(self.client)
        snapshot_id = resolve_id(
            iscsi.resolve_ids,
            args.get('<identifier>'),
            'Snapshot')
	result = iscsi.get_iscsi(snapshot_id,mask='mask[parentPartnerships.volumeId]')
	volume_id = result['parentPartnerships'][0]['volumeId']
        iscsi.restore_from_snapshot(volume_id, snapshot_id)

class ListISCSISnapshots(CLIRunnable):

    """
    usage: sl iscsi list_snapshots <identifier>

List iSCSI Snapshots
"""
    action = 'list_snapshots'

    def execute(self, args):
        mgr = iSCSIManager(self.client)
        iscsi_id = resolve_id(mgr.resolve_ids,args.get('<identifier>'),'iSCSI')
	iscsi = self.client['Network_Storage_Iscsi']
        snapshots = iscsi.getPartnerships(mask='volumeId,partnerVolumeId,createDate,type', id = iscsi_id)
	print snapshots
        snapshots = [NestedDict(n) for n in snapshots]

        t = Table([
            'id',
            'createDate',
            'name',
	    'description',
        ])
	
        for n in snapshots:
            t.add_row([
                n['partnerVolumeId'],
		n['createDate'],
		n['type']['name'],
	    	n['type']['description'],
		])
	return t
	
