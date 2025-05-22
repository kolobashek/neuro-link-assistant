function Show-DirTree($path = ".\tests", $indent = "", $exclude = @(".git", "venv", ".venv", "__pycache__", ".vscode", ".github", ".pytest_cache")) {
    $items = Get-ChildItem -Path $path
    foreach ($item in $items) {
        if ($exclude -contains $item.Name) { continue }
        if ($item.Name -like "*.pyc") { continue }
        Write-Host "$indent|-- $($item.Name)"
        if ($item.PSIsContainer) {
            Show-DirTree -path $item.FullName -indent "$indent|   " -exclude $exclude
        }
    }
}

Show-DirTree
