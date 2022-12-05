#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset


# N.B. If only .env files supported variable expansion...
# export CELERY_BROKER_URL="${REDIS_URL}"

python << END
import sys
import time

import redis

suggest_unrecoverable_after = 30
start = time.time()


while True:
    try:
        r = redis.Redis.from_url("${REDIS_URL}")
        r.ping()
        break
    except Exception as error:
        sys.stderr.write("Waiting for Redis to become available...\n")

        if time.time() - start > suggest_unrecoverable_after:
            sys.stderr.write("This is taking longer than expected. The following exception may be indicative of an unrecoverable error: '{}'\n".format(error))

    time.sleep(1)
END

>&2 echo 'Redis is available'

exec "$@"
