#!/bin/bash
set -e

echo "### build aspyx_message_server"
cd packages/aspyx_message_server
hatch build