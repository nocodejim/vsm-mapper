    # --- Dockerfile Content ---
    # This content should be placed inside vsm_mermaid_generator/app/Dockerfile

    # Use a lightweight Nginx image as the base
    # Nginx is a web server good for serving static files (like our HTML/JS)
    FROM nginx:alpine

    # Define build arguments for versioning.
    # These values are injected during the Docker build process (see deploy.sh).
    # Default values are provided in case the arguments are not passed during build.
    ARG APP_VERSION="N/A"
    ARG IMAGE_BUILD_TAG="N/A"

    # Set the working directory inside the container
    WORKDIR /usr/share/nginx/html

    # Remove the default Nginx welcome page
    RUN rm -f index.html default.conf

    # Copy the HTML file from the build context (your 'app' directory)
    # into the Nginx html directory inside the container.
    COPY index.html .

    # Substitute placeholders in index.html with build argument values.
    # This uses sed to replace %%APP_VERSION%% and %%IMAGE_BUILD_TAG%%.
    RUN sed -i "s|%%APP_VERSION%%|$APP_VERSION|g" index.html && \
        sed -i "s|%%IMAGE_BUILD_TAG%%|$IMAGE_BUILD_TAG|g" index.html

    # If you had separate CSS or JS files, you would copy them too:
    # COPY style.css .
    # COPY script.js .

    # Expose port 80 (the default port Nginx listens on)
    # Note: The deploy.sh script maps a host port (e.g., 8080) to this container port.
    # We define the internal port here as 8080 to match the script.
    EXPOSE 8080

    # Nginx default command starts the server, but we need it to listen on 8080
    # We can modify the default config or provide a new one.
    # For simplicity, let's just copy a modified config.

    # Create a simple Nginx config file to listen on port 8080
    RUN echo "server {" > /etc/nginx/conf.d/default.conf && \
        echo "    listen 8080;" >> /etc/nginx/conf.d/default.conf && \
        echo "    location / {" >> /etc/nginx/conf.d/default.conf && \
        echo "        root /usr/share/nginx/html;" >> /etc/nginx/conf.d/default.conf && \
        echo "        index index.html;" >> /etc/nginx/conf.d/default.conf && \
        echo "    }" >> /etc/nginx/conf.d/default.conf && \
        echo "}" >> /etc/nginx/conf.d/default.conf

    # The default Nginx command will automatically run when the container starts
    # CMD ["nginx", "-g", "daemon off;"] # This is the default, no need to override usually
    