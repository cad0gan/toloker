import os


def notify(title: str = 'toloker', subtitle: str = '', message: str = ''):
    if not message:
        raise AttributeError
    title = f'-title "{title}"'
    subtitle = f'-subtitle "{subtitle}"'
    message = f'-message "{message}"'
    os.system(f'terminal-notifier {title} {subtitle} {message} -sound default')
