# Client Monitoring

1. **Copy the files inside the `client` folder to your repository.**

2. **Update the `<your-ip>` placeholder in the `client/configs/otel-collector-config` file with your actual IP address.**

3. **To test the monitoring setup, execute the following command:** docker-compose -f docker-compose-client-monitor.yml up -d

This command will start the monitoring containers in detached mode.

4. **After running the command, you can access the Grafana dashboard at `http://5.75.190.25:3000/d/rYdddlPWk/node-exporter-full?orgId=1` to see if your host appears in the list of monitored hosts.**

5. **If you want to include the monitoring setup in your Jenkins pipeline (Jenkinsfile), you can add the command to start the monitoring containers.**

After completing these steps, you will have a monitoring setup for your client environment, with this having to be done for each individual VM that needs to be monitored. The Grafana dashboard will display metrics and visualizations for the hosts. This data will automatically be monitored and stored in our server so that it can be used later.

# Additional Monitoring Resources

## Grafana Dashboard
Access the Grafana dashboard at: `http://5.75.190.25:3000/d/rYdddlPWk/node-exporter-full?orgId=1`

![Grafana Dashboard](dashboard.png)

## Prometheus Node Exporter
The Prometheus Node Exporter is available at: `http://5.75.190.25:9100/`

## cAdvisor
The cAdvisor dashboard can be accessed at: `http://5.75.190.25:8080/containers/`




