'''
Script to backup the database to s3

Usage:
    s3_upload.py <db_path> <config_filename>
'''
import boto3
import subprocess
import tarfile
import yaml

from datetime import datetime
from docopt import docopt

DUMP_LOCATION = '/dump'
DUMP_FILENAME = 'hashtag-exchange-dump.tar.gz'
LOG_LOCATION = '/scripts/log'


def get_config(config_filename):
    with open(config_filename, 'r') as f:
        return yaml.load(f)


def get_s3_client(s3_key, s3_secret):
    return boto3.client(
        's3', aws_access_key_id=s3_key, aws_secret_access_key=s3_secret
    )


def make_backup_key():
    now = datetime.utcnow()
    return 'hashtag_exchange_db_backup_{}'.format(now.isoformat())


def upload(backup_filename, config):
    s3_access_key = config['backup']['S3_AWS_KEY']
    s3_secret_key = config['backup']['S3_AWS_SECRET_KEY']
    s3_bucket = config['backup']['S3_BUCKET']

    s3_client = get_s3_client(s3_access_key, s3_secret_key)
    s3_client.upload_file(backup_filename, s3_bucket, make_backup_key())


def do_dump(db_path, config):
    mongo_user = config['users']['MONGO_DB_DUMP_USER']
    mongo_password = config['passwords']['MONGO_DB_DUMP_PASSWORD']
    mongo_host = 'localhost'
    mongo_port = config['vms']['DIGITAL_OCEAN_MONGO_PORT']

    command = (
        'mongodump --host={} --port={} --username={} --password={} '
        '--out={} --db=hashtagExchange --authenticationDatabase=admin'
    ).format(
        mongo_host, mongo_port, mongo_user, mongo_password, DUMP_LOCATION
    )

    subprocess.check_output(
        command, shell=True
    )

    dump_filename = "{}/{}".format(DUMP_LOCATION, DUMP_FILENAME)
    with tarfile.open(dump_filename, "w:gz") as tar:
        tar.add(DUMP_LOCATION, arcname="hashagExchangeDump")

    return dump_filename


def main(backup_filename, config_filename):
    config = get_config(config_filename)
    dump_file = do_dump(backup_filename, config)
    upload(dump_file, config)


if __name__ == '__main__':
    args = docopt(__doc__)
    db_path = args['<db_path>']
    config_filename = args['<config_filename>']

    main(db_path, config_filename)
