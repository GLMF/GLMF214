from updater.Updater import Updater
from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve
import abc
import os
import shutil



@Updater.register
class PythonUpdater(Updater):

    def _getInfos(self):
        ''' Get version, filename and url to download '''
        try:
            page = urlopen(self._url)
            soup = BeautifulSoup(page, 'html.parser')
            link = soup.find('a', {'class': 'button'})
            self._data['version'] = link.text.strip()[16:]
            self._data['filename'] = 'Python-{}.tgz'.format(self._data['version'])
            self._data['url'] = 'https://www.python.org/ftp/python/{}/{}'.format(self._data['version'], self._data['filename'])
        except:
            self._log.write('Error while parsing ' + self._url + '\n')
            self._log.write('Please, verify if the code page has changed !\n')
            self._log.close()
            exit(3)


    def _compile(self):
        ''' Compilation instructions '''
        urlretrieve(self._data['url'], '{}/{}'.format(PythonUpdater.TEMP_DIR, self._data['filename']))
        os.chdir(PythonUpdater.TEMP_DIR)
        os.system('tar -xvf {}'.format(self._data['filename']))
        os.chdir('Python-{}'.format(self._data['version']))
        self._execute('./configure --enable-optimizations --enable-shared')
        self._execute('make')
        self._execute('sudo make altinstall')
        os.chdir(PythonUpdater.TEMP_DIR)
        shutil.rmtree('Python-{}'.format(self._data['version']))
        os.remove(self._data['filename'])
