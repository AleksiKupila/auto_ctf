FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends ufw openssh-client

RUN adduser --disabled-password --gecos "" target

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

WORKDIR /home/target

CMD ["tail", "-f", "/dev/null"]