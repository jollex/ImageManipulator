# ImageManipulator

## How to setup on Digital Ocean
1. Install apache, wsgi, and Pillow dependency stuff
`sudo apt-get install apache2 libapache2-mod-wsgi python-dev libjpeg-dev zlib1g-dev`
2. Enable mod_wsgi
`sudo a2enmod wsgi`
3. Enable mod_rewrite
`sudo a2enmod rewrite`
4. Clone this repo
`git clone https://github.com/jollex/ImageManipulator.git`
5. Install virtualenv if you don't it
`sudo pip install virtualenv`
6. Create new virtualenv
`sudo virtualenv env'
7. Activate new env
`source env/bin/activate`
8. Install requirements
`pip install -r requirements.txt`
9. Create a VirtualHost file
`sudo vi /etc/apache2/sites-available/ImageManipulator.conf
10. Add following text to file
```xml
<VirtualHost *:80>
                ServerName gifoofoo.alexjolly.me
                ServerAdmin alex@alexjolly.me
                WSGIScriptAlias / /var/www/ImageManipulator/ImageManipulator.wsgi
                <Directory /var/www/ImageManipulator/ImageManipulator/>
                        Order allow,deny
                        Allow from all
                </Directory>
                Alias /static /var/www/ImageManipulator/ImageManipulator/static
                <Directory /var/www/ImageManipulator/ImageManipulator/static/>
                        Order allow,deny
                        Allow from all
                </Directory>
                ErrorLog ${APACHE_LOG_DIR}/error.log
                LogLevel warn
                CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```
11. Enable the VirtualHost
`sudo a2ensite ImageManipulator`
12. Restart apache
`service apache2 restart`
