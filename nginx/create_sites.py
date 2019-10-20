import os
import yaml
from textwrap import dedent

nginxPath = '/etc/nginx/sites-available/'

with open("sites.yaml", 'r') as stream:
	try:
		data = yaml.safe_load(stream)
		sites = data['sites']
		for site in sites.items():
			siteName = site[0]
			#todo iterate through the array of hostnames correctly
			hostName = site[1]['hosts'][0]
			if os.path.isfile(nginxPath + hostName):
				print('{siteName} is already configured'.format(siteName = siteName))
			else:
				contents = dedent('''\
				server {{
					listen 80;
					root /var/www/{siteName};
					index index.php index.html index.htm index.nginx-debian.html;
					server_name {hostName};

					location / {{
							try_files $uri $uri/ /index.php?$args;
					}}

					location ~ \.php$ {{
							include snippets/fastcgi-php.conf;
							fastcgi_pass unix:/var/run/php/php7.2-fpm.sock;
					}}

					location ~ /\.ht {{
							deny all;
					}}
				}}
				''').format(siteName = siteName, hostName = hostName)

				#symlink the config files into sites-enabled
				symLink = 'ln -s /etc/nginx/sites-available/{hostName} /etc/nginx/sites-enabled/'.format(hostName = hostName)
				os.system(symLink)

				#write in the sites-available file
				siteConfigFile = open(nginxPath + hostName, 'w+')
				siteConfigFile.write(contents)
				siteConfigFile.close

				#write into /etc/hosts
				hostsFile = open('/etc/hosts', 'a')
				hostsFile.write('\n127.0.0.1\t'+hostName)
				hostsFile.close

				#restart nginx
				restartNginx = 'systemctl reload nginx'
				os.system(restartNginx)

	except yaml.YAMLError as exc:
		print(exc)

