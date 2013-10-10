def registerCallbacks(reg):    
    #version
    matchEvents = {'Shotgun_Version_Change': ['sg_status_list']}
    
    reg.registerCallback('shotgunEventDaemon', 'e9f5a6858b086219257a432bc7e0a4b304d64ab4', versionUpdate, matchEvents, None)
    
    #task
    matchEvents = {'Shotgun_Task_Change': ['sg_status_list']}
    
    reg.registerCallback('shotgunEventDaemon', 'e9f5a6858b086219257a432bc7e0a4b304d64ab4', taskUpdate, matchEvents, None)

def versionUpdate(sg, logger, event, args):
    
    #getting version
    try:
        filters = [['id','is',event['entity']['id']]]
        fields=['entity','sg_task']
        version=sg.find_one('Version',filters,fields)
    except:
        logger.info("Event #%s failed:\n%s" % (event['id'],event))
        
        return
    
    #if its a shot and not an asset
    try:
        if version['entity']['type']=='Shot':
        
            #getting shot
            filters = [['id','is',version['entity']['id']]]
            fields=['code']
            shot=sg.find_one('Shot',filters,fields)
            
            #setting status
            newStatus=event['meta']['new_value']
            
            #getting task
            filters = [['id','is',version['sg_task']['id']]]
            fields=['content','step']
            task=sg.find_one('Task',filters,fields)
            
            #task updating to rned when version is on rned
            if newStatus=='rned':
                
                #if its a Comp task, set task to complete and version to rev
                if task['step']['name'] == 'Comp':
                    sg.update("Task",task['id'], data={'sg_status_list' : 'cmpt'})
                    logger.info("Set Task #%s/%s to '%s'" % (task['id'],task['content'],'cmpt'))
                            
                    sg.update("Version",version['id'], data={'sg_status_list' : 'rev'})
                    logger.info("Set Version #%s/%s to '%s'" % (version['id'],version['code'],'rev'))
                #everything else and task gets set to rned
                else:
                    sg.update("Task",task['id'], data={'sg_status_list' : 'rned'})
                    logger.info("Set Task #%s/%s to '%s'" % (task['id'],task['content'],'rned'))
            
            #updating task if version are requeud on farm
            if newStatus=='rnd' or newStatus=='qrnd':
                
                sg.update("Task",task['id'], data={'sg_status_list' : 'farm'})
                logger.info("Set Task #%s/%s to '%s'" % (task['id'],task['content'],'farm'))
                
            #changing shot status
            sg.update("Shot",shot['id'], data={'sg_status_list' : newStatus})
            logger.info("Set Shot #%s/%s to '%s'" % (shot['id'],shot['code'],newStatus))
    except:
        logger.info("Version #%s/%s failed!" % (version['id'],version['entity']['name']))

def taskUpdate(sg, logger, event, args):
    
    #getting task
    try:
        filters = [['id','is',event['entity']['id']]]
        fields=['entity','step']
        task=sg.find_one('Task',filters,fields)
    except:
        logger.info("Event #%s failed:\n%s" % (event['id'],event))
        
        return
    
    #setting status
    newStatus=event['meta']['new_value']
    
    #exception for rendered status update
    if newStatus=='rned':
        return
    
    #if its a shot and not an asset
    try:
        if task['entity']['type']=='Shot':
            
            #getting shot
            filters = [['id','is',task['entity']['id']]]
            fields=['code']
            shot=sg.find_one('Shot',filters,fields)
            
            #artist reviewing the renders, and puts it on complete
            #only light step is affected
            if task['step']['name'] == 'Light' and newStatus=='cmpt':
                
                filters = [['entity','is',shot]]
                fields=['code','sg_status_list']
                versions=sg.find('Version',filters,fields)
                
                for version in versions:
                    
                    if version['sg_status_list']=='rned':
                        
                        sg.update("Version",version['id'], data={'sg_status_list' : 'rev'})
                        logger.info("Set Version #%s/%s to '%s'" % (version['id'],version['code'],'rev'))
                
                return
            
            #changing shot status
            sg.update("Shot",shot['id'], data={'sg_status_list' : newStatus})
            logger.info("Set Shot #%s/%s to '%s'" % (shot['id'],shot['code'],newStatus))
    except:
        logger.info("Task #%s/%s failed!" % (task['id'],task['content']))