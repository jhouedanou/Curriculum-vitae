from .educarriere import Educarriere
from .novojob import Novojob
from .remotive import Remotive

# Pour ajouter un site : crée un fichier sur le modèle de novojob.py
# puis ajoute sa classe ici et une entrée dans config.yaml → sources.
SOURCES = {cls.nom: cls for cls in (Novojob, Educarriere, Remotive)}
