$Host.PrivateData.DebugBackgroundColor = "Black"
$Host.PrivateData.ErrorBackgroundColor = "Black"

Import-Module PSReadLine
Set-PSReadLineOption -EditMode Emacs
Set-PSReadlineOption -BellStyle None

$env:SHORT_PATH=0

function shortr { $env:SHORT_PATH=1; }
function longr { $env:SHORT_PATH=0; }

function .. { Push-Location ..; }
function ... { Push-Location ../..; }

function n { 
    $dir = (Get-Item -Path ".\").FullName
    $arglist = "-NoExit -command  `"& {Set-Location $dir}`""
    Start-Process powershell -argumentlist $arglist
}

# Searching for commands with up/down arrow is really handy. The
# option "moves to end" is useful if you want the cursor at the end
# of the line while cycling through history like it does w/o searching,
# without that option, the cursor will remain at the position it was
# when you used up arrow, which can be useful if you forget the exact
# string you started the search on.
Set-PSReadLineOption -HistorySearchCursorMovesToEnd 
Set-PSReadlineKeyHandler -Key UpArrow -Function HistorySearchBackward
Set-PSReadlineKeyHandler -Key DownArrow -Function HistorySearchForward

# Clipboard interaction is bound by default in Windows mode, but not Emacs mode.
Set-PSReadlineKeyHandler -Key Shift+Ctrl+C -Function Copy
Set-PSReadlineKeyHandler -Key Ctrl+V -Function Paste

function getGitBranch {
    $branches = (git branch) | Out-String
    $list = $branches.Split([Environment]::NewLine)
    Foreach ($branch in $list) {
        If (($branch).Contains("*")){
            $branch = ($branch).Replace("* ", "")
            $out = $branch
        }
    }
    if($out) { return " ("+$out+")" }
    else { return "" }
}

function getDrive {
    $dir = (Get-Item -Path ".\").FullName
    return $dir.Split(':')[0]
}

function getHost {
    $uname = $Env:username
    $uname = $uname.ToLower()
    $hostname = $Env:computername
    return $uname+'@'+$hostname
}

function countSlashes {
    $word = $args[0]
    $char = "\"
    $result = 0..($word.length - 1) | ? {$word[$_] -eq $char}
    return $result.count
}

function getPath {
    $dir = (Get-Item -Path ".\").FullName
    If($dir.StartsWith($HOME)){
        $dir = $dir.Replace($HOME, '~')
        if(($env:SHORT_PATH -eq 1) -and ($(countSlashes $dir) -gt 2)){
            $dir = $dir -replace "([^~]+\\)+","/.../"
        }
    } else {
        if(($env:SHORT_PATH -eq 1) -and ($(countSlashes $dir) -gt 2)){
            $dir = $dir -replace "([^~]+\\)+","/.../"
            $dir = "/Vol/" + $(getDrive) + $dir
        } else {
            $dir = "/Volumes/" + $dir
        }
    }
    $dir = $dir.Replace(':', '')
    $dir = $dir.Replace('\', '/')
    
    return $dir
}

function Global:prompt {
    #Write-Host "ps " -nonewline
    Write-Host $(getHost) -nonewline -foreground Green
    Write-Host ":" -nonewline -foreground White
    Write-Host $(getPath) -nonewline -foreground Blue
    Write-Host $(getGitBranch) -nonewline -foreground Red
    Write-Host "$" -nonewline -foreground White
    return " "
}

# This key handler shows the entire or filtered history using Out-GridView. The
# typed text is used as the substring pattern for filtering. A selected command
# is inserted to the command line without invoking. Multiple command selection
# is supported, e.g. selected by Ctrl + Click.
Set-PSReadlineKeyHandler -Key F7 `
                         -BriefDescription History `
                         -LongDescription 'Show command history' `
                         -ScriptBlock {
    $pattern = $null
    [Microsoft.PowerShell.PSConsoleReadLine]::GetBufferState([ref]$pattern, [ref]$null)
    if ($pattern)
    {
        $pattern = [regex]::Escape($pattern)
    }

    $history = [System.Collections.ArrayList]@(
        $last = ''
        $lines = ''
        foreach ($line in [System.IO.File]::ReadLines((Get-PSReadlineOption).HistorySavePath))
        {
            if ($line.EndsWith('`'))
            {
                $line = $line.Substring(0, $line.Length - 1)
                $lines = if ($lines)
                {
                    "$lines`n$line"
                }
                else
                {
                    $line
                }
                continue
            }

            if ($lines)
            {
                $line = "$lines`n$line"
                $lines = ''
            }

            if (($line -cne $last) -and (!$pattern -or ($line -match $pattern)))
            {
                $last = $line
                $line
            }
        }
    )
    $history.Reverse()

    $command = $history | Out-GridView -Title History -PassThru
    if ($command)
    {
        [Microsoft.PowerShell.PSConsoleReadLine]::RevertLine()
        [Microsoft.PowerShell.PSConsoleReadLine]::Insert(($command -join "`n"))
    }
}



# Chocolatey profile
# $ChocolateyProfile = "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1"
# if (Test-Path($ChocolateyProfile)) {
#   Import-Module "$ChocolateyProfile"
# }
