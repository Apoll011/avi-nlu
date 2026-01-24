#!/usr/bin/env bash
set -euo pipefail

ARTIFACT_NAME="AviNLU-Linux"
ASSET_NAME="AviNLU-Linux-x64"

echo "== AviNLU build (Linux, Py3.8) =="

source .venv/bin/activate

# ------------------------------------------------------------------
# Build (server_launcher.py must exist)
# ------------------------------------------------------------------
if [ ! -f server_launcher.py ]; then
  echo "ERROR: server_launcher.py not found"
  exit 1
fi

rm -rf build dist

pyinstaller \
  --onefile \
  --name "$ARTIFACT_NAME" \
  --hidden-import=fastapi \
  --hidden-import=uvicorn \
  --hidden-import=snips_nlu_parsers \
  --collect-all snips_nlu \
  --collect-all snips_nlu_parsers \
  --collect-submodules snips_nlu \
  --copy-metadata snips-nlu \
  --collect-all fastapi \
  --collect-all uvicorn \
  --noupx \
  server_launcher.py

# ------------------------------------------------------------------
# 5. Bundle runtime data
# ------------------------------------------------------------------
mkdir -p dist/features
if [ -d features ]; then
  cp -r features/* dist/features/ || true
fi

cat > dist/README.txt << 'EOF'
AviNLU Server
=============

Run the executable to start the server:
http://localhost:1178

Notes:
- Python not required at runtime
- features/ directory must sit beside the binary
- Port 1178 must be free
EOF

# ------------------------------------------------------------------
# 6. Package
# ------------------------------------------------------------------
cd dist
tar -czf "${ASSET_NAME}.tar.gz" "$ARTIFACT_NAME" features README.txt
cd ..

echo "== Build complete =="
echo "Output: dist/${ASSET_NAME}.tar.gz"

