#! /usr/bin/python

from jinja2 import Environment, FileSystemLoader, Template
from yaml import load
from pprint import pprint
import json
import yaml
import requests

def getcmdlist(template, userinfo):
    env = Environment(loader=FileSystemLoader(""))
    my_template = env.get_template(template)

    with open(userinfo) as myfile:
        data = load(myfile)

    result = my_template.render(data)
    cmdlist = result.split("\n")
    cmdlist.remove("")

    length = len(cmdlist)
    for i in range(length):
        if "source-address" in cmdlist[i]:
            cmdlist[i] = cmdlist[i][0:-3]
    return(cmdlist)

def updateAPI(filepath, baseurl, cmdlist):
    with open(filepath) as userfile:
        userinput = yaml.load(userfile, Loader=yaml.FullLoader)
        token = userinput["token"]
        header = { 'Authorization' : 'Token ' + token, "Content-Type": "application/json" }
        siteurl = baseurl + "/api/v1/orgs/" + userinput["org"] + "/sites"
        sites = requests.get(siteurl, headers=header).json()
        for site in sites:
            usersites = userinput["sites"]
            if usersites.get(site["name"]) != None:
                sitename = site["name"]
                pprint("Site %s needs change" % str(sitename))
                switchurl = baseurl + "/api/v1/sites/" + site["id"] + "/devices?type=switch"
                swobjs = requests.get(switchurl, headers=header).json()
                for switch in swobjs:
                    if usersites[sitename]["switches"].get(switch["name"]) != None:
                        pprint("Switch %s needs change" % str(switch["name"]))
                        puturl = baseurl + "/api/v1/sites/" + site["id"] + "/devices/" + switch["id"]
                        if "additional_config_cmds" in switch:
                            cmdlist.extend(switch["additional_config_cmds"])
                        pushlist = ["\"" + item for item in cmdlist]
                        if(pushlist[len(pushlist)-1] == "\""):
                            pushlist.pop()
                        payload = "{ \"additional_config_cmds\": [" + "\", ".join(pushlist) + "\" ]}"
                        response = requests.put(puturl, data=payload, headers=header)
                        print(response)
                    else:
                        print("No change needed at any existing sites.")

if __name__ == "__main__":
    baseurl = "https://api.mist.com"
    template = "Switch-Template.j2"
    userinfo = "Userinput.yaml"
    cmdlist = getcmdlist(template, userinfo)
    updateAPI(userinfo, baseurl, cmdlist)

# Future improvements:
# 1. Save jinja2 output to a file. This will help as Mist UI doesn't keep track of Junos config and the additional commands can be easily lost
# 2. Make changes to jinja2 output for pushing config to multiple switches in one-go. This will include using a custom string in the dictionary
