# encoding: utf-8

from discover import discoverReceiver
import eiscp
from workflow import Workflow3 as Workflow


def getSource(value):
    return {
        '01': 'CBL/SAT',
        '02': 'GAME',
        '03': 'AUX',
        '05': 'PC',
        '10': 'BD/DVD',
        '23': 'TV/CD',
        '24': 'FM',
        '25': 'AM',
        '29': 'USB',
        '2B': 'NET',
    }.get(value, 'Unknown')


def getStatus(value):
    return {
        'P': 'Playing',
        'p': 'Paused',
        'S': 'Stopped',
        'F': 'Fast Forward',
        'R': 'Rewind',
    }.get(value[0], 'Unknown')


def main(workflow):
    if 'receiver_host' not in workflow.settings:
        foundReceiver = discoverReceiver()
        if not foundReceiver:
            return

        workflow.settings['receiver_host'] = foundReceiver.host

    receiver = eiscp.eISCP(workflow.settings['receiver_host'])
    data     = {
        'modelName': receiver.model_name,
        'isPowerOn': (receiver.raw('PWRQSTN') == 'PWR01'),
        'isMuting':  (receiver.raw('AMTQSTN') == 'AMT01'),
        'volume':    int(receiver.raw('MVLQSTN')[3:], 16),
        'source':    getSource(receiver.raw('SLIQSTN')[3:]),
    }

    if data['isPowerOn'] and data['source'] == 'NET':
        data['title']  = receiver.raw('NTIQSTN')[3:]
        data['artist'] = receiver.raw('NATQSTN')[3:]
        data['album']  = receiver.raw('NALQSTN')[3:]
        data['time']   = receiver.raw('NTMQSTN')[3:]
        data['status'] = getStatus(receiver.raw('NSTQSTN')[3:])

    workflow.cache_data('receiver_data', data)
    receiver.disconnect()


if __name__ == '__main__':
    workflow = Workflow()
    workflow.run(main)
