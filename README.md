# Website
Website for UF Security Clinic

## Quick Start
To deploy this app, first [install Docker](docs/Docker.md) for your system. 
If you're on Windows or you have privileges to run Docker as the current user, 
you can omit `sudo` from the following commands.

Once you have Docker installed, simply run the following command to get it up
and running:
```
sudo docker compose up
```

If you need to stop the Docker containers, run
```
sudo docker compose down
```

If changes are made to the app, you'll need to rebuild it. Run the following 
command before bringing the app up in order to rebuild it:
```
sudo docker compose build
```

Note that rebuilding the app may clear all data previously associated with
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