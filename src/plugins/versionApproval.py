def registerCallbacks(reg):
    matchEvents = {
        'Shotgun_Version_Change': ['sg_status_list'],
    }
    
    reg.registerCallback('shotgunEventDaemon', 'e9f5a6858b086219257a432bc7e0a4b304d64ab4', versionApproveTasks, matchEvents, None)

def versionApproveTasks(sg, logger, event, args):
    
    # we only care about Tasks that have been approved
    if 'new_value' not in event['meta'] or event['meta']['new_value'] != 'apr':
        return
    
    #getting task associated with version
    filters = [['id','is',event['entity']['id']]]
    fields=['sg_task']
    version=sg.find_one('Version',filters,fields)
    
    filters = [['id','is',version['sg_task']['id']]]
    task=sg.find_one('Task',filters,None)
    
    #setting task to final
    sg.update("Task",task['id'], data={'sg_status_list' : 'fin'})
    logger.info("Set Task #%s to 'fin'", task['id'])