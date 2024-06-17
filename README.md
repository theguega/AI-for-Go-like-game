# IA02 - Projet - P24

Ce projet met en place plusieurs stratégies d'Intelligence Artificielle permettant de jouer aux jeux Dodo et Gopher.  

<div id="image-table">
    <table>
	    <tr>
    	    <td style="padding:10px">
        	    <img src="doc/dodo.jpg" width="100%"/>
      	    </td>
            <td style="padding:10px">
            	<img src="doc/gopher.jpg" width="100%"/>
            </td>
        </tr>
    </table>
</div>

# Mise en place des outils de jeu

## Configuration du projet

Pour l'utilisation du projet, nous recommandons l'utilisation d'un environnement virtuel, ici en utilisant anaconda par exemple :  

```bash
git clone https://gitlab.utc.fr/guegathe/ia02_project.git
cd ia02_project
conda create --name ia02 python=3.12 
conda activate ia02
pip install -r requirements.txt
```

## Utilisation du serveur

Le serveur s'exécute en ligne de commande (terminal sous Linux et macOS, PowerShell sous Windows) 

1. Copier le bon exécutable dans votre répertoire de travail. On suppose par la suite que l'exécutable s'appelle `/server/gndserver`
2. Ajouter les droits en exécution (si besoin sous Linux et MacOS) : `chmod a+x /server/gndserver`
3. Vérifier le fonctionnement et voir les options : `./server/gndserver`

```bash
# toutes les options
./server/gndserver -h
```

```bash
# lancer un serveur de dodo contre un joueur random
./server/gndserver -game dodo -random 
```

```bash
# lancer un serveur de gopher contre un joueur random
./server/gndserver -game gopher -random
```

```bash
# lancer un serveur de gopher contre un joueur random gopher qui sera la joueur bleu
./server/gndserver -game gopher -rcolor blue -random
```

```bash
# tout réinitialiser
rm config.json server.json
```

## Utilisation du client

1. Ouvrir le fichier `main.py` et définir votre strategy en adaptant la ligne `133` (paramètre de la fonction start) avec une des statégies suivantes :  

- strategy_mc  
- strategy_mcts  
- strategy_negascoot
- strategy_alphabeta
- strategy_random  

_À noter que toutes les stratégies citées au-dessus sont fonctionnelles à la fois sur Gopher et Dodo, toute l'adaptation se fait automatiquement._  

2. Lancer le client via la commande suivante :

```bash
# lancer le client
python3 main.py numero_groupe nomjoueur1 nomjoueur2
```

## Faire tourner des simulations

NAME = GOPHER_STR
SIZE = 4

# display settings
DISPLAY=False

# game settings
NB_ITERATION = 50
BASE_DEPTH = 6 # depth for alphabeta algorythms
NB_SIMU = 400 # number of simulations for monte carlo

Nous avons mis en place un script nous permettant de faire tourner beaucoup de simulations pour nos tests avec un export sur serveur et un profilage pour vérifier le temps d'exécution de chaque fonction.  

Les paramètres `EXPORT`, `SIZE`, `DISPLAY`, `NAME` et `NB_ITERATION` sont adaptables ainsi que la strategy des joueurs parmi les suivantes aux lignes `71` et `77` : 

```python
action = env.strategy_alpha_beta(depth)
action = env.strategy_negascout(depth)
action = env.strategy_random()
action = env.strategy_mc(simu)
action, _ = env.strategy_mcts(simu)
```

---

Crédits : Aubin Vert & Théo Guegan - GI02 - P24