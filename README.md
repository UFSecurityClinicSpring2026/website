# Website
Website for UF Security Clinic

## Quick Start
To deploy this app, first [install Docker](docs/Docker.md) for your system. 
If you're on Windows or you have privileges to run Docker as the current user, 
you can omit `sudo` from the following commands.

Once you have Docker installed, build the app. From the root directory of
this repository (the directory containing `Dockerfile`), run
```
sudo docker build --tag 'fscwebsite' .
```
Note that you'll need to rebuild every time the source code of the app
changes.

Finally, run the built container. Forward the appropriate ports
```
sudo docker run -d --name 'myfscwebsite' -p 80:80 -p 443:443 fscwebsite
```
If port 443 is taken up on your server, try (replacing `8443` with whatever
port is available on your system)
```
sudo docker run -d --name 'myfscwebsite' -p 8443:443 fscwebsite
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
Note that rebuilding the app will clear all data previously associated with
the app.

## Tech Stack
 * Caddy
 * Flask
 * Python
 * SQLite
 * Linux
 * Docker
 
## License
```
Copyright (C) 2026  Yuliang Huang, Adriel Barzola, Sasha Watanabe, Maxwell
Griffin, Leo Graham, and contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Neither the name of the copyright holders nor the names of its contributors 
may be used to endorse or promote products derived from this software without 
specific prior written permission.
```