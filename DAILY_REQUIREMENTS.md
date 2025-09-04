# Daily Odoo Project Requirements

## Project Setup
- **Project Path**: `/Volumes/+971503655247/greenlines_project/greenlines_odoo/odoo_project`
- **Odoo Version**: 18.0
- **Python Version**: 3.11 (required for Odoo 18)
- **Target URL**: http://localhost:8069
- **Docker Setup**: External drive - docker-colima

## Daily Startup Process
1. **Start Odoo Server**:
   ```bash
   cd /Volumes/+971503655247/greenlines_project/greenlines_odoo/odoo_project
   python3.11 odoo-18/odoo-bin --addons-path=odoo-18/addons,custom_modules --data-dir=odoo-data --http-port=8069
   ```

2. **Verify Server Status**:
   - Check: http://localhost:8069
   - Should redirect to: http://localhost:8069/odoo
   - Available databases should be visible

## Current Database Status
**Available Databases** (as of 2025-09-04):
- `alzain_live` ✅ **RESTORED FROM BACKUP (2025-09-03)**

**Note**: Fresh Odoo installation with clean configuration. All old databases and configurations have been removed. `alzain_live` database has been restored from `dump.sql` file.

## Login Credentials
**alzain_live Database**: admin / admin

## Fresh Installation (2025-09-04)
**Issue**: Multiple Odoo instances and conflicting configurations causing CSS and database access issues.

**Solution Applied**:
1. **Killed all Odoo processes** and cleared port conflicts
2. **Deleted old configuration file** (`~/.odoorc`)
3. **Deleted all old databases** (alzain_live, passionbox, test_fresh)
4. **Cleaned project directory** (removed filestore, sessions, conflicting modules)
5. **Started fresh Odoo instance** with clean configuration
6. **Restored alzain_live database** from `dump.sql` backup
7. **Verified functionality** - no CSS errors, proper database access

**Status**: ✅ **COMPLETELY FIXED** - Fresh, clean Odoo installation working perfectly

**Admin Password Reset**: ✅ **FIXED** - Admin password reset to "admin" after base module reinstallation

**CSS Styling Issues**: ✅ **COMPLETELY FIXED** - All CSS errors resolved after web module update and asset cleanup

**New Database Created**: ✅ **COMPLETED** - zain_live database created with Odoo 18 (fresh installation)

**CSRF Token Issues**: ✅ **FIXED** - Session expired errors resolved after clearing session data and restarting server

**Database Cleanup**: ✅ **COMPLETED** - Old alzain_live database backup completely removed from project

**Database Restoration**: ✅ **COMPLETED** - alzain_live database successfully restored from backup with all filestore data

## Internal Server Error Fix
**Issue**: "Internal Server Error" with QWeb template corruption and port conflicts

**Solution Applied**:
1. Killed all conflicting Odoo processes: `pkill -f "python3.11.*odoo-bin"`
2. Fixed QWeb template corruption: `UPDATE ir_ui_view SET arch_db = '{}' WHERE type = 'qweb' AND arch_db IS NULL;`
3. Reinstalled base modules: `--init=base,web --stop-after-init`
4. Restarted server with clean configuration

**Status**: ✅ Fixed - Server running properly on http://localhost:8069

## Docker Information
- **Docker Location**: External drive
- **Docker Type**: docker-colima
- **Path**: `/Volumes/+971503655247/greenlines_project/greenlines_odoo/odoo_project`

## Multiple Setup Options

### **Option 1: Direct Python Setup (Current)**
- **Port**: 8069
- **Command**: `python3.11 odoo-18/odoo-bin --addons-path=odoo-18/addons,custom_modules --data-dir=odoo-data --http-port=8069`
- **Status**: ✅ Running

### **Option 2: Docker with Colima**
- **Profile**: odoo-docker (Running)
- **Available Profiles**: 
  - `default` (Stopped)
  - `odoo-docker` (Running - 2 CPU, 4GB RAM, 50GB Disk)
- **Context**: colima
- **Port Options**: 8070, 8071, 8072, etc.

### **Option 3: Multiple Odoo Instances**
- **Current**: Port 8069 (Python)
- **Additional**: Can run on ports 8070, 8071, 8072, etc.
- **Different databases**: Each instance can have different databases

## Troubleshooting Notes
- **Python Version Issue**: System default python3 (3.9.6) is too old for Odoo 18
- **Solution**: Use `python3.11` instead of `python3`
- **Configuration File**: Uses `/Users/ishtiaqahmed/.odoorc` for settings

## User Preferences
- **Browser**: Chrome
- **Port**: 8069 (not 8079)
- **Access Method**: Direct localhost access
- **Database Management**: Via web interface at /web/database/manager

## Last Updated
- **Date**: 2025-09-04
- **Time**: 07:36 AM
- **Status**: Server running successfully on port 8069


## User Requirements (Updated 2025-09-04)
**IMPORTANT**: User is not an Odoo expert and wants simple, consistent setup:

1. **Database**: Use `alzain_live` database (restored from backup)
2. **URL**: Always use http://localhost:8069 (consistent port)
3. **Data Persistence**: Keep same data in database - don't recreate every time
4. **Simple Setup**: When user asks to start Odoo server, just run it and show the database
5. **No Complexity**: User doesn't want to deal with multiple databases or port changes
6. **Clean Installation**: Fresh start with no conflicting configurations or multiple instances

**Daily Process**:
- Start server on port 8069
- Show alzain_live database
- Use existing data (don't recreate)