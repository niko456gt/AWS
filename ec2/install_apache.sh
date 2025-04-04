#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>Servidor Apache en EC2 funcionando</h1>" > /var/www/html/index.html
echo "<h3>Aqui triunfando</h3>" > /var/www/html/index.html