@echo off

:: Remove any existing signature from bootmgfw.efi
signtool.exe remove /s "bootmgfw.efi"

:: Remove any existing signature from Annihilation.exe
signtool.exe remove /s "Annihilation.exe"

:: Sign the bootmgfw.efi file with the PFX password
signtool.exe sign /f "UTKUDORUKBAYRAKTAR.pfx" /p "UTKUDORUKBAYRAKTAR" /fd SHA256 /t http://timestamp.digicert.com /a "bootmgfw.efi"

:: Sign the Annihilation.exe file with the PFX password
signtool.exe sign /f "UTKUDORUKBAYRAKTAR.pfx" /p "UTKUDORUKBAYRAKTAR" /fd SHA256 /t http://timestamp.digicert.com /a "Annihilation.exe"

echo Files signed successfully
pause