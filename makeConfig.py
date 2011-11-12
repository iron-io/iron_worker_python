import ConfigParser

#config = ConfigParser.ConfigParser()
config = {}
config['IronWorker'] = {"token" : "YOUR_TOKEN_HERE", 
                        "host"  : "worker-aws-us-east-1.iron.io",
                        "port"  : "80",
                        "version" : "2",
                        "defaultProjectId" : "YOUR_PROJECT_ID"}

config['CloudCache'] = {"token" : "YOUR_TOKEN_HERE",
                        "host"  : "174.129.12.177",
                        "port"  : "4567"}
 
config['HipChat']    = {"token" : "YOUR_TOKEN_HERE",
                        "host"  : "api.hipchat.com",
                        "port"  : "80",
                        "version" : "v1"}

cnf = ConfigParser.RawConfigParser()
for section in config.keys():
  cnf.add_section(section)
  kvz = config[section]
  for k in kvz.keys():
    cnf.set(section, k, kvz[k])

with open('config_example.ini', 'w') as configfile:
  cnf.write(configfile)

       
