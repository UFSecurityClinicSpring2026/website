# Website
Website for UF Security Clinic

## Deploying
To deploy this app, first install Docker for your system. If you're on Windows
or you have privileges to run Docker as the current user, you can omit `sudo`
from the following commands.

Once you have Docker installed, build the app.
```
sudo docker build --tag 'fscwebsite' .
```

Finally, run the built container.
```
sudo 
```

Sometimes, you might want to rebuild the app. You'll need to remove the old
version first using the following command:
```
sudo docker stop fscwebsite && sudo docker remove fscwebsite
```

build the dockerfile and start the Docker. Don't forget
to forward the appropriate ports. The app listens on port 80 and 443 by default.

## Tech Stack
 * Caddy
 * Flask
 * Python
 * SQLite