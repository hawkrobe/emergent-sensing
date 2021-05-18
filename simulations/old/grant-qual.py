from boto.mturk.connection import MTurkConnection
import sys

from os.path import expanduser
home = expanduser("~")

worker_id = sys.argv[1]

ACCESS_ID = open(home + '/keys/aws-public').next().strip()
SECRET_KEY = open(home + '/keys/aws-private').next().strip()
HOST = 'mechanicalturk.amazonaws.com'

mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                                            aws_secret_access_key=SECRET_KEY,
                                            host=HOST)

mtc.assign_qualification('3JCU2M9SCZTQEZ2N021NJ70XCXMFY2', worker_id)
