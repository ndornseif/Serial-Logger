# Serial-Logger
Simple script for logging data from a serial port to a file

## Overview
This script reads data from a configured serial port.  
The data is split into points at a specified data separator.  
These data points are then timestamped and saved to a CSV document.  
Use the `SerialConfiguration()` class to modify the script's behavior.  

## Example
Read from serial port:  
```
DATA1\r\n
DATA2\r\n
```
Written to file:  
```
2023-06-15T20:46:30.918932,DATA1\n
2023-06-15T20:46:41.510888,DATA2\n
```

## Other
Published under GPL-3.0 license.  
