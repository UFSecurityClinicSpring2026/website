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
sudo docker run -d --name 'myfscwebsite' -p 80:80 -p 443:443 fscwebsite
```

If you need a shell in the app, run
```
sudo docker exec -it myfscwebsite /bin/bash
```

Sometimes, you might want to rebuild the app. You'll need to remove the old
version first using the following command:
```
sudo docker stop myfscwebsite && sudo docker rm myfscwebsite
```

build the dockerfile and start the Docker. Don't forget
to forward the appropriate ports. The app listens on port 80 and 443 by default.

## Tech Stack
 * Caddy
 * Flask
 * Python
 * SQLite