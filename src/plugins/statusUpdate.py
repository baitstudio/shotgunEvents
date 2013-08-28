def registerCallbacks(reg):    
    #version
    matchEvents = {'Shotgun_Version_Change': ['sg_status_list']}
    
    reg.registerCallback('shotgunEventDaemon', 'e9f5a6858b086219257a432bc7e0a4b304d64ab4', versionUpdate, matchEvents, None)
    
    #task
    matchEvents = {'Shotgun_Task_Change': ['sg_status_list']}
    
    reg.registerCallback('shotgunEventDaemon', 'e9f5a6858b086219257a432bc7e0a4b304d64ab4', taskUpdate, matchEvents, None)

def versionUpdate(sg, logger, event, args):
    
    #getting version
    filters = [['id','is',event['entity']['id']]]
    fields=['entity','sg_task']
    version=sg.find_one('Version',filters,fields)
    
    #getting shot
    filters = [['id','is',version['entity']['id']]]
    fields=['code']
    shot=sg.find_one('Shot',filters,fields)
    
    #setting status
    newStatus=event['meta']['new_value']
    
    #task updating to cmpt when version is on rev
    if newStatus=='rev':
        #getting task
        filters = [['id','is',version['sg_task']['id']]]
        fields=['content']
        task=sg.find_one('Task',filters,fields)
        
        sg.update("Task",task['id'], data={'sg_status_list' : 'cmpt'})
        logger.info("Set Task #%s/%s to '%s'" % (task['id'],task['content'],'cmpt'))
    
    #if its a shot and not an asset
    if shot:
        #changing shot status
        sg.update("Shot",shot['id'], data={'sg_status_list' : newStatus})
        logger.info("Set Shot #%s/%s to '%s'" % (shot['id'],shot['code'],newStatus))

def taskUpdate(sg, logger, event, args):
    
    #getting task
    filters = [['id','is',event['entity']['id']]]
    fields=['entity','step']
    task=sg.find_one('Task',filters,fields)
    
    #exception for light task when put to cmpt
    if task['step']['name'] == 'Light' and event['meta']['new_value'] == 'cmpt':
        return
    
    #getting shot
    filters = [['id','is',task['entity']['id']]]
    fields=['code']
    shot=sg.find_one('Shot',filters,fields)
    
    #setting status
    newStatus=event['meta']['new_value']
    
    #if its a shot and not an asset
    if shot:
        #changing shot status
        sg.update("Shot",shot['id'], data={'sg_status_list' : newStatus})
        logger.info("Set Shot #%s/%s to '%s'" % (shot['id'],shot['code'],newStatus))