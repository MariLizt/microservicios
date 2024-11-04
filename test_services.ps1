# Test de servicios
Write-Host "Probando servicios..." -ForegroundColor Green
# Test Servicio de Usuarios
$usersResponse = Invoke-RestMethod -Uri "http://localhost:5000/usuarios" -Method Get
Write-Host "Servicio de Usuarios:" -ForegroundColor Yellow
$usersResponse.usuarios | ConvertTo-Json
# Test Servicio de Pedidos
$ordersResponse = Invoke-RestMethod -Uri "http://localhost:5001/pedidos" -Method Get
Write-Host "Servicio de Pedidos:" -ForegroundColor Yellow
$ordersResponse.pedidos | ConvertTo-Json
# Test de integración
Write-Host "Probando integracion..." -ForegroundColor Green
$userOrders = Invoke-RestMethod -Uri "http://localhost:5001/pedidos/usuario/1" -Method Get
Write-Host "Pedidos del usuario 1:" -ForegroundColor Yellow
$userOrders.usuario | ConvertTo-Json