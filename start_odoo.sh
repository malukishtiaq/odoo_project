#!/bin/bash

# GreenLines Odoo Project - Robust Startup Script
# Starts Odoo detached from this terminal/chat, with PID and rotating logs

set -euo pipefail

PROJECT_DIR="/Volumes/+971503655247/greenlines_project/greenlines_odoo/odoo_project"
PID_FILE="$PROJECT_DIR/odoo.pid"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/odoo_$(date +%Y%m%d_%H%M%S).log"
PORT=8069
ADDONS_PATH="odoo-18/addons,custom_modules"
DATA_DIR="odoo-data"
DB_NAME="zain_live"

echo "🚀 Starting GreenLines Odoo Project..."
echo "📍 Project Directory: $PROJECT_DIR"
echo "🌐 URL: http://localhost:$PORT"
echo "📝 Logs: $LOG_FILE"
echo ""

cd "$PROJECT_DIR"

mkdir -p "$LOG_DIR" "$DATA_DIR/sessions"

echo "🔄 Stopping any existing Odoo processes..."
if [[ -f "$PID_FILE" ]]; then
  OLD_PID="$(cat "$PID_FILE" || true)"
  if [[ -n "${OLD_PID}" ]] && ps -p "$OLD_PID" >/dev/null 2>&1; then
    kill "$OLD_PID" >/dev/null 2>&1 || true
    sleep 1
  fi
  rm -f "$PID_FILE"
fi

# Fallback: kill by pattern and free the port
pkill -f "python3.11.*odoo-bin" 2>/dev/null || true
sleep 1
if lsof -ti:"$PORT" >/dev/null 2>&1; then
  lsof -ti:"$PORT" | xargs kill -9 2>/dev/null || true
fi

echo "▶️  Starting Odoo server in background..."
nohup python3.11 odoo-18/odoo-bin \
  --addons-path="$ADDONS_PATH" \
  --data-dir="$DATA_DIR" \
  --http-port="$PORT" \
  --database="$DB_NAME" \
  --log-level=info \
  >> "$LOG_FILE" 2>&1 &
NEW_PID=$!
echo "$NEW_PID" > "$PID_FILE"

sleep 2

if ps -p "$NEW_PID" >/dev/null 2>&1; then
  echo "✅ Odoo server started (PID: $NEW_PID)"
  echo "🌐 Access your system at: http://localhost:$PORT"
  echo "🔑 Login: admin / admin"
  echo "📊 Database: $DB_NAME"
else
  echo "❌ Failed to start Odoo. Check logs at: $LOG_FILE" >&2
  exit 1
fi
