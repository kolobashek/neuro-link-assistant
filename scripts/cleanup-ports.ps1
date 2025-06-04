# Функция для очистки портов
function Clear-Port {
    param(
        [int]$Port = 5000
    )

    Write-Host "🔍 Проверяем порт $Port..." -ForegroundColor Yellow

    # Находим процесс на порту
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue

    if ($connections) {
        foreach ($conn in $connections) {
            $process = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "🔧 Завершаем процесс: $($process.Name) (PID: $($process.Id))" -ForegroundColor Red
                Stop-Process -Id $process.Id -Force
            }
        }

        # Ждем освобождения порта
        Start-Sleep -Seconds 2

        # Проверяем результат
        $stillUsed = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if (-not $stillUsed) {
            Write-Host "✅ Порт $Port освобожден" -ForegroundColor Green
        } else {
            Write-Host "❌ Порт $Port все еще занят" -ForegroundColor Red
        }
    } else {
        Write-Host "✅ Порт $Port свободен" -ForegroundColor Green
    }
}

function Clear-AllFlaskProcesses {
    Write-Host "🔧 Завершаем все Flask процессы..." -ForegroundColor Yellow

    $flaskProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*app.py*" -or $_.CommandLine -like "*flask*"
    }

    foreach ($proc in $flaskProcesses) {
        Write-Host "🔧 Завершаем: $($proc.Name) (PID: $($proc.Id))"
        Stop-Process -Id $proc.Id -Force
    }

    if ($flaskProcesses.Count -gt 0) {
        Write-Host "✅ Завершено $($flaskProcesses.Count) процессов" -ForegroundColor Green
    }
}

# Основная логика
Clear-Port -Port 5000
Clear-AllFlaskProcesses

Write-Host "🎉 Очистка завершена!" -ForegroundColor Green
