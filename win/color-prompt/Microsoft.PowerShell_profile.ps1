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
    $hostname = $Env:computername
    $hostname = $hostname.ToLower()
    $hostname = $hostname+".lwr.local"
    return $hostname
}

function getPath {
    $dir = (Get-Item -Path ".\").FullName
    If($dir.StartsWith($HOME)){
        $dir = $dir.Replace($HOME, '~')
    } else {
        $dir = "/Volumes/" + $dir
    }
    $dir = $dir.Replace(':', '')
    $dir = $dir.Replace('\', '/')
    
    return $dir
}

function Global:prompt {
    #Write-Host "ps " -nonewline
    Write-Host $Env:username@$(getHost) -nonewline -foreground Green
    Write-Host ":" -nonewline -foreground White
    Write-Host $(getPath) -nonewline -foreground Blue
    Write-Host $(getGitBranch) -nonewline -foreground Red
    Write-Host "$" -nonewline -foreground White
    return " "
}