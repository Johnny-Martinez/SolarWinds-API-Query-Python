# SolarWinds-API-Query-Python
Python script to query SolarWinds API for specific details

Author: Jeremiah Owen

Purpose: To utilize the SolarWinds API to query for information

Use: Enter NPM credentials at the top and then change the function call on line 129 to reflect what query you want to run - Save. Make sure that orionAPI.py is executable (`sudo chmod +x orionAPI.py`). Next, install orion python API package with `sudopip install orionsdk`. Then run it with `python orionAPI.py`

# Links:
 - Orion SDK: https://github.com/solarwinds/OrionSDK
 - Orion Python SDK: https://github.com/solarwinds/orionsdk-python
 - Orion Schema: http://solarwinds.github.io/OrionSDK/schema/

_Note: you can customize the queries to pull any information that is in the orion DB. To view the schema see links above._