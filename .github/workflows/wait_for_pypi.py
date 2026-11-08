"""Wait until the flamapy packages this one depends on are installable from PyPI.

Run by release.yml before the GitHub release and the upload. The flamapy packages are
released in lock-step, so every internal requirement must be on PyPI at exactly this
package's version: a dev release must not settle for an older .devN that already satisfies
a ``~=`` pin. The requirements are [project].dependencies and the optional extras except
dev/test (test extras may pin packages released after this one). PyPI's simple index is
polled because it is what pip reads; the JSON API can show a version earlier.

With this wait the tags of every repo can be pushed at once: each upload still happens only
after the packages it needs, in dependency order.
"""
import json
import os
import re
import sys
import time
import tomllib
import urllib.error
import urllib.request

INTERNAL = re.compile(r'^(flamapy(?:-[a-z0-9]+)*)\s*(?:\[[^\]]*\])?\s*[~=<>!]', re.IGNORECASE)
NOT_LOCKSTEP = {'flamapy-cudd'}      # released on its own version line
SKIP_EXTRAS = {'dev', 'test'}
INTERVAL_S = 20
HTTP_NOT_FOUND = 404
TIMEOUT_S = int(os.environ.get('FLAMAPY_PYPI_WAIT_S', '3000'))


def internal_requirements(project: dict) -> list[str]:
    requirements = list(project.get('dependencies', []))
    for extra, items in project.get('optional-dependencies', {}).items():
        if extra not in SKIP_EXTRAS:
            requirements += items
    names = set()
    for requirement in requirements:
        match = INTERNAL.match(requirement.strip())
        if match:
            names.add(match.group(1).lower())
    return sorted(names - NOT_LOCKSTEP - {project['name'].lower()})


def on_pypi(name: str, version: str) -> bool:
    request = urllib.request.Request(
        f'https://pypi.org/simple/{name}/',
        headers={'Accept': 'application/vnd.pypi.simple.v1+json', 'Cache-Control': 'no-cache'})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return version in json.load(response).get('versions', [])
    except urllib.error.HTTPError as error:
        if error.code == HTTP_NOT_FOUND:
            return False
        raise
    except urllib.error.URLError:
        return False  # transient network error: try again on the next round


def main() -> int:
    with open('pyproject.toml', 'rb') as file:
        project = tomllib.load(file)['project']
    version = project['version']
    pending = internal_requirements(project)
    if not pending:
        print('No flamapy dependencies to wait for.')
        return 0
    print(f"Waiting for {', '.join(pending)} {version} on PyPI (up to {TIMEOUT_S} s).")
    deadline = time.monotonic() + TIMEOUT_S
    while pending:
        for name in list(pending):
            if on_pypi(name, version):
                print(f'  {name} {version} is on PyPI', flush=True)
                pending.remove(name)
        if not pending:
            break
        if time.monotonic() > deadline:
            print(f"::error::{', '.join(pending)} {version} never appeared on PyPI; check "
                  f'that release first. Nothing was published.')
            return 1
        time.sleep(INTERVAL_S)
    return 0


if __name__ == '__main__':
    sys.exit(main())
