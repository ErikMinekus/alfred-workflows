# encoding: utf-8

import eiscp
import sys
from workflow import Workflow3 as Workflow, MATCH_SUBSTRING
from workflow.background import run_in_background, is_running


def getItems(query, data):
    args   = query.split(' ')
    action = args[0]
    value  = args[1] if len(args) > 1 else ''

    if not data:
        return [{
            'title': 'Connecting...',
            'autocomplete': '',
            'valid': False,
        }, {
            'title': 'Discover receiver',
            'arg': 'discover',
            'valid': True,
        }]

    if not data['isPowerOn']:
        return [{
            'title': 'Turn receiver on',
            'subtitle': data['modelName'],
            'arg': 'on',
            'valid': True,
        }]

    if action == 'net':
        if data['source'] != 'NET':
            return [{
                'title': 'Set source to NET',
                'arg': 'source net',
                'valid': True,
            }]

        isPlaying = (data['status'] == 'Playing')

        return [{
            'title': data['title'],
            'subtitle': getTrackSubtitle(data['artist'], data['album']),
            'autocomplete': 'net ',
            'valid': False,
        }, {
            'title': 'Pause' if isPlaying else 'Play',
            'arg': 'net pause' if isPlaying else 'net play',
            'valid': True,
        }, {
            'title': 'Next track',
            'arg': 'net next-track',
            'valid': True,
        }, {
            'title': 'Previous track',
            'arg': 'net previous-track',
            'valid': True,
        }]

    if action == 'source':
        return [{
            'title': 'BD/DVD',
            'arg': 'source bd',
            'valid': True,
        }, {
            'title': 'CBL/SAT',
            'arg': 'source cbl',
            'valid': True,
        }, {
            'title': 'GAME',
            'arg': 'source game',
            'valid': True,
        }, {
            'title': 'NET',
            'arg': 'source net',
            'valid': True,
        }, {
            'title': 'USB',
            'arg': 'source usb',
            'valid': True,
        }]

    if action == 'volume':
        if value.isdigit():
            return [{
                'title': 'Set volume to %d' % int(value),
                'arg': 'volume %d' % int(value),
                'valid': True,
            }]

        return [{
            'title': 'Set volume to ...',
            'autocomplete': 'volume ',
            'valid': False,
        }, {
            'title': 'Unmute' if data['isMuting'] else 'Mute',
            'arg': 'volume mute',
            'valid': True,
        }]

    items = [{
        'title': 'Set source',
        'subtitle': data['source'],
        'autocomplete': 'source ',
        'valid': False,
    }, {
        'title': 'Set volume',
        'subtitle': str(data['volume']),
        'autocomplete': 'volume ',
        'valid': False,
    }, {
        'title': 'Turn receiver off',
        'subtitle': data['modelName'],
        'arg': 'off',
        'valid': True,
    }]

    if data['source'] == 'NET':
        items.insert(0, {
            'title': data['title'],
            'subtitle': getTrackSubtitle(data['artist'], data['album']),
            'autocomplete': 'net ',
            'valid': False,
        })

    return items


def getItemFilterKey(item):
    return item['arg'] if item['valid'] else item['autocomplete']


def getTrackSubtitle(artist, album):
    return artist if not album else u' — '.join([artist, album])


def main(workflow):
    query = workflow.args[0]
    data  = workflow.cached_data('receiver_data', max_age=0)
    items = getItems(query, data)

    if query:
        items = workflow.filter(query, items,
            key=getItemFilterKey,
            match_on=MATCH_SUBSTRING)

    if items:
        for item in items:
            workflow.add_item(**item)
    else:
        workflow.add_item('No action found for "%s"' % query)

    workflow.rerun = 1.0
    workflow.send_feedback()

    if not is_running('onkyo_update'):
        run_in_background('onkyo_update', ['/usr/bin/python', workflow.workflowfile('update.py')])


if __name__ == '__main__':
    workflow = Workflow()
    sys.exit(workflow.run(main))
