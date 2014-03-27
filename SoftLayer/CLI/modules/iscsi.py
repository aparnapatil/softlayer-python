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
    CLIAbort, ArgumentError, NestedDict, blank, resolve_id, KeyValueTable,
    update_with_template_args, FALSE_VALUES, export_to_template,
    active_txn, transaction_status)
from SoftLayer import ISCSIManager


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
	import pdb
	pdb.set_trace()
        iscsi = ISCSIManager(self.client)

        self._validate_create_args(args)
	order = {
	'size':int(args['--size']),
	}
	location = self._get_location_id(args['--dc'])
	order['dc'] = location
	iscsi.order_iscsi(**order)

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
	raise ArgumentError('Invalid datacenter name: %s'%location)

class CanceliSCSI(CLIRunnable):

    """
usage: sl iscsi cancel <identifier> [options]

Cancel iSCSI Storage

options :
--immediate    Cancels the iSCSI immediately (instead of on the billing
             anniversary)
--reason=REASON    An optional cancellation reason.

"""
    action = 'cancel'
    options = ['confirm']

    def execute(self, args):
	import pdb
	pdb.set_trace()
        iscsi = ISCSIManager(self.client)
        iscsi_id = resolve_id(
            iscsi.resolve_ids,
            args.get('<identifier>'),
            'iSCSI')

        immediate = args.get('--immediate', False)

        reason = args.get('--reason')
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
        iscsi = ISCSIManager(self.client)
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

Options:
--notes=NOTE    An optional note

"""
    action = 'create_snapshot'

    def execute(self, args):
	import pdb
	pdb.set_trace()
        iscsi = ISCSIManager(self.client)
        iscsi_id = resolve_id(iscsi.resolve_ids,
                              args.get('<identifier>'),
                              'iSCSI')
	notes = args.get('--notes')
        iscsi.create_snapshot(iscsi_id, notes)


class OrderIscsiSpace(CLIRunnable):

    """
usage: sl iscsi order_snapshot_space <identifier> [options]

Order iSCSI snapshot space.

Required :
--capacity=Capacity Snapshot Capacity
"""

    action = 'order_snapshot_space'
    required_params = ['--capacity']

    def execute(self, args):
        import pdb
        pdb.set_trace()
        iscsi = ISCSIManager(self.client)
	invalid_args = [k for k in self.required_params if args.get(k) is None]
        if invalid_args:
            raise ArgumentError('Missing required options: %s'
                                % ','.join(invalid_args))
        iscsi_id = resolve_id(
            iscsi.resolve_ids,
            args.get('<identifier>'),
            'iSCSI')
        capacity = args.get('--capacity')
        iscsi.order_snapshot_space(iscsi_id, capacity)

class IscsiDeleteSnapshot(CLIRunnable):

    """
usage: sl iscsi delete_snapshot <identifier> [options]

Delete iSCSI snapshot.

"""
    action = 'delete_snapshot'

    def execute(self, args):
        iscsi = ISCSIManager(self.client)
        snapshot_id = resolve_id(
            iscsi.resolve_ids,
            args.get('<identifier>'),
            'Snapshot')
        iscsi.delete_snapshot(snapshot_id)


class RestoreVolumefromSnapshot(CLIRunnable):

    """
usage: sl iscsi restore_volume <volume_identifier> <snapshot_identifier>

restores volume from existing snapshot.

"""
    action = 'restore_volume'

    def execute(self, args):
        iscsi = ISCSIManager(self.client)
        volume_id = resolve_id(iscsi.resolve_ids,args.get('<volume_identifier>'),'iSCSI')
        snapshot_id = resolve_id(iscsi.resolve_ids,args.get('<snapshot_identifier>'),'Snapshot')
        iscsi.restore_from_snapshot(volume_id, snapshot_id)

class ListISCSISnapshots(CLIRunnable):

    """
    usage: sl iscsi list_snapshots <identifier>

List iSCSI Snapshots
"""
    action = 'list_snapshots'

    def execute(self, args):
        mgr = ISCSIManager(self.client)
        iscsi_id = resolve_id(mgr.resolve_ids,args.get('<identifier>'),'iSCSI')
	iscsi = self.client['Network_Storage_Iscsi']
        snapshots = iscsi.getPartnerships(mask='volumeId,partnerVolumeId,createDate,type', id = iscsi_id)
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
	
