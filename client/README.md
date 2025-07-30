# Client Setup Instructions
## Migration from Older Version

If you're currently running an older version of this monitoring setup, follow these steps to upgrade:

### 0. Create New Setup Directory and Download Required Files

Set up the new monitoring configuration structure:

```bash
# Create new setup directory
mkdir -p /path/to/new/setup/
cd /path/to/new/setup/

# Download the following files form the GitHub repo to the created directory
client/<client-name>/docker-compose.yml
client/<client-name>/.env

# Create new setup config directory
mkdir -p /path/to/new/setup/config
cd /path/to/new/setup/config

# Download the following files form the GitHub repo to the created directory
client/<client-name>/config/otel-collectorconfig.yaml
client/<client-name>/config/promtail-config.yaml
```

### 1. Ensure New .env File Has Same Values as Old .env

Preserve all existing environment variables from your old setup:

```bash
# Navigate to your old setup directory
cd /path/to/old/setup

# Backup and compare existing .env values
cp .env .env.old.backup

# Navigate to new client directory
cd /path/to/new/setup (client/<client-name>)

# Copy old values to new .env, ensuring no variables are lost
cp /path/to/old/setup/.env .env

# Verify all required variables are present
cat .env | grep -E "(SERVER_MONITORING_PUBLIC_IP|HOST_PUBLIC_IP|HOST_NAME)"
```

### 2. Ensure Services Have Same Configuration

Verify that any extra modifications made to the old Docker Compose file and the old OpenTelemetry Collector configuration are also applied in this new version.

### 3. Stop Services from Old Setup

```bash
# Navigate to old setup and stop all services
cd /path/to/old/setup

# Stop services gracefully
docker compose down 
or
docker compose -f docker-compose-file-name.yml down

# Verify all containers are stopped
docker ps | grep -v "CONTAINER ID"

# Check for any remaining processes
docker ps -a | grep "Exited"
```

### 4. Start Services from New Setup

```bash
# Navigate to new client directory
cd /path/to/new/setup (client/<client-name>)

# Start all services
docker compose up -d
or
docker compose -f docker-compose-file-name.yml up -d

# Verify all services are running
docker compose ps

# Check service logs for any errors
docker compose logs --tail=50
```

### 5. Verify Setup in Grafana

Access Grafana dashboard and confirm data flow:

- [http://5.75.190.25:3000](http://5.75.190.25:3000)

You can access one of its dashboards to verify that the variables are set up. 
```
- Home -> Dashboards -> Node Exporter Full
```
