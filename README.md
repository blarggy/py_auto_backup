# py_auto_backup
This application is intended to simply copy a directory into a user-specified backup direectory. It supports game server data and a simple rcon cli client.

# Install instructions
Pull source code, create and activate a virtual environment

python -m venv venv
source venv/bin/activate   # On Windows: .\venv\Scripts\activate

pip install -r requirements.txt
pip install .

For Palworld:

remove the check for response ID from ./venv/Lib/site-packages/rcon/source/client.py, comment this code out:

```commandline
    def run(self, command: str, *args: str, encoding: str = "utf-8") -> str:
        """Run a command."""
        request = Packet.make_command(command, *args, encoding=encoding)
        response = self.communicate(request)

        # if response.id != request.id:
        #     raise SessionTimeout()

        return response.payload.decode(encoding)
```
Configure your settings per settings.cfg

Run program with:

python main.py