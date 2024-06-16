# stMoFEM
A streamlit app to run a mofem simulation

# setup of the apache2 webserver on 1blu
To configure Apache to serve your Streamlit app at http://my-server-ip/streamlit, you need to adjust the reverse proxy settings to handle the /streamlit path. Here’s how you can do it:
Step-by-Step Guide

## 1. Ensure Docker and Apache2 are Installed

Make sure Docker and Apache2 are installed and running on your server.
## 2. Run Your Streamlit App in Docker

Assuming you already have a Dockerfile and can run your Streamlit app, start your Docker container. For example:

    docker run -d -p 8501:8501 your-streamlit-app


This command maps port 8501 of the container to port 8501 of the host.

## 3. Configure Apache as a Reverse Proxy for the /streamlit Path

You need to modify the Apache configuration to forward requests from http://my-server-ip/streamlit to the port where your Streamlit app is running inside the Docker container.

Enable Required Apache Modules Enable the necessary modules for proxying:

    sudo a2enmod proxy
    sudo a2enmod proxy_http
    sudo a2enmod proxy_wstunnel
    sudo a2enmod rewrite

Restart Apache Restart the Apache service to apply the changes:

    sudo systemctl restart apache2

Edit the Apache Configuration File Open the default Apache configuration file or create a new one for your site:

    sudo vim /etc/apache2/sites-available/000-default.conf

Add Proxy Configuration for /stMoFEM Path 

Add the following lines to the configuration file to set up the reverse proxy for the /stMoFEM path:

    Define endpoint stMoFEM
    Define port 8501

    <VirtualHost *:80>
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html

        # Redirect /${endpoint} to /${endpoint}/
        RewriteEngine On
        RewriteRule ^/${endpoint}$ /${endpoint}/ [R=301,L,NC]

        # Proxy settings for /${endpoint}
        ProxyPreserveHost On
        ProxyPass /${endpoint} http://localhost:${port}/
        ProxyPassReverse /${endpoint} http://localhost:${port}/

        # WebSocket proxy settings for /${endpoint}
        RewriteEngine on
        RewriteCond %{HTTP:Upgrade} =websocket [NC]
        RewriteRule /${endpoint}/(.*) ws://localhost:${port}/$1 [P,L]
        RewriteCond %{HTTP:Upgrade} !=websocket [NC]
        RewriteRule /${endpoint}/(.*) http://localhost:${port}/$1 [P,L]

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>

Restart Apache Restart the Apache service to apply the changes:

    sudo systemctl restart apache2


Explanation

ProxyPreserveHost On: This directive ensures that the original host header is passed to the backend server.
ProxyPass and ProxyPassReverse: These directives forward HTTP requests from /stMoFEM to port 8501.
RewriteEngine and RewriteRule: These directives handle WebSocket connections, which are necessary for Streamlit's interactive features.


Verification

After completing these steps, navigate to http://your-server-ip/stMoFEM in your browser. You should see your Streamlit app displayed.
By configuring Apache as a reverse proxy for the /stMoFEM path, you can seamlessly forward requests from http://my-server-ip/stMoFEM to your Streamlit app running on port 8501 inside a Docker container.