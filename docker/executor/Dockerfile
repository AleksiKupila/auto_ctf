FROM debian:bookworm-slim

# Install needed packages
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip python3-venv nmap curl netcat-traditional iproute2 iputils-ping openssh-client dnsutils && rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-password --gecos "" scanner

USER scanner
WORKDIR /home/scanner

RUN mkdir -p /home/scanner/tests

RUN echo "text file!" > /home/scanner/tests/test.txt

#RUN echo "# <title> Some text here." | pandoc -o /home/scanner/tests/file.docx --pdf-engine=weasyprint

#RUN pandoc /home/scanner/tests/file.docx -o /home/scanner/tests/file.pdf --pdf-engine=weasyprint

CMD ["tail", "-f", "/dev/null"]