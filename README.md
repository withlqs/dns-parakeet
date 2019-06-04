# dns-parakeet

forward each dns request to multiple servers to accelerate dns resolving
 
 
### usage:

&nbsp;&nbsp;parakeet.py [-h] [--debug] list_file
 
 
### positional arguments:

&nbsp;&nbsp;list_file   specify servers' list
 
 
### optional arguments:

&nbsp;&nbsp;-h, --help  show this help message and exit

&nbsp;&nbsp;--debug     debug mode


### Sample

```sudo python3 parakeet.py china.json``` and change system dns resolver to ```127.0.0.1```

probably need root privilege
