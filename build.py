import re
import subprocess
import sys
import tomllib
from datetime import datetime
from pathlib import Path

pyproject = Path("pyproject.toml")
config = tomllib.loads(pyproject.read_text())
version = config["project"]["version"]

if "--bump" in sys.argv:
    date = datetime.now().strftime("%Y.%m.%d")
    old_date = version.lstrip("v").rsplit("-", 1)[0]
    old_n = int(version.rsplit("-", 1)[-1]) if "-" in version else 0

    n = old_n + 1 if old_date == date else 1
    new_version = f"v{date}-{n}"

    content = re.sub(r'^version = ".*"', f'version = "{new_version}"', pyproject.read_text(), flags=re.MULTILINE)
    pyproject.write_text(content)
    print(f"Version: {version} -> {new_version}")
    version = new_version

versionFile = Path("src/_version.py")
versionFileBackup = versionFile.read_text()

versionFile.write_text(f'VERSION = "{version}"\n')
subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "quickplay.spec"], check=True)

if "--bump" in sys.argv:
    versionFile.write_text(versionFileBackup)
