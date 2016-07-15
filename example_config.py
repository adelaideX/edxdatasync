"""
Created on 13 Jan 2015

@author: a1600975
@modified: Tim Cavanagh	06/01/2016 Modified design to be generic and configurable.

Edit this file to suit your own environment
"""

passphrase = "passforS3"
s3_profile = "yourS3Profile"
package_path = "/Volumes/adelaidex/DataPackages"
path_to_aws = "/usr/local/bin/aws"
path_to_gpg = "/usr/local/bin/gpg"  # /usr/bin/gpg
path_to_logs = package_path + "/logs/"
email_subscribers = ["my.email@emailserver"]
email_sender = "noreply@emailserver"
enable_ingest = True

# clean up the files that we are not using for reporting
remove = ['*/ora', 'AdelaideX-AD101x', 'AdelaideX-addict01', 'AdelaideX-ADDICTIONX',
          'AdelaideX-AdelaideXDemo101x', 'AdelaideX-AdelaideXSandbox', 'AdelaideX-AdXSandbox2',
          'AdelaideX-Code101-', 'AdelaideX-Code101xOCV', 'AdelaideX-Cyberwar', 'AdelaideX-edxTest102x',
          'AdelaideX-Entrep101x-2016', 'AdelaideX-HumBiol101-', 'AdelaideX-Language101', 'AdelaideX-MARIO',
          'AdelaideX-McDevitt', 'AdelaideX-NanoX', 'AdelaideX-TAD', 'AdelaideX-TEST101', 'AdelaideX-UkeX',
          'AdelaideX-Wine101x-2015', 'AdelaideX-WorldofWine101', 'AdelaideX-tim101', 'AdelaideX-NanoTest101']

s3_buckets = {
    "database-data": "course-data/",
    "edge-event-data": "edx-course-data/adelaidex/edge/events/",
    "edx-event-data": "edx-course-data/adelaidex/edx/events/"
}

storage_folders = {
    "database-data": package_path + "/database-data/",
    "edge-event-data": package_path + "/event-data/edge/",
    "edx-event-data": package_path + "/event-data/edx/",
    "database-data-unzipped": package_path + "/unzipped/database-data/",
    "database-data-legacy": package_path + "/database-data/legacy/fallback/",
    "database-data-test": package_path + "/database-data/test/0.7.0/"}

storage_folder_decrypted = {
    "database-data": package_path + "/decrypted/database-data/",
    "edge-event-data": package_path + "/decrypted/event-data/edge/",
    "edx-event-data": package_path + "/decrypted/event-data/edx/",
    "database-data-legacy": package_path + "/decrypted/database-data/legacy/fallback/",
    "database-data-test": package_path + "/decrypted/database-data/test/0.7.0/",
    "ingestor-database-data": package_path + "/database_state",
    "ingestor-clickstream-logs": package_path + "/clickstream-logs"
}

storage_folder_ingestor = {
    "database_state": package_path + "/database_state/",
    "clickstream-logs": package_path + "/clickstream_logs/latest/"
}
