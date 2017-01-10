#from __future__ import print_function
import re
import requests
from orionsdk import SwisClient


#Input your EXPORT servers in this list below If you don't have ssl installed on the npm server leave 'verify' to false
OrionServers=[{'ip':'hostname', 'username':'', 'password':'', 'verify':False},{'ip':'10.10.10.10','username':'', 'password':'','verify':False},{'ip':'hostname','username':'','password':'','verify':False},{'ip':'11.123.134.1','username':'','password':'','verify':False}]

#input your IMPORT (Target) Server below:
TargetServer={'ip':'10.10.1.10', 'username':'', 'password':'','verify':False}
TargetNodes=[]
TargetGroups=[]

def getAllTargetNodes():
    #get all nodes from target server to create index for URI
    swis = SwisClient(TargetServer['ip'], TargetServer['username'], TargetServer['password'], TargetServer['verify'])
    results = swis.query("SELECT IPAddress, Uri FROM Orion.Nodes")
    try:
        for row in results['results']:
            TargetNodes.append({row['IPAddress']:row['Uri']})
        return TargetNodes
    except(KeyError):
        try:
            print results['Message']
        except(KeyError):
            print "Error"
def setAllTargetGroups():
    #get all nodes from target server to create index for URI
    swis = SwisClient(TargetServer['ip'], TargetServer['username'], TargetServer['password'], TargetServer['verify'])
    results = swis.query("SELECT Name, Uri FROM Orion.Container")
    try:
        for row in results['results']:
            TargetGroups.append({row['Name']:row['Uri']})
        return TargetGroups
    except(KeyError):
        try:
            print results['Message']
        except(KeyError):
            print "Error"

def getGroupSubGroups(server, user, pwd, verify=False):
    parents=[]
    swis = SwisClient(server, user, pwd, verify=False)
    #Query may need to be adjusted depending on configuration and version of NPM
    #Selecting all C Containers joined by the memberdefinition table back to the p Parent container which is on the Container table
    #Corner case not tested is non-Unique child container names
    results = swis.query("SELECT c.name, p.name as parent, p.description FROM Orion.Container c JOIN Orion.ContainerMemberDefinition m ON m.Expression = 'Groups.ContainerID='+toString(c.ContainerID) JOIN Orion.Container p ON m.ContainerID=p.ContainerID WHERE m.Entity='Orion.Groups'")
    try:
        for row in results['results']:
            parents.append({'childName':row['name'], 'parentName':row['parent'], 'parentDescription':row['description']})
        return parents
    except(KeyError):
        try:
            print results['Message']
        except(KeyError):
            return "Error"
    return parents

def getNodeGroups(server, user, pwd, verify=False):
    swis = SwisClient(server, user, pwd, verify=False)
    groups=[]
    #Note: this query may be need to be altered depending on the version of NPM and current configuration.
    results = swis.query("SELECT n.IP_Address, n.DNS, c.Name, m.Description FROM Orion.Nodes n JOIN Orion.ContainerMemberDefinition m ON m.Expression = 'Nodes.NodeID='+toString(n.NodeID) JOIN Orion.Container c ON m.ContainerID=c.ContainerID WHERE m.Entity='Orion.Nodes'")
    try:
        for row in results['results']:
            node={'ip':row['IP_Address'], 'hostname':row['DNS'], 'groupname':row['Name'], 'groupdesc':row['Description']}
            groups.append(node)
    except(KeyError):
        try:
            return results['Message']
        except(KeyError):
            return "Error"
    return groups

#Function to return all groups currently in Target server in order to deduplicate entries before inserting.
def getDedupGroups():
    swis = SwisClient(TargetServer['ip'], TargetServer['username'], TargetServer['password'], TargetServer['verify'])
    results = swis.query("SELECT c.name, m.definition FROM Orion.Container c join Orion.ContainerMemberDefinition m on c.ContainerID=m.ContainerID")
    group=[]
    try:
        for row in results['results']:
            node={'name':row['name'], 'definition':row['definition']}
            group.append(node)
    except(KeyError):
        try:
            return results['Message']
        except(KeyError):
            return "Error"
    return group


def getNodeUri(ip):
    for node in TargetNodes:
        for address, uri in node.iteritems():
            if (address==ip):
                return uri
    return None

def getGroupUri(name):
    for group in TargetGroups:
        for group, uri in group.iteritems():
            if  (group==name):
                return uri
    return None


def addNodeGroups(server, un, pwd, container, nodes, desc, verify=False):

    swis = SwisClient(server, un, pwd, verify=False)
    
    #
    # CREATING A NEW GROUP
    #
    # Creating a new group with initial Cisco and Windows devices.
    # Note that all comments are for guidance, examples, etc, but are not necessary to be uncommented to run the code.
    #
    ret = swis.invoke('Orion.Container', 'CreateContainer',
        # group name
        container,

        # owner, must be 'Core'
        'Core',

        # refresh frequency in seconds
        60,

        # Status rollup mode:
        # 0 = Mixed status shows warning
        # 1 = Show worst status
        # 2 = Show best status
        0,

        # group description
        desc,

        # polling enabled/disabled = true/false
        True,

        # group members
        #[
        #    {'Name': 'Cisco Devices',   'Definition': "filter:/Orion.Nodes[Vendor='Cisco']"},
        #    {'Name': 'Windows Devices', 'Definition': "filter:/Orion.Nodes[Vendor='Windows']"}
        #]
        nodes
    )
    return ret
