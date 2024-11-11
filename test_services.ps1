# Test de servicios
Write-Host "Probando servicios..." -ForegroundColor Green

# Test Servicio de Usuarios
$usersResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/usuarios" -Method Get
Write-Host "Servicio de Usuarios:" -ForegroundColor Yellow
$usersResponse.usuarios | ConvertTo-Json

# Test Servicio de Pedidos
$ordersResponse = Invoke-RestMethod -Uri "http://localhost:5001/api/pedidos" -Method Get
Write-Host "Servicio de Pedidos:" -ForegroundColor Yellow
$ordersResponse.pedidos | ConvertTo-Json

# Test de integración
Write-Host "Probando integracion..." -ForegroundColor Green
$userOrders = Invoke-RestMethod -Uri "http://localhost:5001/api/pedidos/usuario/1" -Method Get
Write-Host "Pedidos del usuario 1:" -ForegroundColor Yellow
$userOrders.pedidos | ConvertTo-Json

# Test Redis Cache con Docker
Write-Host "Comprobando si Redis esta funcionando..." -ForegroundColor Green

# Verificar si Redis está corriendo en Docker
$redisStatus = docker ps --filter "name=redis" --filter "status=running" --format "{{.Names}}"

if ($redisStatus) {
    Write-Host "Redis esta funcionando correctamente." -ForegroundColor Yellow
} else {
    Write-Host "Redis no esta corriendo o no se encontró el contenedor." -ForegroundColor Red
}
