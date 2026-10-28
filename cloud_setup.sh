#!/usr/bin/env bash
# Install what the scripts need in a cloud sandbox. Usage: bash cloud_setup.sh [--posters]
#   --posters  also installs rembg + Playwright Chromium (for poster.py)
# Always run the scripts afterwards with the same `python` (pip is invoked as `python -m pip`
# because the sandbox's `pip` may belong to a different Python version).
set -u
cd "$(dirname "$0")"
pkgs="telethon requests pillow"
[ "${1:-}" = "--posters" ] && pkgs="$pkgs rembg[cpu] playwright"
PIP="python -m pip"

try() { $PIP install -q $pkgs 2>/dev/null; }
# Debian-patched Pythons break source builds (pyaes) with "install_layout"; retry with stdlib distutils.
try || SETUPTOOLS_USE_DISTUTILS=stdlib try || {
  # Last resort: pyaes is pure Python — unpack it next to the scripts and install the rest without it.
  $PIP download -q --no-deps --no-binary :all: pyaes -d /tmp/pyaes && tar -xzf /tmp/pyaes/pyaes-*.tar.gz -C /tmp/pyaes \
    && cp -r /tmp/pyaes/pyaes-*/pyaes ./pyaes
  $PIP install -q --no-deps telethon && $PIP install -q pyasn1 rsa $(echo "$pkgs" | sed 's/telethon//')
}
python -c "import telethon; print('telethon', telethon.__version__)" || exit 1
if [ "${1:-}" = "--posters" ]; then
  python -m playwright install --with-deps chromium >/dev/null 2>&1 || python -m playwright install chromium
fi
echo "setup ok"
