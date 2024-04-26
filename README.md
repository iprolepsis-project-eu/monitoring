# Monitoring 

## Grafana Dashboard 
http://5.75.190.25:3000/d/rYdddlPWk/node-exporter-full?orgId=1

## Prometheus Node Exporter
http://5.75.190.25:9100/

## cAdvisor 
http://5.75.190.25:8080/containers/

# Client Monitoring
1. Copy the files inside client folder for your repository 
2. In **client/configs/otel-collector-config** change **&lt;your-ip&gt;**
3. To test you can execute **"docker-compose -f docker-compose-client-monitor up -d"**  and then go to **http://5.75.190.25:3000/d/rYdddlPWk/node-exporter-full?orgId=1** and see if your host appears in the list of hosts 
4. Don't forget to put the command to startup monitors containers in your JenkinsFile  
