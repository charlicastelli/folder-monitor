import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import shutil
import pymsgbox

################################################################################
# Titulo    : Folder Monitor.                                                  #
# Versao    : 1.0                                                              #
# Data      : 25/06/2024                                                       #
# Tested on : Windows10/11                                                     #
# created by: Charli Castelli.                                                 #
# -----------------------------------------------------------------------------#
# Descrição:                                                                   #
#   Essa ferramenta monitora pastas e mostra um alerta informando que          #
#   algo suspeito foi criado.                                                  #
#   No alerta permite interromper a criação ou permitir                        #
# -----------------------------------------------------------------------------#
# Nota da Versão:                                                              #
#   Na variavel "folders_to_monitor" deve informar qual pasta deseja monitorar.#
#   Podendo escolher apenas uma ou mais pastas.                                #
################################################################################



class MyHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_event_time = None

    def should_ignore_event(self, event_time):
        if self.last_event_time is not None and (event_time - self.last_event_time) < 3:
            return True
        self.last_event_time = event_time
        return False

    def on_created(self, event):
        current_time = time.time()
        if self.should_ignore_event(current_time):
            return
        
        if event.is_directory:
            return  # Ignora pastas criadas
        
         # Verifica se o arquivo tem uma das extensões desejadas
        allowed_extensions = (".exe", ".ps1", ".py", ".bat", ".cmd", ".msi", ".dll", ".vbs")
        if event.src_path.lower().endswith(allowed_extensions):
        
            # Exibe a caixa de mensagem diretamente
            result = pymsgbox.confirm(text=f"Foi detectada uma nova criação em {event.src_path}\n\n\nDeseja permitir a criação?", title="Alerta de Segurança")
            if result == "OK":
                print("YES")
            else:
                print("Criação interrompida.")
                if os.path.isfile(event.src_path):
                    try:
                        os.remove(event.src_path)  # Remove o arquivo
                    except Exception as e:
                        print(f"Erro ao remover o arquivo: {e}")  
                else:                                                  
                    try:
                        shutil.rmtree(event.src_path)  # Remove a pasta e seu conteúdo
                    except Exception as e:
                        print(f"Erro ao remover a pasta: {e}")

# Caminho das pastas que deseja monitorar (Substituir pelos caminhos reais)
folders_to_monitor = ["C:\\Users\\local\\Documents", "C:\\Windows\\System32", "C:\\Windows\\SysWOW64", "C:\\Users\\local\\AppData\\Local\\Temp"]
observers = []

for folder in folders_to_monitor:
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, folder, recursive=True)
    observer.start()
    observers.append(observer)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    for observer in observers:
        observer.stop()
    for observer in observers:
        observer.join()