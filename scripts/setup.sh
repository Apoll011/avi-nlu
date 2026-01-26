#!/usr/bin/env bash
set -euo pipefail

echo "== AviNLU setup (Python 3.8 on Ubuntu 24.04) =="

# -------------------------------------------------
# Enable Python 3.8 repository (required on 24.04)
# -------------------------------------------------
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update

# -------------------------------------------------
# System deps
# -------------------------------------------------
sudo apt install -y \
  python3.8 \
  python3.8-venv \
  python3.8-dev \
  build-essential \
  curl \
  patchelf

# -------------------------------------------------
# Virtual environment pinned to 3.8
# -------------------------------------------------
if [ ! -d ".venv" ]; then
  python3.8 -m venv .venv
fi

source .venv/bin/activate

# -------------------------------------------------
# Toolchain baseline
# -------------------------------------------------
python -m pip install --upgrade pip setuptools wheel

# Snips requires this
pip config set global.trusted-host "resources.snips.ai"

# -------------------------------------------------
# Core deps (order matters)
# -------------------------------------------------
pip install --no-cache-dir \
  urllib3==1.26.6 \
  setuptools-rust \
  numpy \
  snips-nlu \
  fastapi \
  uvicorn \
  pyinstaller

# -------------------------------------------------
# Inject utils.py BEFORE language downloads
# -------------------------------------------------
if [ -f utils.py ]; then
  SNIPS_PATH=$(python - << 'EOF'
import snips_nlu, os
print(os.path.dirname(snips_nlu.__file__))
EOF
)
  cp utils.py "$SNIPS_PATH/cli/utils.py"
  echo "utils.py injected into snips_nlu"
fi

# -------------------------------------------------
# Apply NumPy compatibility patch BEFORE downloads
# -------------------------------------------------
python - << 'EOF'
import numpy as np

with open(np.__file__, "a") as f:
    f.write("\nfloat = float\nint = int\nbool = bool\ncomplex = complex\n")

print("NumPy compatibility patch applied")
EOF

# -------------------------------------------------
# Download language entities (now safe)
# -------------------------------------------------
python -m snips_nlu download-language-entities pt_pt
python -m snips_nlu download-language-entities en

# -------------------------------------------------
# Optional project requirements
# -------------------------------------------------
if [ -f requirements.txt ]; then
  pip install --no-cache-dir -r requirements.txt
fi

echo "== Setup finished =="
echo "Activate with: source .venv/bin/activate"

