# -*- coding: utf-8 -*-
import re
import sys
from pip._internal.cli.main import main


def run_pip():
    """Run pip with the script extension stripped from argv[0]."""
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())


if __name__ == '__main__':
    run_pip()
