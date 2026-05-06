# BEE Tracker — Operations Manual

This document covers manual deployment steps that aren't part of any
implementation plan because they depend on the user's specific
infrastructure (Windows Server / Linux box / container / SaaS tenant).

## Microsoft Graph app registration

Before `--backend graph` can be used, register an Azure app:

1. Go to https://portal.azure.com → Azure Active Directory → App registrations → New registration
2. Name: "BEE Tracker"
3. Supported account types: "Accounts in this organizational directory only"
4. After creation, note the **Application (client) ID** and **Directory (tenant) ID**
5. Certificates & secrets → New client secret → 24-month expiry → copy the **value** (you won't see it again)
6. API permissions → Add a permission → Microsoft Graph → Application permissions:
   - `Files.ReadWrite.All` (for the workbook)
   - `Mail.Send` (for `bee-send-alerts`)
7. Click "Grant admin consent for <tenant>"
8. Set environment variables on the admin machine:
   ```bash
   export GRAPH_TENANT_ID="<tenant id>"
   export GRAPH_CLIENT_ID="<application id>"
   export GRAPH_CLIENT_SECRET="<secret value>"
   ```

## Entity locator YAML

Each entity's workbook needs a (drive_id, item_id) entry:

```yaml
# graph_locator.yaml
entity_a:
  drive_id: "b!XYZ..."     # SharePoint drive ID
  item_id: "01ABC..."      # Workbook item ID inside the drive
entity_b:
  drive_id: "b!XYZ..."
  item_id: "01DEF..."
```

To find these IDs: `https://graph.microsoft.com/v1.0/sites/<site-id>/drive`
returns the drive metadata; `/items/root:/path/to/BEE_Tracker.xlsx` resolves
the item ID.

## Daemon as a service

### Linux (systemd)

`/etc/systemd/system/bee-tracker.service`:

```ini
[Unit]
Description=BEE Tracker run-queue daemon
After=network.target

[Service]
Type=simple
User=raphy
WorkingDirectory=/opt/bee_tracker
Environment="GRAPH_TENANT_ID=<...>"
Environment="GRAPH_CLIENT_ID=<...>"
Environment="GRAPH_CLIENT_SECRET=<...>"
ExecStart=/opt/bee_tracker/.venv/bin/bee-run-queue-daemon \
  --root /opt/bee_tracker --backend graph --interval 60
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now bee-tracker
journalctl -u bee-tracker -f
```

### Windows (Task Scheduler — simpler than a Windows Service)

Open Task Scheduler → Create Basic Task:
- Trigger: At system startup
- Action: Start a program
- Program: `C:\bee_tracker\.venv\Scripts\bee-run-queue-daemon.exe`
- Arguments: `--root C:\bee_tracker --backend graph --interval 60`
- Settings: Restart the task if it fails (every 5 minutes, up to 3 attempts)

Set environment variables via System Properties → Environment Variables (or in a wrapper batch script that loads them before launching the daemon).

### macOS (launchd, optional)

`~/Library/LaunchAgents/com.example.bee-tracker.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.example.bee-tracker</string>
  <key>ProgramArguments</key>
  <array>
    <string>/opt/bee_tracker/.venv/bin/bee-run-queue-daemon</string>
    <string>--root</string><string>/opt/bee_tracker</string>
    <string>--backend</string><string>graph</string>
    <string>--interval</string><string>60</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>GRAPH_TENANT_ID</key><string><...></string>
    <key>GRAPH_CLIENT_ID</key><string><...></string>
    <key>GRAPH_CLIENT_SECRET</key><string><...></string>
  </dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>/var/log/bee-tracker/out.log</string>
  <key>StandardErrorPath</key><string>/var/log/bee-tracker/err.log</string>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.example.bee-tracker.plist
```

## Scheduled tasks

### Nightly recalc + alerts (cron)

```cron
# /etc/cron.d/bee-tracker
0 2 * * * raphy /opt/bee_tracker/.venv/bin/bee-calculate-score \
  --root /opt/bee_tracker --entity entity_a --backend graph \
  --requested-by nightly@example >> /var/log/bee-tracker/nightly.log 2>&1

0 7 * * * raphy /opt/bee_tracker/.venv/bin/bee-send-alerts \
  --root /opt/bee_tracker --entity entity_a \
  --from-user bee-tracker@example.com >> /var/log/bee-tracker/alerts.log 2>&1
```

Repeat per entity, OR write a small wrapper that loops over
`/opt/bee_tracker/entities/*` and calls the CLI per directory.

## Real SharePoint smoke test

Once env vars + locator are configured, verify with a small entity that
nothing else uses:

```bash
bee-calculate-score --root /opt/bee_tracker --entity smoke-test \
  --backend graph --requested-by you@example -v
```

The first run should show the Graph token being acquired (visible in -v
output), the workbook downloaded, scored, uploaded back. Confirm in
SharePoint that:
- The workbook's Calc_* sheets are populated
- The Dashboard shows the new BEE Level
- The ChangeLog has a new row

If the workbook didn't update, check:
1. The `If-Match` precondition didn't 412 — someone else may have edited mid-run
2. The Graph app has Files.ReadWrite.All consent (not just Files.Read.All)
3. The locator YAML's drive_id/item_id are correct

## Sending an evidence pack to a verifier

Once a verification cycle starts:

```bash
bee-export-evidence-pack --root /opt/bee_tracker --entity entity_a \
  --output /tmp/entity_a_evidence_pack_$(date +%Y%m%d).zip
```

Verify the zip's contents (`unzip -l <path>`) before forwarding. Missing
evidence files (referenced in the Evidence sheet but absent on disk) are
logged as warnings rather than included; check stderr for that list.
