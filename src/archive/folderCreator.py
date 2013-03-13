'''

possibly have a storage space to point projects to? > when creating new projects in shotgun, you wont need to set the link
embed xml files with data about where to put stuff
tell user about fatal warnings like not linking a project through shotgun notes?

'''

import os
from xml.dom.minidom import parse, parseString

def registerCallbacks(reg):
    projectEvent = {'Shotgun_Project_New': ['*']}
    reg.registerCallback('shotgunEventDeamon', 'e9f5a6858b086219257a432bc7e0a4b304d64ab4', projectFolder, projectEvent, None)
    
    sceneEvent = {'Shotgun_Scene_New': ['*']}
    reg.registerCallback('shotgunEventDeamon', 'e9f5a6858b086219257a432bc7e0a4b304d64ab4', episodeFolder, sceneEvent, None)

    seqEvent = {'Shotgun_Sequence_New': ['*']}
    reg.registerCallback('shotgunEventDeamon', 'e9f5a6858b086219257a432bc7e0a4b304d64ab4', sequenceFolder, seqEvent, None)

    shotEvent = {'Shotgun_Shot_New': ['*']}
    reg.registerCallback('shotgunEventDeamon', 'e9f5a6858b086219257a432bc7e0a4b304d64ab4', shotFolder, shotEvent, None)

#recursive function to create directories
def createSubDirs(childNodes,rootDir):
    for i in childNodes:
        if i.attributes!=None:
            if i.tagName=='dir':
                if os.path.exists(rootDir+'/'+i.getAttribute('name'))!=True:
                    os.makedirs(rootDir+'/'+i.getAttribute('name'))
                if len(i.childNodes)>0:
                    newDir=rootDir+'/'+i.getAttribute('name')
                    createSubDirs(i.childNodes,newDir)

def projectFolder(sg,logger,event,args):
    #scene data
    filters = [['id', 'is', event['entity']['id']]]
    fields = ['code','sg_xml_link','sg_link']
    project = sg.find_one('Project', filters, fields)

    #fail safe for project link
    if project['sg_link']==None:
        logger.warning('Project folders FAILED! No Project link found.\nName:%s' % event['entity']['name'])
    else:
        #fail safe for project xml link
        if project['sg_xml_link']==None:
            logger.warning('Project folders FAILED! No xml link exists\nName:%s' % event['entity']['name'])

            #project directory
            projectDir=project['sg_link']['local_path_windows']
            
            pluginsDir=os.path.dirname(__file__)

            #reading xml file
            f=open((pluginsDir+'/xml/project.xml'),'r')
            
            #getting data from file
            fData=f.read()
            
            #convert string to document
            doc=parseString(fData)
            root=doc.childNodes[0]

            createSubDirs(root.childNodes,projectDir)
        else:       
            #project directory
            projectDir=project['sg_link']['local_path_windows']
            
            #create folder
            if os.path.exists(projectDir+'/episodes/'+event['entity']['name'])!=True:
                os.makedirs(projectDir+'/episodes/'+event['entity']['name'])

                #logging
                logger.info("New Episode folder created. \nName:%s\nDirectory:%s" % (event['entity']['name'],(projectDir+'/episodes/'+event['entity']['name'])))
            else:
                #logging
                logger.warning("Episode folder exists. \nName:%s\nDirectory:%s" % (event['entity']['name'],(projectDir+'/episodes/'+event['entity']['name'])))

            #update link field
            data={'name':event['entity']['name'],'url':('file://'+(projectDir+'/episodes/'+event['entity']['name'])),'local_path':(projectDir+'/episodes/'+event['entity']['name'])}
            sg.update('Scene',event['entity']['id'],{'sg_link':data})
        
