import lw3
import re
import tcpip
import manparser

## author : "Milan Tenk"

class NodeInfoFunctions:
    HIERARCHY = 1
    MISSING_MANUAL = 2

hierarchyDebth = 0

#Prints the hierarchy of the nodes and properties.
def printNodePropMet(device, targetFile, usedDirectory, useTab):
    
    global hierarchyDebth
    
    for node in device.GET(usedDirectory,'*'):
        if useTab:
            hierarchyDebth += 1
        if node['property']:
#            print('\t'*hierarchyDebth + '.' + node['name'] + ' = ' + node['value'])
            targetFile.write('\t'*hierarchyDebth + '.' + node['name'] + ' = ' + node['value'] + '\n')
        else:
#            print('\t'*hierarchyDebth + ':' + node['name'] + '()')
            targetFile.write('\t'*hierarchyDebth + ':' + node['name'] + '()' + '\n')
        if useTab:
            hierarchyDebth -= 1
    return

#The printed directories dont fit the documentation criteria:
#        - The manual doesn't have []-s at the beginning, or in case of properties it is not filled.
#        - The description must contain at least 3 words.
#        - The ManParser must be able to interpret it.
#        - The ManParser throws exception while parsing the data
def printIncorrectManuals(device, targetFile, usedDirectory, useTab):
    
    global hierarchyDebth
    global manErrorCounter
    
    for node in device.GET(usedDirectory,'*'):
        if re.match('^[-#+*@&|?]', node['name']):
#            print('Error: caused by one of -#+*@&| characters!')
            targetFile.write('Error: caused by one of -#+*@&| characters!' + usedDirectory + node['name'] + '\n')
            return
        manResponse = device.MANMethod(usedDirectory, node['name'])      
        if not re.match('\[.+\] .+ .+ .+', manResponse[0]['value']):
            if node['property']:
#                print(usedDirectory + node['name'] + '=' + manResponse[0]['value'])
                targetFile.write(usedDirectory + node['name'] + '=' + manResponse[0]['value'] + '\n')
            else:
                if re.match('\[\]', manResponse[0]['value']): #in case of method the [] pattern is valid
                    return
#                print(usedDirectory + node['name'] + '=' + manResponse[0]['value'])
                targetFile.write(usedDirectory + node['name'] + '=' + manResponse[0]['value'] + '\n')
        else:
            manpars = manparser.ManParser()
            try:
                parsedData = manpars.parseManual(manResponse[0]['value'])
            except:
#                print('ERROR caused by parser: ' + usedDirectory + node['name'] + '=' + manResponse[0]['value'])
                targetFile.write('ERROR caused by parser: ' + usedDirectory + node['name'] + '=' + manResponse[0]['value'] + '\n')
                return
            if not parsedData['values']:
#                print(usedDirectory + node['name'] + '=' + manResponse[0]['value'])
                targetFile.write(usedDirectory + node['name'] + '=' + manResponse[0]['value'] + '\n')             
    return


#usedDirectory:  The node, from what we want to get the information.
#neededInfo: Use NodeInfoFunctions for choose the functionality of the function
def printNodeInfo(device, targetFile, usedDirectory, neededInfo):

    global hierarchyDebth    
    
    if neededInfo == NodeInfoFunctions.HIERARCHY:
        if hierarchyDebth == 0:
#            print(usedDirectory)
            targetFile.write(usedDirectory + '\n')

    actualChilden = device.GETChilds(usedDirectory)
    if not actualChilden: 
        #list is empty, properties and functions are found
        if neededInfo == NodeInfoFunctions.HIERARCHY:
            printNodePropMet(device, targetFile, usedDirectory, True)
        elif neededInfo == NodeInfoFunctions.MISSING_MANUAL:
            printIncorrectManuals(device, targetFile, usedDirectory, True)
        else:
            print("Unkown info requested, please use  the members of NodeInfoFunctions class.")
    else:
        #list is not empty, recursive call for all children
        hierarchyDebth += 1
        isFolderPropertyPrintingNeeded = True
        for actualRootChild in actualChilden:
            
            if actualRootChild == 'DATABASE':
                continue
            
            if isFolderPropertyPrintingNeeded:
                if neededInfo == NodeInfoFunctions.HIERARCHY:
                    printNodePropMet(device, targetFile, usedDirectory, False)
                elif neededInfo == NodeInfoFunctions.MISSING_MANUAL:
                    printIncorrectManuals(device, targetFile, usedDirectory, False)
                else:
                    print("Unkown info requested, please use  the members of NodeInfoFunctions class.")
                isFolderPropertyPrintingNeeded = False
            if neededInfo == NodeInfoFunctions.HIERARCHY:
#                print('\t'*hierarchyDebth + '/' + actualRootChild)
                targetFile.write('\t'*hierarchyDebth + '/' + actualRootChild + '\n')
            printNodeInfo(device, targetFile, usedDirectory + actualRootChild + '/', neededInfo)
        hierarchyDebth -= 1
    return