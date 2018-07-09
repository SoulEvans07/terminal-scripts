# Windows PowerShell prompt coloring

https://stackoverflow.com/questions/5725888/windows-powershell-changing-the-command-prompt

The following command will create a config file for powershell in ${USER_HOME}/Documents/WindowsPowerShell named as Microsoft.PowerShell_profile.ps1

```powershell
new-item -itemtype file -path $profile -force
```

