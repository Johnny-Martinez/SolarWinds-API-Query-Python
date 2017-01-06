import orionsdk
from orionsdk import SwisClient
import requests
import csv
#input access credentials
npm_server = '10.10.01.100'
username = ''
password = ''
OutputFileName = 'output.csv'

#This is needed if SSL is not setup.
verify = False
if not verify:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def getUnknownNodes():
    writeCSV(['NodeID','IP','MachineType'])
    results = swis.query("SELECT NodeID, IPAddress, MachineType FROM Orion.Nodes where MachineType='Unknown'")
    try:
        for row in results['results']:
            writeCSV([row['NodeID'], row['IPAddress'], row['MachineType']])
        return results
    except(KeyError):
        try:
            print results['Message']
        except(KeyError):
            print "Error"


def getPollers():
    writeCSV(['EngineID','Pollers','IP'])
    results = swis.query("SELECT EngineID, Pollers, IP FROM Orion.Engines")
    try:
        for row in results['results']:
            writeCSV([row['EngineID'], row['Pollers'], row['IP']])
        return results
    except(KeyError):
        try:
            print results['Message']
        except(KeyError):
            print "Error"

def writeCSV(row):
	with open(OutputFileName, 'a') as csvfile:
	    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	    writer.writerow(row)
	    return

swis = SwisClient(npm_server, username, password, verify=False)
def getNodes():
    writeCSV(['NodeID','IP','Location'])
    results = swis.query("SELECT NodeID, IPAddress, Location FROM Orion.Nodes")
    try:
        for row in results['results']:
            writeCSV([row['NodeID'], row['IPAddress'], row['Location']])
        return results
    except(KeyError):
        try:
            print results['Message']
    	except(KeyError):
    		print "Error"
def getNodesDetails():
    writeCSV(['NodeID','IP','Community','RWCommunity','SNMPVersion'])
    results = swis.query("SELECT NodeID, IPAddress, Community, RWCommunity, SNMPVersion FROM Orion.Nodes ORDER BY Community")
    try:
        for row in results['results']:
            writeCSV([row['NodeID'], row['IPAddress'], row['Community'], row['RWCommunity']])
        return results
    except(KeyError):
        try:
            print results['Message']
        except(KeyError):
            print "Error"

def getNodeGroups():
    writeCSV(['IP Address','DNS','Name of Container', 'Container ID'])
    results = swis.query("SELECT n.IP_Address, n.DNS, c.Name, m.ContainerID FROM Orion.Nodes n JOIN Orion.ContainerMemberDefinition m ON m.Expression = 'Nodes.NodeID='+toString(n.NodeID) JOIN Orion.Container c ON m.ContainerID=c.ContainerID WHERE m.Entity='Orion.Nodes'")
    try:
        for row in results['results']:
            writeCSV([row['IP_Address'], row['DNS'], row['Name'], row['ContainerID']])
        return results 
    except(KeyError):
		try:
			print results['Message']
		except(KeyError):
			print "Error"

def getGroupSubGroups():
    writeCSV(['Subgroup','SubGroupID','ParentGroup'])
    results = swis.query("SELECT c.name, m.ContainerID, d.name as groupName FROM Orion.Container c JOIN Orion.ContainerMemberDefinition m ON m.Expression = 'Groups.ContainerID='+toString(c.ContainerID) JOIN Orion.Container d ON m.ContainerID=d.ContainerID WHERE m.Entity='Orion.Groups'")
    try:
        for row in results['results']:
            writeCSV([row['name'], row['ContainerID'], row['Name']])
        return results
    except(KeyError):
		try:
			print results['Message']
		except(KeyError):
			print "Error"
def getCredentials():
    writeCSV(['ID','Name','Description', 'CredentialType', 'CredentialOwner', 'DisplayName', 'InstanceType', 'Uri', 'InstanceSiteId'])
    results = swis.query("SELECT ID, Name, Description, CredentialType, CredentialOwner, DisplayName, InstanceType, Uri, InstanceSiteId FROM Orion.Credential")
    try:
        for row in results['results']:
            writeCSV([row['ID'], row['Name'], row['Description'], row['CredentialType'], row['CredentialOwner'], row['DisplayName'], row['InstanceType'], row['Uri'], row['InstanceSiteId']])
        return results
    except(KeyError):
        try:
            print results['Message']
        except(KeyError):
            print "Error"
def getCredentialsByName(cred):
    writeCSV(['ID','Name','Description', 'CredentialType', 'CredentialOwner', 'DisplayName', 'InstanceType', 'Uri', 'InstanceSiteId'])
    results = swis.query("SELECT ID, Name, Description, CredentialType, CredentialOwner, DisplayName, InstanceType, Uri, InstanceSiteId FROM Orion.Credential where Name="+cred)
    try:
        for row in results['results']:
            writeCSV([row['ID'], row['Name'], row['Description'], row['CredentialType'], row['CredentialOwner'], row['DisplayName'], row['InstanceType'], row['Uri'], row['InstanceSiteId']])
        return results
    except(KeyError):
        try:
            print results['Message']
        except(KeyError):
            print "Error"
            
requests.packages.urllib3.disable_warnings()
if __name__ == '__main__':
    #Type function name below and save and build to get results
    getUnknownNodes()