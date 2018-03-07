# encoding: utf-8

import eiscp
import sys
from workflow import Workflow3 as Workflow, MATCH_SUBSTRING
from workflow.background import run_in_background, is_running


def getItems(query, data):
    args   = query.split(' ')
    action = args[0]
    value  = args[1] if len(args) > 1 else ''

    if action == 'discover':
        return [{
            'title': 'Discover receiver',
            'subtitle': '',
            'arg': 'discover',
            'autocomplete': '',
            'valid': True,
        }]

    if not data:
        return [{
            'title': 'Connecting...',
            'subtitle': '',
            'arg': '',
            'autocomplete': '',
            'valid': False,
        }]

    if not data['isPowerOn']:
        return [{
            'title': 'Turn receiver on',
            'subtitle': data['modelName'],
            'arg': 'on',
            'autocomplete': '',
            'valid': True,
        }]

    if action == 'net':
        if data['source'] != 'NET':
            return [{
                'title': 'Set source to NET',
                'subtitle': '',
                'arg': 'source net',
                'autocomplete': '',
                'valid': True,
            }]

        isPlaying = (data['status'] == 'Playing')

        return [{
            'title': data['title'],
            'subtitle': getTrackSubtitle(data['artist'], data['album']),
            'arg': '',
            'autocomplete': 'net ',
            'valid': False,
        }, {
            'title': 'Pause' if isPlaying else 'Play',
            'subtitle': '',
            'arg': 'net pause' if isPlaying else 'net play',
            'autocomplete': '',
            'valid': True,
        }, {
            'title': 'Next track',
            'subtitle': '',
            'arg': 'net next-track',
            'autocomplete': '',
            'valid': True,
        }, {
            'title': 'Previous track',
            'subtitle': '',
            'arg': 'net previous-track',
            'autocomplete': '',
            'valid': True,
        }]

    if action == 'source':
        return [{
            'title': 'BD/DVD',
            'subtitle': '',
            'arg': 'source bd',
            'autocomplete': '',
            'valid': True,
        }, {
            'title': 'CBL/SAT',
            'subtitle': '',
            'arg': 'source cbl',
            'autocomplete': '',
            'valid': True,
        }, {
            'title': 'GAME',
            'subtitle': '',
            'arg': 'source game',
            'autocomplete': '',
            'valid': True,
        }, {
            'title': 'NET',
            'subtitle': '',
            'arg': 'source net',
            'autocomplete': '',
            'valid': True,
        }, {
            'title': 'USB',
            'subtitle': '',
            'arg': 'source usb',
            'autocomplete': '',
            'valid': True,
        }]

    if action == 'volume':
        if value.isdigit():
            return [{
                'title': 'Set volume to %d' % int(value),
                'subtitle': '',
                'arg': 'volume %d' % int(value),
                'autocomplete': '',
                'valid': True,
            }]

        return [{
            'title': 'Set volume to ...',
            'subtitle': '',
            'arg': '',
            'autocomplete': 'volume ',
            'valid': False,
        }, {
            'title': 'Unmute' if data['isMuting'] else 'Mute',
            'subtitle': '',
            'arg': 'volume mute',
            'autocomplete': '',
            'valid': True,
        }]

    items = [{
        'title': 'Set source',
        'subtitle': data['source'],
        'arg': '',
        'autocomplete': 'source ',
        'valid': False,
    }, {
        'title': 'Set volume',
        'subtitle': str(data['volume']),
        'arg': '',
        'autocomplete': 'volume ',
        'valid': False,
    }, {
        'title': 'Turn receiver off',
        'subtitle': data['modelName'],
        'arg': 'off',
        'autocomplete': '',
        'valid': True,
    }]

    if data['source'] == 'NET':
        items.insert(0, {
            'title': data['title'],
            'subtitle': getTrackSubtitle(data['artist'], data['album']),
            'arg': '',
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
