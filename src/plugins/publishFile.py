import os
import fnmatch
import shutil

def registerCallbacks(reg):    
    #version
    matchEvents = {'Shotgun_Task_Change': ['sg_status_list']}
    
    reg.registerCallback('shotgunEventDaemon', 'e9f5a6858b086219257a432bc7e0a4b304d64ab4', publishUpdate, matchEvents, None)

def getUnpublishedFiles(work_path,publish_path,exclusions=None):
    
    #getting work files
    work_files=[ f for f in os.listdir(work_path) if os.path.isfile(os.path.join(work_path,f)) ]
    
    #getting publish files
    publish_files=[ f for f in os.listdir(publish_path) if os.path.isfile(os.path.join(publish_path,f)) ]
    
    #getting unpublished files
    unpublished_files=[]
    for f in work_files:
        
        if f not in publish_files:
            
            unpublished_files.append(f)
    
    #checking exclusions
    if exclusions:
        for excl in exclusions:
            
            if '*' in excl:
                for f in fnmatch.filter(unpublished_files, excl):
                    del(unpublished_files[unpublished_files.index(f)])
            
            if excl in unpublished_files:
                del(unpublished_files[unpublished_files.index(excl)])
    
    return unpublished_files

def publishUpdate(sg, logger, event, args):
    
    try:
        #getting task info
        filters = [['id','is',event['entity']['id']]]
        fields=['entity','step','project']
        task=sg.find_one('Task',filters,fields)
        
        #excluding all tasks except comp and light
        if task['step']['name'] not in ['Comp','Light']:
            return
        
        #excluding all statuses except 'cmpt'
        if event['meta']['new_value']!='cmpt':
            return
        
        #getting shot info
        filters = [['id','is',task['entity']['id']]]
        fields=['code','sg_scene']
        shot=sg.find_one('Shot',filters,fields)
        
        #generating local paths
        work_path='M:/00719_grandpa/episodes/%s/%s/%s/work' % (shot['sg_scene']['name'],shot['code'],task['step']['name'])
        publish_path='M:/00719_grandpa/episodes/%s/%s/%s/publish' % (shot['sg_scene']['name'],shot['code'],task['step']['name'])
        
        #getting unpublishes files
        exclusions=['*.mel','SHOTGUN_SAVE_AS_PLEASE.ma','*.nk~']
        unpublished_files=getUnpublishedFiles(work_path, publish_path,exclusions=exclusions)
        
        if unpublished_files:
            #copying unpublished files
            nextVersion=0
            latestVersionFile=None
            for f in unpublished_files:
                
                shutil.copy(os.path.join(work_path,f),publish_path)
                
                #checking newest version number
                version=int(f.split('.')[-2][1:])
                if nextVersion<version:
                    nextVersion=version
                    latestVersionFile=f
                
                #deciding what type the file is
                fileName, fileExtension = os.path.splitext(f)
                fileType=None
                
                if fileExtension=='.nk':
                    fileType={'type': 'PublishedFileType', 'id': 10, 'name': 'Nuke Script'}
                elif fileExtension=='.ma':
                    fileType={'type': 'PublishedFileType', 'id': 1, 'name': 'Maya Scene'}
                
                #creating shotgun entry
                data = {
                    "code": f,
                    "description": 'ShotgunDaemon created publish file.',
                    "name": fileName,
                    "project": task['project'],
                    "entity": shot,
                    "task": task,
                    'path': {'local_path': os.path.join(publish_path,f).replace('\\',r'\\').replace('/',r'\\')},
                    "version_number": version,
                    'published_file_type':fileType}
                
                sg.create("PublishedFile", data)
            
            #creating new version
            nextVersion+=1
            
            fileSplit=latestVersionFile.split('.')
            fileSplit[-2]='v%03d' % nextVersion
            
            nextVersionFile='.'.join(fileSplit)
            
            shutil.copy(os.path.join(work_path,latestVersionFile),os.path.join(work_path,nextVersionFile))
        
        
        logger.info('Published files for %s/%s:%s' % (shot['code'],task['step']['name'],str(unpublished_files)))
    except:
        logger.info("Event #%s failed:\n%s" % (event['id'],event))