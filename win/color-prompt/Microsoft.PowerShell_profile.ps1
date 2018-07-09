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

function Global:prompt {
    Write-Host "ps " -nonewline
    Write-Host $Env:username -nonewline -foreground Green
    Write-Host ":" -nonewline
    Write-Host (Get-Item -Path ".\").FullName -nonewline -foreground Blue
    Write-Host $(getGitBranch) -nonewline -foreground Red
    Write-Host " $" -nonewline
    return " "
}