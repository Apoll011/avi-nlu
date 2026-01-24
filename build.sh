#!/usr/bin/env bash
set -euo pipefail

ARTIFACT_NAME="AviNLU-Linux"
ASSET_NAME="AviNLU-Linux-x64"

echo "== AviNLU build (Linux, Py3.8) =="

source .venv/bin/activate

rm -rf build dist

SNIPS_PACKAGES=$(ls .venv/lib/python3.8/site-packages | grep '^snips_nlu' | grep -v 'dist-info' | grep -v '__pycache__' || true)

COLLECT_FLAGS=""
METADATA_FLAGS="--copy-metadata snips-nlu"

for pkg in $SNIPS_PACKAGES; do
    COLLECT_FLAGS="$COLLECT_FLAGS --collect-all $pkg"
    # We copy metadata for both hyphenated and underscored versions to be safe
done

pyinstaller \
  --onefile \
  --name "$ARTIFACT_NAME" \
  --hidden-import=snips_nlu_utils \
  --hidden-import=snips_nlu_parsers \
  --hidden-import=snips_nlu_utils.string \
  --hidden-import=snips_nlu_utils.utils \
  $COLLECT_FLAGS \
  $METADATA_FLAGS \
  --collect-submodules snips_nlu_utils \
  --collect-submodules snips_nlu_parsers \
  --collect-all fastapi \
  --collect-all uvicorn \
  --collect-all lingua_franca \
  --noupx \
  --paths=./src \
  main.py

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

1. Run the executable (AviNLU or AviNLU.exe)
2. Server will start on http://localhost:1178
3. Press Ctrl+C to stop the server

REQUIREMENTS:
-------------
- Ensure the 'features' folder is in the same directory as the executable
- Port 1178 must be available

TROUBLESHOOTING:
----------------
- If the server fails to start, check that port 1178 is not in use
- Make sure all required data files are present
- Run from command line to see error messages

For support, please visit: https://github.com/apoll011/avi-nlu

Notes:
- Python not required at runtime
- features/ directory must sit beside the binary
- Port 1178 must be free
EOF


echo "== Build complete =="
echo "Output: dist/${ASSET_NAME}"


