import platform
import docker
import requests
import subprocess
import time
import argparse
import zipfile


def connect_docker():
    base_url = 'tcp://127.0.0.1:1234' if platform.system() == 'Windows' else 'unix://var/run/docker.sock'
    print('Connect to docker...')
    cli = docker.APIClient(base_url=base_url)
    print('  Done!')
    return cli


def create_fuseki_container(cli=None, volume_name='fuseki-data'):
    if cli is None:
        cli = connect_docker()
    host_config = cli.create_host_config(
            port_bindings={3030: 3030},
            volumes_from=[volume_name])
    cli.create_container('stain/jena-fuseki',
                         detach=True,
                         ports=[3030],
                         host_config=host_config,
                         environment={'ADMIN_PASSWORD': 'pw'},
                         name='fuseki')


def create_fuseki_data_volume(cli=None):
    if cli is None:
        cli = connect_docker()
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


def pull_images(cli=None):
    if cli is None:
        cli = connect_docker()
    print('Pulling the images')
    cli.pull('stain/jena-fuseki')
    cli.pull('busybox')
    print('  Done!')


def create_containers(cli=None):
    if cli is None:
        cli = connect_docker()
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


def create_datasets():
    print('Create `gtfs_sncf` dataset...')
    create_dataset('gtfs_sncf')
    print('  Done!')
    print('Create `gtfs_saintetiennebustram` dataset...')
    create_dataset('gtfs_saintetiennebustram')
    print('  Done!')
    print('Create `parking_argenteuil` dataset...')
    create_dataset('parking_argenteuil')
    print('  Done!')


def import_data():
    print('Unzip the data...')
    with zipfile.ZipFile('./data.zip', 'r') as zip_ref:
        zip_ref.extractall('./')
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


def setup_fuseki():
    cli = connect_docker()
    pull_images(cli)
    create_containers(cli)
    create_datasets()
    import_data()


parser = argparse.ArgumentParser(description='Script to setup the fuseki database with docker. Pass no options to build all.')
parser.add_argument('-p', '--pull', action='store_true', default=False,
                    help='Pull the docker images (`stain/jean-fuseki` and `busybox`)')
parser.add_argument('-c', '--container', action='store_true', default=False,
                    help='Create the containers/volumes (`fuseki-data` and `fuseki`)')
parser.add_argument('-d', '--dataset', action='store_true', default=False,
                    help='Create the datasets (`gtfs_sncf`, `gtfs_saintetiennebustram`, and `parking_argenteuil`)')
parser.add_argument('-i', '--import-data', action='store_true', default=False,
                    help='Import the data in the datasets')
args = parser.parse_args()
options = {
    'pull': args.pull,
    'container': args.container,
    'dataset': args.dataset,
    'import_data': args.import_data
}
if (not any(options.values())) or all(options.values()):
    setup_fuseki()
else:
    if options['pull']:
        pull_images()
    if options['container']:
        create_containers()
    if options['dataset']:
        create_datasets()
    if options['import_data']:
        import_data()

