FROM alpine:3.19

# Install needed packages
RUN apk update && apk add --no-cache nmap perl sudo shadow bash nikto nmap-nselibs nmap-scripts

RUN chmod +x /usr/bin/nikto.pl \
 && ln -s /usr/bin/nikto.pl /usr/local/bin/nikto \
 && ln -s /usr/bin/nikto.pl /usr/bin/nikto

# RUN echo "#include /etc/sudoers.d" >> /etc/sudoers

# Create user and group
# RUN addgroup -S wheel || true
RUN adduser -D -s /bin/bash scanner

# Add the specific, passwordless sudo rule for the scanner user
# RUN echo 'scanner ALL=(ALL) NOPASSWD: /usr/bin/nmap, /usr/local/bin/nikto' > /etc/sudoers.d/scanner \
 # && chmod 0440 /etc/sudoers.d/scanner

# Switch to scanner user
USER scanner
WORKDIR /home/scanner

RUN mkdir /home/scanner/tests/

RUN echo "text file!" > /home/scanner/tests/test.txt

#RUN echo "# <title> Some text here." | pandoc -o /home/scanner/tests/file.docx --pdf-engine=weasyprint

#RUN pandoc /home/scanner/tests/file.docx -o /home/scanner/tests/file.pdf --pdf-engine=weasyprint

CMD ["tail", "-f", "/dev/null"]