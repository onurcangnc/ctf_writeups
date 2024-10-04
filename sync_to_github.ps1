$path = "C:\Users\rekal\OneDrive\Belgeler\Projects\ctf_writeups"
$logFile = "C:\Users\rekal\OneDrive\Belgeler\Projects\log.txt"
cd $path

while ($true) {
    try {
        # Öncelikle güncel değişiklikleri çek
        git pull origin main
        
        # Eğer yeni değişiklik yapılmışsa commit ve push yap
        if (git status --porcelain) {
            git add .
            git commit -m "Auto commit on $(Get-Date)"
            git push origin main
            "[$(Get-Date)] Git Process has been completed." | Out-File -Append $logFile
        }
    }
    catch {
        # Hata olursa loga yaz
        "[$(Get-Date)] Hata: $_" | Out-File -Append $logFile
    }
    
    Start-Sleep -Seconds 600  # 10 dakika bekler
}
