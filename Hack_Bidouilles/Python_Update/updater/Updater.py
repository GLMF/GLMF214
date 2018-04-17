import os
import abc



class Updater(abc.ABC):
    TEMP_DIR = '/tmp/'


    def __init__(self, name, url, mail):
        ''' Constructor '''
        self._name = name
        self._url = url
        self._data = {}
        self._logFilename = Updater.TEMP_DIR + 'log_' + self._name
        self._rootMail = mail
        try:
            self._log = open(self._logFilename, 'w')
        except:
            print('Unable to create ' + self._logFilename)
            exit(1)


    @abc.abstractmethod
    def _getInfos(self):
        ''' Get version, filename and url to download '''


    @abc.abstractmethod
    def _compile(self):
        ''' Compilation instructions '''


    def _isToUpdate(self):
        ''' Verify if the Web version is newer'''
        versionFile = os.path.dirname(os.path.realpath(__file__)) + '/../data/' + self._name + '_update/' + self._name + '_version'
        try:
            with open(versionFile, 'r') as fic:
                currentVersion = fic.read().strip()
        except:
            self._log.write('Unable to open ' + versionFile)
            self._log.close()
            exit(2)

        valueNewVersion = self._data['version'].split('.')
        for pos, valueCurrentVersion in enumerate(currentVersion.split('.')):
            if valueNewVersion[pos] > valueCurrentVersion:
                try:
                    with open(versionFile, 'w') as fic:
                        fic.write(self._data['version'])
                except:
                    self._log.write('Unable to write new version in ' + versionFile)
                    self._log.close()
                    exit(3)
                return True
            
        return False


    def _mail(self, message=None):
        ''' Send log or message if defined '''
        with open(self._logFilename, 'r') as fic:
            log = fic.read()
        content = 'To:{}\nSubject:[Updater] Mise à jour automatique de {}\n\n'.format(self._rootMail, self._name)
        if message is None:
            content += log
        else:
            content += message
        with open(Updater.TEMP_DIR + 'mail.txt', 'w') as fic:
            fic.write(content)
        os.system('msmtp -t < /tmp/mail.txt')
        os.remove('/tmp/mail.txt')


    def _execute(self, cmd):
        ''' Execute command '''
        self._log.close()
        os.system('echo ">>> EXECUTE : {}" >> {}'.format(cmd, self._logFilename))
        errorCode = os.system('{} >> {}'.format(cmd, self._logFilename))
        if errorCode != 0:
            self._mail(self._log)
            os.system('notify-send -i /usr/share/icons/mate/32x32/emblems/dialog-warning.png -u critical -t 1500 "Updater" "Erreur lors de la mise à jour.<br />Un mail a été envoyé à l\'administrateur."'.format(self._name, self._data['version']))
            exit(errorCode)


    def start(self):
        ''' Start update process '''
        data = self._getInfos()
        if self._isToUpdate():
            os.system('notify-send -i /usr/share/icons/mate/32x32/emblems/emblem-default.png -t 1500 "Updater" "Mise à jour de {} en version {} en cours"'.format(self._name, self._data['version']))
            self._compile()
            os.system('notify-send -i /usr/share/icons/mate/32x32/emblems/emblem-default.png -t 1500 "Updater" "Mise à jour de {} en version {} effectuée!"'.format(self._name, self._data['version']))
            self._mail('Mise à jour de {} en version {} effectuée!'.format(self._name, self._data['version']))
