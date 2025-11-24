# Use the official MySQL 8.0 image as the base
FROM mysql:8.0

# Set environment variables
ENV MYSQL_ROOT_PASSWORD=MarkboardRoot@2024! \
    MYSQL_DATABASE=markboard \
    MYSQL_USER=admin \
    MYSQL_PASSWORD=MarkboardAdmin@2024!

# Copy the initialization SQL script
COPY ./init.sql /docker-entrypoint-initdb.d/

EXPOSE 3306

# Add healthcheck for database
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD mysqladmin ping -h localhost --silent