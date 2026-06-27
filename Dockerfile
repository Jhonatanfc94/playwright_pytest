# Use the official Locust image as base
FROM locustio/locust

# COPY requirement packages to the container
COPY packages.txt /

# Install dependencies defined in packages.txt
RUN pip install -r /packages.txt