function Show-DirTree($path = ".", $indent = "", $exclude = @(".git", "htmlcov", "venv", ".venv", "__pycache__", ".vscode", ".github", ".pytest_cache")) {
    $items = Get-ChildItem -Path $path
    foreach ($item in $items) {
        if ($exclude -contains $item.Name) { continue }
        if ($item.Name -like "*.pyc") { continue }
        Write-Output "$indent|-- $($item.Name)"
        if ($item.PSIsContainer) {
            Show-DirTree -path $item.FullName -indent "$indent|   " -exclude $exclude
        }
    }
}

# Save output to file
Show-DirTree | Out-File -FilePath "project_structure.txt" -Encoding utf8
Write-Host "Tree saved to: project_structure.txt"
