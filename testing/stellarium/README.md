Testing communications with Stellarium
---------------------------------------

Getting and showing the equatorial coordinates sent from Stellarium.

### Stellarium configuration

> Configuration window -> Plugins -> Telescope Control -> Configure -> Add

In that window you can introduce the configuration data:

* Telescope controlled by:	**External Software or a remote computer**
	* Name:	**Laser pointer** (or whatever you want..)

* Connection settings:
	* IP:	**localhost**
	* Port:	**10001**

* User interface settings:
	* **Use field of view indicators**


### Example of use:

Once the "virtual telescope" has been configured in Stellarium, you can send the selected object coordinates by **"Ctrl + 1"** keys.

So now we can start the server in order to receive the coordinates, in console:

	./telescope_server.py
	telescope_server.py: run - INFO: Telescope_Server 
	telescope_server.py: handle_accept - DEBUG: Connected: ('127.0.0.1', 37023) 
	telescope_server.py: handle_read - DEBUG: Size: 20, Type: 0, Time: 1342975913635132, RA: 1932791525 (e50e3473), DEC: 17943536 (f0cb1101) 
	coords.py: *rad_2_stellarium_protocol - DEBUG: (hours, degrees): (10.800277, 1.503900) -> (10h48m1.0s, 1º30'14'')*


([More info...](http://yoestuveaqui.es/blog/communications-between-python-and-stellarium-stellarium-telescope-protocol/))
