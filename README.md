# Mist-Switch-Specific-Config


## Goal
Push switch specific config to switches that are adopted/claimed in Mist Cloud. This includes setting unique IP addresses on the loopback and various IRB interfaces and using the loopback's IP as the source-address to talk to TACACS server.


## Requirements
1. Install python
2. Pip install requests jinja2 pyyaml
3. Please setup the topology as mentioned in "Demo-Topology.pdf"
4. Interface ranges need to be defined as per your topology in the Mist switch-config template 


## Workflow:
1. User inputs details in the "Userinput.yaml" file
2. Jinja2 template reads the yaml file and prepares Junos config
3. Python uses this config and makes an API call to Mist Cloud
4. Mist Cloud stores the config, and pushes it down to the Juniper switch


## Usage
0. Claim/Adopt EX switch on Mist cloud
1. git clone https://github.com/ankitchadha/Mist-Switch-Specific-Config.git
2. cd Mist-Switch-Specific-Config/
3. Provide switch-specific parameters in "Userinput.yaml" file  
3.1. Insert your token  
3.2. Input Mist org-ID  
3.3. Insert the switch-name for which custom-config needs to be pushed  
3.4. Insert IP address for the loopback, and various IRBs that need to be advertized with OSPF  
4. python Switch-config-with-jinja.py


## Final Result
The switch-specific OSPF configuration should be pushed down to the switch. Two OSPF peerings should come up on the switch, one for each Distribution-Switch. All the local RFC1918 routes should get advertised upstream via OSPF.


## Verification
```
root@EX2300-Demo-Switch> show ospf neighbor
Address          Interface              State     ID               Pri  Dead
10.20.1.4        irb.3510               Full      88.88.88.88      128    34
10.20.1.6        irb.3511               Full      88.88.88.88      128    32

{master:0}
```
