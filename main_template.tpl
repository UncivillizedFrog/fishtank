<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <title>Fishtank</title>
    <meta http-equiv="refresh" content="20">
    <link rel="stylesheet" type="text/css" href="static/css/topcoat-desktop-light.css">
    <link rel="stylesheet" type="text/css" href="static/fonts/stylesheet.css">
</head>
<body>
<h1>Fishtank</h1>
The current pwm level is {{current_level}}, dim time is {{dim_time}}
%if modding:
    <p>Currently dimming</p>
%else:
    <p>Not dimming at the moment</p>
%end

<form action="release_override" method="put">
  <div class= "topcoat-button-bar">
    <div class = topcoat-button-bar__item">
      <button formaction = "release_override" class="topcoat-button-bar__button">Release Internet Overrides</button>
    </div>
    <div class = "topcoat-button-bar__item">
      <button formaction = "engage_override" class="topcoat-button-bar__button">Engage Internet Overrides</button>
    </div>
  </div>
</form>

<form action="dim_off" method="put">
  <div class="topcoat-button-bar">
    <div class="topcoat-button-bar__item">
      <button formaction="dim_on" class="topcoat-button-bar__button">Dim On</button>
    </div>
    <div class="topcoat-button-bar__item">
      <button formaction="dim_off" class="topcoat-button-bar__button">Dim Off</button>
    </div>
  </div>
</form>



<form action="turn_on" method="put">
  <div class="topcoat-button-bar">
    <div class="topcoat-button-bar__item">
      <button formaction="turn_on" class="topcoat-button-bar__button">Turn On</button>
    </div>
    <div class="topcoat-button-bar__item">
      <button formaction="turn_off" class="topcoat-button-bar__button">Turn Off</button>
    </div>
  </div>
</form>

<form action="set_dim" method="post">
Dim Time(secs): <input class="topcoat-input" type="text" name="dim_time">
<button class="topcoat-button">Set</button>
</form>

<form action="set_brightness" method="post">
Maximum light brightness: <input class="topcoat-input" type="text" name="pwm_min">
<button class="topcoat-button">Set</button>
</form>

<form action="set_uptime" method="post">
Light cycle startup time (0-23): <input class="topcoat-input" type="text" name="dimup_time">
<button class="topcoat-button">Set</button>
</form>

<form action="set_downtime" method="post">
Light cycle shutdown time (0-23): <input class="topcoat-input" type="text" name="dimdown_time">
<button class="topcoat-button">Set</button>
</form>

</body>
