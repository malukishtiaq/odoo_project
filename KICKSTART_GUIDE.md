# 🚀 Odoo Project Kickstart Guide

## Quick Start Command
When you want to start the project, simply say: **"kick start odoo"**

## What I Will Do Automatically:
1. **Start Odoo server** on http://localhost:8069
2. **Use database**: `zain_live` (Odoo 18)
3. **Open browser** to the correct URL
4. **No explanations needed** - just get it running

## Current Setup Status:
- ✅ **Odoo Version**: 18.0
- ✅ **Database**: `zain_live` (fresh installation)
- ✅ **Port**: 8069
- ✅ **Custom Modules**: `dashboard_pos` available
- ✅ **CSS Issues**: All fixed
- ✅ **Admin Password**: `admin`

## Login Credentials:
- **Database**: `zain_live`
- **Username**: `admin`
- **Password**: `admin`

## Server Command:
```bash
python3.11 odoo-18/odoo-bin --addons-path=odoo-18/addons,custom_modules --data-dir=odoo-data --http-port=8069
```

## Files Committed:
- `DAILY_REQUIREMENTS.md` - Complete setup documentation
- `start_odoo.sh` - Simple startup script
- `custom_modules/dashboard_pos/` - Custom POS dashboard module
- `KICKSTART_GUIDE.md` - This guide

## What's NOT Committed (and why):
- `dump.sql` - Large database backup (excluded by .gitignore)
- `odoo-data/` - Runtime data directory (excluded by .gitignore)
- `odoo-18/` - Odoo core files (excluded by .gitignore)

---
**Last Updated**: 2025-09-04
**Status**: ✅ Ready for daily use
