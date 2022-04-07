# temperature-remote-monitoring
get temperature updates and alerts

<h2>Description:</h2>
<p>This system permits to have an almost live updates of the temperature in a remote place thanks to the internet connection provided by a hotspot of a smartphone with a sim card.<br /> This project become vewy usefull for areas that are not covered with WiFi connection.</p>

<p>
<ul>The components of this projecct are:
  <li> esp8266; </li>
  <li> smartphone;</li>
  <li> server; </li>
  <li> database; </li>
  <li> user device with Telegram installed. </li>
 </ul>
  </p>
  
  <h2>Flow:</h2>
  
<p>The flow of the data is really simple: first the server need to start the load_data.py script on a port, then the esp8266 when powered will connect thanks to the socket on the server port.
The server will recieve every PERIOD(setted in the esp code-DEFAULT=4 minutes) and thanks to the load_data.py code will insert a tuple with date and hour on a database.
The database will be queried by the app.py script that handle the telegram bot requests from the user.
</p>
<br />
<img src="system_scheme.jpg" alt="scheme">
<br />
<h2>What can the user ask?</h2>
<ul>The user can ask for:
  <li>last temperature registeres</li>
  <li>all the temperature for database</li>
  <li>live updates</li>
  <li>alert after the temperature get below a certain threshold</li>
  <li>change the alert threshold</li> 
  <li>a plot of the temperatures from today and the day before only if there are</li>
</ul>
 <p></p>


<p><i>NOTE:</i> the esp8266 uses DS18B20 temperature sensor</p>
