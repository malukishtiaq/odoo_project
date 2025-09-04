#!/bin/bash

# GreenLines Odoo Project - Daily Startup Script
# This script starts the Odoo server with the correct configuration

echo "🚀 Starting GreenLines Odoo Project..."
echo "📍 Project Directory: /Volumes/+971503655247/greenlines_project/greenlines_odoo/odoo_project"
echo "🌐 URL: http://localhost:8069"
echo ""

# Kill any existing Odoo processes
echo "🔄 Stopping any existing Odoo processes..."
pkill -f "python3.11.*odoo-bin" 2>/dev/null || true

# Wait a moment for processes to stop
sleep 2

# Start Odoo server
echo "▶️  Starting Odoo server..."
python3.11 odoo-18/odoo-bin --addons-path=odoo-18/addons --data-dir=odoo-data --http-port=8069

echo ""
echo "✅ Odoo server started successfully!"
echo "🌐 Access your system at: http://localhost:8069"
echo "🔑 Login: admin / admin"
echo "📊 Database: alzain_live"