def runImportSubGroups():
    containers=[]
    groups=[]
    groupdesc=[]
    #Populate target node variable:
    getAllTargetNodes()
    #get Target NPM Server groups
    npmGroups=getDedupGroups()
    for npm in OrionServers:
        g=getNodeGroups(npm['ip'],npm['username'],npm['password'],npm['verify'])
        if (g!='Error'):
            containers.append(g)
    for servers in containers:
        for nodes in servers:
            alreadyImported=0
            exists=0
            try:
                groupname=nodes['groupname']
            except:
                break
            try:
                name=nodes['hostname']
            except(KeyError):
                name=''
            try:
                ip=nodes['ip']
            except(KeyError):
                break
            try:
                groupdescription=nodes['groupdesc']
            except(KeyError):
                groupdescription=''
            nodeUri=getNodeUri(ip)
            #If the node is not in the target system the best we can do is a dynamic query(filter)
            if (nodeUri==None):
                nodeUri="filter:/Orion.Nodes[IPAddress="+ip+"]"
            #Check if we already have this item in the Target server
            if ({'name':groupname, 'definition':nodeUri} in npmGroups):
                alreadyImported=1
            #check if Groupname is already existing in list
            for g in groups:
                for key, val in g.iteritems():
                    if (key==groupname):
                        exists=1
            #If it doesn't already exist in list then add it
            if (exists==0 and alreadyImported==0):
                groups.append({groupname:[{'Name':name,'Definition':nodeUri}]})
                groupdesc.append({groupname:groupdescription})
            #If it does exist just append it to the node list inside the groupname dictionary
            if (exists==1 and alreadyImported==0):
                for g in groups:
                    for key, val in g.iteritems():
                        if (key==groupname):
                            val.append({'Name':name,'Definition':nodeUri})
    #Now add in each group to the target server
    for g in groups:
        for key, val in g.iteritems():
            descript= key+' Group'
            #get group description
            for d in groupdesc:
                for name, desc in d.iteritems():
                    if (name==key):
                        if (desc!=None):
                            descript=desc
            #add groups to new server
            print addNodeGroups(TargetServer['ip'], TargetServer['username'], TargetServer['password'], key, val, descript)
    return 'Success!'

def runImportParentGroups():
    setAllTargetGroups()
    parentContainer=[]
    parentGroups=[]
    parentGroupdesc=[]
    #get Target NPM Server groups
    npmGroups=getDedupGroups()
    for npm in OrionServers:
        g=getGroupSubGroups(npm['ip'],npm['username'],npm['password'],npm['verify'])
        if (g!='Error'):
            parentContainer.append(g)
    for servers in parentContainer:
        for nodes in servers:
            alreadyImported=0
            exists=0
            try:
                parentName=nodes['parentName']
            except:
                break
            try:
                childName=nodes['childName']
            except(KeyError):
                name=''
            try:
                parentDescription=nodes['parentDescription']
            except(KeyError):
                parentDescription=''
            groupUri=getGroupUri(childName)
            #If the child is not in the target system the best we can do is a dynamic query(filter)
            if (groupUri==None):
                groupUri="filter:/Orion.Container[Name="+childName+"]"
            #Check if we already have this item in the Target server
            if ({'name':parentName, 'definition':groupUri} in npmGroups):
                alreadyImported=1
            #check if parentName is already existing in list
            for g in parentGroups:
                for key, val in g.iteritems():
                    if (key==parentName):
                        exists=1
            #If it doesn't already exist in list then add it
            if (exists==0 and alreadyImported==0):
                parentGroups.append({parentName:[{'Name':parentName,'Definition':groupUri}]})
                parentGroupdesc.append({parentName:parentDescription})
            #If it does exist just append it to the group list inside the parentName dictionary
            if (exists==1 and alreadyImported==0):
                for g in parentGroups:
                    for key, val in g.iteritems():
                        if (key==parentName):
                            val.append({'Name':parentName,'Definition':groupUri})
    #Now add in each group to the target server
    for g in parentGroups:
        for key, val in g.iteritems():
            descript= key+' Group'
            #get group description
            for d in parentGroupdesc:
                for name, desc in d.iteritems():
                    if (name==key):
                        if (desc!=None):
                            descript=desc
            #add parentGroups to new server
            print addNodeGroups(TargetServer['ip'], TargetServer['username'], TargetServer['password'], key, val, descript)
    return 'Success!'

requests.packages.urllib3.disable_warnings()

if __name__ == '__main__':
    #
    ##Uncomment the lines below to perform the desired task
    #
    #print runImportSubGroups()
    #You may need to repeat the below task a few times to account for multiple nested levels of groups
    #print runImportParentGroups()
