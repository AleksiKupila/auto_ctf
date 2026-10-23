FROM debian:bookworm-slim

# Install needed packages
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip python3-venv nmap curl netcat-traditional iproute2 iputils-ping openssh-client dnsutils && rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-password --gecos "" target

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

RUN mkdir -p /home/target/tests
RUN echo "text file!" > /home/target/tests/test.txt

USER target
WORKDIR /home/target

CMD ["tail", "-f", "/dev/null"]