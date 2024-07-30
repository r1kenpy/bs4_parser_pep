from pathlib import Path
from urllib.parse import urljoin

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'

DT_FORMAT = '%d.%m.%Y %H:%M:%S'
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'parser.log'
FOLDER_RESULTS = 'results'
FOLDER_DOWNLOADS = 'downloads'
DOWNLOADS_URL = urljoin(MAIN_DOC_URL, 'download.html')
WHATS_NEW_URL = urljoin(MAIN_DOC_URL, 'whatsnew/')

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}

OUTPUT_PRETTY = 'pretty'
OUTPUT_FILE = 'file'
