def registerCallbacks(reg):
    matchEvents = {
        'Shotgun_Task_Change': ['sg_status_list'],
    }
    
    reg.registerCallback('shotgunEventDaemon', 'e9f5a6858b086219257a432bc7e0a4b304d64ab4', assigmentUpdate, matchEvents, None)


def assigmentUpdate(sg, logger, event, args):
    
    try:
        # we only care about Tasks that have been finalled
        if 'new_value' not in event['meta'] or event['meta']['new_value'] != 'cmpt':
            return
        
        #only care about tracking tasks
        filters = [['id','is',event['entity']['id']]]
        fields=['downstream_tasks','step','entity']
        task=sg.find_one('Task',filters,fields)
        
        #excluding all tasks except track
        if task['step']['name'] not in ['Track']:
            return
        
        #getting shot info for logger
        filters = [['id','is',task['entity']['id']]]
        fields=['code']
        shot=sg.find_one('Shot',filters,fields)
        
        #assigning animation
        if len(task['downstream_tasks'])!=0:
            
            for ds_task in task['downstream_tasks']:
                
                filters = [['id','is',ds_task['id']]]
                fields=['step','task_assignees','content']
                tsk=sg.find_one('Task',filters,fields)
                
                if tsk['step']['name']=='Anim':
                    
                    if len(tsk['task_assignees'])==0:
                        
                        animGroup=[{'type': 'Group', 'id': 5, 'name': 'Animation'}]
                        sg.update("Task",tsk['id'], data={'task_assignees' : animGroup})
                        
                        logger.info('Assigned task to Animation: %s/%s' % (shot['code'],tsk['content']))
                        
    except Exception, e:
        logger.info("Event #%s failed:\n%s\nerror:\n%s" % (event['id'],event,e))