def episodeFolder(sg,logger,event,args):
    #scene data
    filters = [['id', 'is', event['entity']['id']]]
    fields = ['code','project','sg_xml_link']
    scene = sg.find_one('Scene', filters, fields)

    #project data
    filters = [['id', 'is', scene['project']['id']]]
    fields = ['sg_link']
    project = sg.find_one('Project', filters, fields)

    #fail safe for project link
    if project['sg_link']==None:
        logger.warning('New Episode folder FAILED! No Project link found.\nName:%s' % event['entity']['name'])
    else:
        #fail safe for project xml link
        if scene['sg_xml_link']==None:
            logger.warning('New Episode folder FAILED! No xml link exists\nName:%s' % event['entity']['name'])

            #project directory
            projectDir=project['sg_link']['local_path_windows']
            
            pluginsDir=os.path.dirname(__file__)

            #reading xml file
            f=open((pluginsDir+'/xml/episode.xml'),'r')
            
            #getting data from file
            fData=f.read()
            
            #convert string to document
            doc=parseString(fData)
            root=doc.childNodes[0]

            #create scene directory
            if os.path.exists(projectDir+'/episodes/'+event['entity']['name'])!=True:
                os.makedirs(projectDir+'/episodes/'+event['entity']['name'])

            createSubDirs(root.childNodes,(projectDir+'/episodes/'+event['entity']['name']))
        else:       
            #project directory
            projectDir=project['sg_link']['local_path_windows']
            
            #create folder
            if os.path.exists(projectDir+'/episodes/'+event['entity']['name'])!=True:
                os.makedirs(projectDir+'/episodes/'+event['entity']['name'])

                #logging
                logger.info("New Episode folder created. \nName:%s\nDirectory:%s" % (event['entity']['name'],(projectDir+'/episodes/'+event['entity']['name'])))
            else:
                #logging
                logger.warning("Episode folder exists. \nName:%s\nDirectory:%s" % (event['entity']['name'],(projectDir+'/episodes/'+event['entity']['name'])))

            #update link field
            data={'name':event['entity']['name'],'url':('file://'+(projectDir+'/episodes/'+event['entity']['name'])),'local_path':(projectDir+'/episodes/'+event['entity']['name'])}
            sg.update('Scene',event['entity']['id'],{'sg_link':data})

def sequenceFolder(sg,logger,event,args):
    #sequence data
    filters = [['id', 'is', event['entity']['id']]]
    fields = ['code','project','sg_episodes']
    seq = sg.find_one('Sequence', filters, fields)

    #project data
    filters = [['id', 'is', seq['project']['id']]]
    fields = ['sg_link']
    project = sg.find_one('Project', filters, fields)

    #fail safe for project link
    if project['sg_link']==None:
        logger.warning('New Sequence folder FAILED!\nName:%s' % event['entity']['name'])
    else:
        #project directory
        projectDir=project['sg_link']['local_path_windows']
        
        #create folder
        for epi in seq['sg_episodes']:
            if os.path.exists(projectDir+'/episodes/'+epi['name']+'/'+event['entity']['name'])!=True:
                os.makedirs(projectDir+'/episodes/'+epi['name']+'/'+event['entity']['name'])
                
                #logging
                logger.info("New Sequence folder created. \nName:%s\nDirectory:%s" % (event['entity']['name'],(projectDir+'/episodes/'+epi['name']+'/'+event['entity']['name'])))
            else:
                #logging
                logger.warning("Sequence folder exists. \nName:%s\nDirectory:%s" % (event['entity']['name'],(projectDir+'/episodes/'+epi['name']+'/'+event['entity']['name'])))
            
            #update link field
            data={'name':event['entity']['name'],'url':('file://'+(projectDir+'/episodes/'+epi['name']+'/'+event['entity']['name'])),'local_path':(projectDir+'/episodes/'+epi['name']+'/'+event['entity']['name'])}
            sg.update('Sequence',event['entity']['id'],{'sg_link':data})

def shotFolder(sg,logger,event,args):
    #shot data
    filters = [['id', 'is', event['entity']['id']]]
    fields = ['code','project','sg_scene','sg_sequence']
    shot = sg.find_one('Shot', filters, fields)

    #project data
    filters = [['id', 'is', event['project']['id']]]
    fields = ['sg_link']
    project = sg.find_one('Project', filters, fields)

    #fail safe for project link
    if project['sg_link']==None:
        logger.warning('New Shot folder FAILED!\nName:%s' % event['entity']['name'])
    else:
        #project directory
        projectDir=project['sg_link']['local_path_windows']
        shotDir=projectDir+'/episodes/'+shot['sg_scene']['name']+'/'+shot['sg_sequence']['name']+'/'+event['entity']['name']

        #create folder
        if os.path.exists(shotDir)!=True:
            os.makedirs(shotDir)

            #logging
            logger.info("New Episode folder created. \nName:%s\nDirectory:%s" % (event['entity']['name'],shotDir))
        else:
            #logging
            logger.warning("Episode folder exists. \nName:%s\nDirectory:%s" % (event['entity']['name'],shotDir))

        pluginsDir=os.path.dirname(__file__)

        #reading xml file
        f=open((pluginsDir+'/xml/shot.xml'),'r')
            
        #getting data from file
        fData=f.read()
            
        #convert string to document
        doc=parseString(fData)
        root=doc.childNodes[0]

        createSubDirs(root.childNodes,shotDir)

        #update link field
        data={'name':event['entity']['name'],'url':('file://'+shotDir),'local_path':shotDir}
        sg.update('Shot',event['entity']['id'],{'sg_link':data})
