# encoding: utf-8

from discover import discoverReceiver
import eiscp
import sys
from workflow import Workflow3 as Workflow
from workflow.notify import notify


def main(workflow):
    args   = workflow.args[0].split(' ')
    action = args[0]
    value  = args[1] if len(args) > 1 else ''

    if action == 'discover':
        foundReceiver = discoverReceiver()
        if foundReceiver:
            workflow.settings['receiver_host'] = foundReceiver.host
            notify('Onkyo Remote', 'Found %s at %s' % (foundReceiver.model_name, foundReceiver.host))
        return

    if 'receiver_host' not in workflow.settings:
        return

    receiver = eiscp.eISCP(workflow.settings['receiver_host'])

    if action in ['off', 'on']:
        receiver.command('power %s' % action)

    elif action == 'net':
        if value in ['pause', 'play']:
            receiver.command('network-usb %s' % value)
        elif value == 'next-track':
            receiver.command('network-usb trup')
        elif value == 'previous-track':
            receiver.command('network-usb trdn')

    elif action == 'source':
        receiver.command('source %s' % value)

    elif action == 'volume':
        if value.isdigit():
            receiver.command('volume %d' % int(value))
        elif value in ['down', 'up']:
            receiver.command('volume level-%s' % value)
        elif value == 'mute':
            receiver.command('audio-muting toggle')

    receiver.disconnect()


if __name__ == '__main__':
    workflow = Workflow()
    sys.exit(workflow.run(main))
