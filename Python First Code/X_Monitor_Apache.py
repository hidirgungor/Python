Monitor Apache / Nginx Log File
Count the number of hits in a Apache/Nginx
This small script will count the number of hits in a Apache/Nginx log file. 
How it works
This script can easily be adapted to any other log file. 

The script starts with making an empty dictionary for storing the IP addresses andcount how many times they exist. 

Then we open the file (in this example the Nginx access.log file) and read the
content line by line. 

The for loop go through the file and splits the strings to get the IP address. 

The len() function is used to ensure the length of IP address. 

If the IP already exists , increase by 1.
ips = {}

fh = open("/var/log/nginx/access.log", "r").readlines()
for line in fh:
    ip = line.split(" ")[0]
    if 6 < len(ip) <=15:
        ips[ip] = ips.get(ip, 0) + 1
print ips
Test it out
If you now browse to your website, and run the python script, you should see your IP address + the counts. 
