getObject = {
    'accountId': 278184,
    'billingItem': {'id': 6327},
    'capacityGb': 20,
    'createDate': '2014-03-14T06:50:15-04:00',
    'guestId': '',
    'hardwareId': '',
    'hostId': '',
    'id': 100,
    'nasType': 'ISCSI',
    'notes': """{'status': 'available', 'name': u'IBMI278184-201', 'id':
u'702dc07d-b04b-49eb-9ffc-cb4493470df9'}""",
    'password': 'YAQSb9s3FbEz',
    'serviceProviderId': 1,
    'serviceResource': {'datacenter': {'id': 138124}},
    'serviceResourceBackendIpAddress': '10.2.37.21',
    'serviceResourceName': 'storagesng0101',
    'username': 'IBMI278184-201'
}

createSnapshot = {
    'accountId': 278184,
    'capacityGb': 20,
    'createDate': '2014-03-27T03:51:11-04:00',
    'guestId': '',
    'hardwareId': '',
    'hostId': '',
    'id': 101,
    'nasType': 'ISCSI_SNAPSHOT',
    'parentVolume': {
        'accountId': 278184,
        'capacityGb': 20,
        'createDate': '2014-03-27T03:38:47-04:00',
        'guestId': '',
        'hardwareId': '',
        'hostId': '',
        'id': 100,
        'nasType': 'ISCSI',
        'password': 'L8ta7MRXELwg',
        'properties': [
            {'createDate': '2014-03-27T03:40:22-04:00',
             'modifyDate': '',
             'type': {
                 'description':
                 'Percent of reserved snapshot space that is available',
                 'keyname': 'SNAPSHOT_RESERVE_AVAILABLE',
                 'name': 'Snaphot Reserve Available'},

             'value': '100',
             'volumeId': 2678430}],

        'propertyCount': 0,
        'serviceProviderId': 1,
        'name': 'storagedal0506',
        'snapshotCapacityGb': '40',
        'username': 'IBMI278184-211'},
    'password': 'L8ta7MRXELwg',
                'serviceProviderId': 1,
                'serviceResource': {'backendIpAddress': '10.1.145.26',
                                    'name': 'storagedal0506',
                                    'type': {'type': 'ISCSI'}},
                'serviceResourceBackendIpAddress': '10.1.145.26',
                'serviceResourceName': 'storagedal0506',
                'username': 'IBMI278184-211'}

restoreFromSnapshot = True
editObject = True
createObject = getObject
deleteObject = True
