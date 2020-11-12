#! /usr/bin/python

from jinja2 import Environment, FileSystemLoader, Template
from yaml import load
from pprint import pprint
import json
import yaml
import requests
import time

def updateswitch(template, baseurl, userinfo):
    with open(userinfo) as userfile:
        data = yaml.load(userfile, Loader=yaml.FullLoader)
    token = data["token"]
    header = { 'Authorization' : 'Token ' + token, "Content-Type": "application/json" }
    siteurl = baseurl + "/api/v1/orgs/" + data["org"] + "/sites"
    msites = requests.get(siteurl, headers=header).json()
    msitenames = []
    for msite in msites:
        msitenames.append(msite["name"])
    usersites = data["sites"]
    for usitename in usersites:
        print("\n\n#Processing site named %s from the input YAML file.\n" % usitename)
        if usitename not in msitenames:
            print("## ERROR! Site %s is not available in Mist. Make sure you create the site and onboard switches before running the script.\n" % usitename)
            time.sleep(1)
        else:
            usiteobj = usersites[usitename]
            for msiteobj in msites:
                if usitename == msiteobj["name"]:
                    msiteid = msiteobj["id"]
                    mswurl = baseurl + "/api/v1/sites/" + msiteid + "/devices?type=switch"
                    mswitches = requests.get(mswurl, headers=header).json()
                    mswitchnames = []
                    for msw in mswitches:
                        mswitchnames.append(msw["name"])
                    userswitches = usiteobj["switches"]
                    for userswitch in userswitches:
                        if userswitch not in mswitchnames:
                            print("## ERROR! Switch named %s under site %s not found in Mist. Make sure you onboard the switch before running this script.\n" % (userswitch, usitename))
                            time.sleep(2)
                        else:
                            print("## Processing changes for switch named %s under site %s." % (userswitch, usitename))
                            for obj in mswitches:
                                if obj["name"] == userswitch:
                                    mswobj = obj
                            uswobj = usiteobj["switches"][userswitch]
                            uswobj["loopback"] = uswobj["interfaces"]["lo0.0"]
                            uswobj["tacacs_servers"] = usiteobj["tacacs_servers"]
                            uswobj["snmp_community"] = usiteobj["snmp"]["community"]
                            cmdlist = getcmdlist(template, uswobj)
                            clicmdsurl = baseurl + "/api/v1/sites/" + msiteid + "/devices/" + mswobj["id"]
                            if ("additional_config_cmds" in msw) & (msw["additional_config_cmds"] != [""]):
                                print("### Additional CLI commands already present for the device. Appending to it now.\n")
                                cmdlist.extend(msw["additional_config_cmds"])
                            pushlist = ["\"" + item for item in cmdlist]
                            if(pushlist[len(pushlist)-1] == "\""):
                                pushlist.pop()
                            payload = "{ \"additional_config_cmds\": [" + "\", ".join(pushlist) + "\" ]}"
                            requests.put(clicmdsurl, data=payload, headers=header)
                            time.sleep(2)

def getcmdlist(template, swobj):
    env = Environment(loader=FileSystemLoader(""))
    my_template = env.get_template(template)
    result = my_template.render(swobj)
    cmdlist = result.split("\n")
    cmdlist.remove("")
    length = len(cmdlist)
    for i in range(length):
        if "source-address" in cmdlist[i]:
            cmdlist[i] = cmdlist[i][0:-3]
    return(cmdlist)

if __name__ == "__main__":
    template = "Switch-Template.j2"
    baseurl = "https://api.mist.com"
    userinfo = "Userinput.yaml"
    updateswitch(template, baseurl, userinfo)