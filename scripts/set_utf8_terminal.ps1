# 将当前 PowerShell 会话切换为 UTF-8 输出，避免中文显示乱码。
[Console]::InputEncoding  = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding           = [System.Text.UTF8Encoding]::new($false)

# 设置代码页为 UTF-8（65001）
chcp 65001 | Out-Null

Write-Host "Terminal encoding is now UTF-8 (code page 65001)." -ForegroundColor Green
