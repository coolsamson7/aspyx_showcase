#!/bin/bash
set -euo pipefail

# Absolute paths to packages
ROOT_DIR=$(pwd)
ASPYX_MESSAGE_SERVER_PATH="$ROOT_DIR/packages/aspyx_message_server"

echo "Installing aspyx message server..."
pip install -e "$ASPYX_MESSAGE_SERVER_PATH"

echo "All done!"