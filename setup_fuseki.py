import platform
import docker
import requests
import subprocess
import time


def pull_images(cli):
    cli.pull('stain/jena-fuseki')
    cli.pull('busybox')


def create_fuseki_container(cli, volume_name):
    host_config = cli.create_host_config(
            port_bindings={3030: 3030},
            volumes_from=[volume_name])
    cli.create_container('stain/jena-fuseki',
                         detach=True,
                         ports=[3030],
                         host_config=host_config,
                         environment={'ADMIN_PASSWORD': 'pw'},
                         name='fuseki')


def create_fuseki_data_volume(cli):
    cli.create_container('busybox', volumes=['/fuseki'], name='fuseki-data')


def create_dataset(name):
    data = {
        'dbType': 'tdb',
        'dbName': name,
    }
    if name[0] != '/':
        name = '/' + name
    requests.post('http://localhost:3030/$/datasets', data=data, auth=('admin', 'pw'))


def import_dataset_ttl(dataset, filename):
    # !! The use of shell=True is not a good idea. !!
    subprocess.run(f'./s-put http://localhost:3030/{dataset} default {filename}', shell=True)


def setup_fuseki():
    base_url = 'tcp://127.0.0.1:1234' if platform.system() == 'Windows' else 'unix://var/run/docker.sock'
    print('Connect to docker...')
    cli = docker.APIClient(base_url=base_url)
    print('  Done!')
    print('Pulling the images')
    pull_images(cli)
    print('  Done!')
    print('Create `fuseki-data` volume...')
    create_fuseki_data_volume(cli)
    print('  Done!')
    print('Create `fuseki` container...')
    create_fuseki_container(cli, 'fuseki-data')
    print('  Done!')
    print('Wait for fuseki container to start...')
    cli.start('fuseki')
    time.sleep(10)  # Ahah
    print('  Done!')
    print('Install `procps` inside fuseki container...')
    cli.exec_create('fuseki', 'apt-get update')
    cli.exec_create('fuseki', 'apt-get install -y --no-install-recommends procps')
    print('  Done!')
    print('Create `gtfs_sncf` dataset...')
    create_dataset('gtfs_sncf')
    print('  Done!')
    print('Create `gtfs_saintetiennebustram` dataset...')
    create_dataset('gtfs_saintetiennebustram')
    print('  Done!')
    print('Create `parking_argenteuil` dataset...')
    create_dataset('parking_argenteuil')
    print('  Done!')
    print('Import `gtfs_sncf` data...')
    import_dataset_ttl('gtfs_sncf', './data/gtfs_sncf.ttl')
    print('  Done!')
    print('Import `gtfs_saintetiennebustram` data...')
    import_dataset_ttl('gtfs_saintetiennebustram', './data/gtfs_saintetiennebustram.ttl')
    print('  Done!')
    print('Import `parking_argenteuil` data...')
    import_dataset_ttl('parking_argenteuil', './data/parking_argenteuil.ttl')
    print('  Done!')


setup_fuseki()
