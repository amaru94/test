Write-Host "[Five9 Audio Fix] Restarting Windows audio services..."
Restart-Service Audiosrv -Force
Restart-Service AudioEndpointBuilder -Force
Write-Host "Done. Reopen Five9 and test headset."
