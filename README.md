# dns-parakeet

accelerate dns resolving by forwarding each dns request to multiple servers
 
 
### usage:

&nbsp;&nbsp;parakeet.py [-h] [--debug] dns_servers_list_file
 
 
### positional arguments:

&nbsp;&nbsp;dns_servers_list_file   specify servers' list
 
 
### optional arguments:

&nbsp;&nbsp;-h, --help  show this help message and exit

&nbsp;&nbsp;--debug     debug mode


### Sample

```sudo python3 parakeet.py china.json``` and change system dns resolver to ```127.0.0.1```

probably need root privilege
