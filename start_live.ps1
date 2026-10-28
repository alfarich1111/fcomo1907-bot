# Start live commentary for one match in the background (survives after the calling session ends).
# Usage: powershell -File start_live.ps1 <espn_event_id> <league_slug>
param([Parameter(Mandatory)][string]$EventId, [string]$League = "ita.1")
$dir = $PSScriptRoot
New-Item -ItemType Directory -Force "$dir\work" | Out-Null
$running = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like "*live.py $EventId*" }
if ($running) { "already running (pid $($running.ProcessId))"; exit 0 }
$p = Start-Process -FilePath "$dir\.venv\Scripts\python.exe" -ArgumentList "live.py $EventId --league $League" `
  -WorkingDirectory $dir -WindowStyle Hidden -PassThru `
  -RedirectStandardOutput "$dir\work\live_$EventId.log" -RedirectStandardError "$dir\work\live_$EventId.err"
"started pid $($p.Id)"
