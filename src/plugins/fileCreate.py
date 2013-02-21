import os
from xml.dom.minidom import parse, parseString
import yaml 

def registerCallbacks(reg):
    matchEvent = {'Shotgun_Task_Change': ['sg_status_list']}
    reg.registerCallback('shotgunEventDaemon', 'e9f5a6858b086219257a432bc7e0a4b304d64ab4', makeFile, matchEvent, None)
    

def makeFile(sg,logger,event,args):
    filters = [ 
        ['sg_status_list', 'is', 'cmpt'], 
        {
            'filter_operator': 'all',
            'filters': [ 
                ['project', 'is', {'type':'Project', 'id': event['project']['id']} ]
            ] 
        }
    ]    
    changed_task = sg.find('Shot', filters)
    newValue1 = event['meta']['new_value']
    if newValue1 == 'cmpt':
        print event
        file_name = 'testEvent.yml'
        temp_path = 'Z:/scripts/' + file_name
        stream = file(temp_path, 'w')
        yaml.dump(event, stream)
        stream.close()