# Configuration
$RESOURCE_GROUP="ehms-rg2"  # Changed name to avoid conflicts
$LOCATION="centralindia"
$APP_NAME="ehms-web2"
$DB_SERVER_NAME="ehms-db2"
$REDIS_NAME="ehms-redis2"
$ACR_NAME="ehmsregistry2"
$APP_PLAN="ehms-plan2"

# Login to Azure
Write-Host "Logging into Azure..." -ForegroundColor Green
az login

# Register providers
Write-Host "Registering resource providers..." -ForegroundColor Green
az provider register --namespace Microsoft.DBforPostgreSQL
az provider register --namespace Microsoft.Cache
az provider register --namespace Microsoft.Web
az provider register --namespace Microsoft.ContainerRegistry

# Create Resource Group
Write-Host "Creating Resource Group..." -ForegroundColor Green
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Container Registry
Write-Host "Creating Container Registry..." -ForegroundColor Green
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic
az acr update -n $ACR_NAME --admin-enabled true

# Get ACR credentials
$ACR_USERNAME = az acr credential show --name $ACR_NAME --query "username" -o tsv
$ACR_PASSWORD = az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv

# Create PostgreSQL server
Write-Host "Creating PostgreSQL server..." -ForegroundColor Green
az postgres flexible-server create `
    --resource-group $RESOURCE_GROUP `
    --name $DB_SERVER_NAME `
    --location $LOCATION `
    --admin-user postgres `
    --admin-password "Tr@310305" `
    --sku-name Standard_B1ms `
    --tier Burstable `
    --storage-size 32 `
    --version 13 `
    --yes

# Configure firewall
Write-Host "Configuring PostgreSQL firewall..." -ForegroundColor Green
az postgres flexible-server firewall-rule create `
    --resource-group $RESOURCE_GROUP `
    --name $DB_SERVER_NAME `
    --rule-name allazureips `
    --start-ip-address 0.0.0.0 `
    --end-ip-address 255.255.255.255

# Create database
Write-Host "Creating database..." -ForegroundColor Green
az postgres flexible-server db create `
    --resource-group $RESOURCE_GROUP `
    --server-name $DB_SERVER_NAME `
    --database-name ehms

# Create Redis Cache
Write-Host "Creating Redis Cache..." -ForegroundColor Green
az redis create `
    --resource-group $RESOURCE_GROUP `
    --name $REDIS_NAME `
    --location $LOCATION `
    --sku Basic `
    --vm-size c0

# Create App Service Plan
Write-Host "Creating App Service Plan..." -ForegroundColor Green
az appservice plan create `
    --name $APP_PLAN `
    --resource-group $RESOURCE_GROUP `
    --sku B1 `
    --is-linux

# Build and push Docker image
Write-Host "Building and pushing Docker image..." -ForegroundColor Green
az acr login --name $ACR_NAME
docker-compose -f docker-compose.prod.yml build
docker tag backend-web "$ACR_NAME.azurecr.io/ehms-web:latest"
docker push "$ACR_NAME.azurecr.io/ehms-web:latest"

# Create Web App
Write-Host "Creating Web App..." -ForegroundColor Green
az webapp create `
    --resource-group $RESOURCE_GROUP `
    --plan $APP_PLAN `
    --name $APP_NAME `
    --multicontainer-config-type compose `
    --multicontainer-config-file docker-compose.prod.yml

# Get connection strings
$DB_HOST = az postgres flexible-server show `
    --resource-group $RESOURCE_GROUP `
    --name $DB_SERVER_NAME `
    --query "fullyQualifiedDomainName" -o tsv
$REDIS_KEY = az redis list-keys `
    --resource-group $RESOURCE_GROUP `
    --name $REDIS_NAME `
    --query primaryKey -o tsv

# Configure Web App settings
Write-Host "Configuring Web App settings..." -ForegroundColor Green
az webapp config appsettings set `
    --resource-group $RESOURCE_GROUP `
    --name $APP_NAME `
    --settings `
    WEBSITES_PORT=8000 `
    POSTGRES_DB=ehms `
    POSTGRES_USER=postgres `
    POSTGRES_PASSWORD=Tr@310305 `
    POSTGRES_HOST=$DB_HOST `
    DATABASE_URL="postgresql://postgres:Tr@310305@$DB_HOST:5432/ehms" `
    REDIS_URL="redis://:$REDIS_KEY@$REDIS_NAME.redis.cache.windows.net:6380?ssl=True" `
    DOCKER_REGISTRY_SERVER_URL="https://$ACR_NAME.azurecr.io" `
    DOCKER_REGISTRY_SERVER_USERNAME=$ACR_USERNAME `
    DOCKER_REGISTRY_SERVER_PASSWORD=$ACR_PASSWORD `
    WEBSITES_ENABLE_APP_SERVICE_STORAGE=true

# Import database
Write-Host "Importing database..." -ForegroundColor Green
$env:PGPASSWORD = "Tr@310305"
psql "host=$DB_HOST port=5432 dbname=ehms user=postgres" -f complete_backup_utf8.sql

# Restart web app
Write-Host "Restarting Web App..." -ForegroundColor Green
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP

# Show URL
Write-Host "Deployment complete! Your website URL is:" -ForegroundColor Green
$WEBSITE_URL = az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "defaultHostName" -o tsv
Write-Host "https://$WEBSITE_URL" -ForegroundColor Cyan