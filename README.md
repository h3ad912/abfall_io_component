[abfallio Custom Component](https://github.com/mk-maddin/abfall_io_component) for homeassistant

# What This Is:

This is a custom component which creates sensors for next trash empyting based on abfall.io / abfallplus.de API. 
It can be configured for your location and will automatically detect available trash types.
I initialy just wanted to add a configuration option for the location, but ended up on a nearly complete rewrite of the code available at [Syralist's repository](https://github.com/Syralist/abfall_io_component).

# What It Does:

Based on the given configuration values it automatically creates sensors with entity_id **`sensor.trash_sensor_<trash name>`**.
These sensors have a state of "days until next empying".

# Installation and Configuration

## Installation
Download the repository and save the "abfallio" folder into your home assistant custom_components directory.

## Getting configuration values
If you found this repository, chances are you already know your waste collection company uses the abfall.io API.
To recieve the required configuration values enable the developer mode in your browser (usually by pressing F12),
then select your configuration on your communities online trash calendar.

Within the "Network" -> Headers" information you will see the corresponding data values within the "Form Data".

## Configuration
Once the files are downloaded and you gathered your configuration values for abfall.io API, 
you’ll need to **update your config** to minimum include the following under the **`abfallio` domain**:

```yaml
abfallio:
  kommune: 2655
  bezirk: 1235
  strasse: 4
```
As I have seen some configurations not working if you not explicitely define your **`api_key`** and your **`modbus`** value, I **highly recommend** to have a minimum configuration like:

```yaml
abfallio:
  kommune: 2655
  bezirk: 1235
  strasse: 4
  api_key: 'bd0c2d0177a0849a905cded5cb734a6f'
  modbus: 'd6c5855a62cf32a4dadbc2831f0f295f'
```
It is possible to defined multiple values for **`strasse`** and **`bezirk`** values as shown in the following:

```yaml
abfallio:
  kommune: 2655
  bezirk: 
    - 1235
    - 6789
  strasse: 
    - 4
    - 5
    - 6
```

Additionally you can configure the **`url`** you would like to use for API access (e.g. if you preferre **`https://`** over **`http://`** or you would like to use abfallplus.de instead of abfall.io).
Furthermore it is possible to define the **`dateformat`** which is used within the API CSV in case your layout is different and you can change the **`zeitraum`** in which time range data is requested.
The following example just redefines the default values in addition to minimum required configuration values :

```yaml
abfallio:
  kommune: 2655
  bezirk: 1235
  strasse: 4
  url: 'http://api.abfall.io'
  dateformat: '%d.%m.%Y'
  zeitraum: '20200101-20301231'
  
```

It is not necessary (and currently not possible, due to an bug in my code I am not able to find,) to define the **`abfallarten`**.
Every **`abfallart`** in the range of 0-99 is automatically detected if dates for it exist and a corresponding sensor created.
Furthermore I plan to make the unit value (currently "Tage bis zur Leerung") and the display_text attribute specific for a language you define.

# Acknowledgements
This code is based on [Tom Beyers Blog](https://beyer-tom.de/blog/2018/11/home-assistant-integration-abfall-io-waste-collection-dates/).
It was adapted in [Syralist's repository](https://github.com/Syralist/abfall_io_component) and forked by myself.
There is also a thread on the [Home Assiantant Forum](https://community.home-assistant.io/t/home-assistant-integration-of-abfall-io-waste-collection-dates-schedule/80160).
