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

Lancer le client via la commande suivante :

```bash
# lancer le client
python3 main.py numero_groupe nomjoueur1 nomjoueur2
```

Nous avons décider d'implémenter les statégies suivantes :
- Alpha-Beta avec cache pour Gopher  
- Monte-Carlo pour Dodo  

## Faire tourner des simulations

Nous avons mis en place un script nous permettant de faire tourner beaucoup de simulations pour nos tests avec un résultat exportés sur fichier texte et un profilage pour vérifier le temps d'exécution de chaque fonction.  

Les paramètres `EXPORT`, `SIZE`, `DISPLAY`, `NAME` et `NB_ITERATION` sont adaptables ainsi que la strategy des joueurs parmi les suivantes aux lignes `71` et `81` : 

```python
action = env.strategy_random()
action = env.strategy_mc(SIMU)
action, env.root = env.strategy_mcts(SIMU,env.root)
action = env.strategy_alpha_beta(DEPTH)
action = env.strategy_alpha_beta_cache(DEPTH)
```
Remarque: Dans notre script tel qu'il est écrit, un seul joueur peut utiliser le MCTS avec conservation de l'arbre en cours.
Dans le cadre de nos simulations, nous n'avons pas eu besoin de confronter deux MCTS avec conservation de racine (stockée dans l'environnement du jeu).
À l'échelle de nombreuses simulations, cela nous permet d'éviter la création de nombreux attributs inutils de conservation de la racine dans notre environnement de jeu.

## Nos stratégies
Dans cette partie, nous allons lister les stratégies développées ainsi que les avantages et inconvénient de chacune.
### Random
Cette stratégie nous envoie un coup aléatoire à jouer. L'avantage de cette stratégie est sa rapidité d'éxécution et son inconvénient est sa performance (en termes de qualité des coups joués).
Nous utilisons notamment cette stratégie dans le cadre des simulations réalisées par les algorithmes Monte Carlo et Monte Carlo Tree Search.

### Alpha-Beta
Cette stratégie nous renvoie le coup qui maximise nos chances de jouer via l'exploration de l'ensemble possibilités de jeux (sauf celles non-nécessaires cf: coupures). 
La forte combinatoire de ce jeu ne nous permet pas une exploration entière de l'arbre de jeu. Notre alpha-beta est donc définie selon une certaine profondeur d'arbre et utilise ensuite une fonction d'évaluation (heuristique) nous permettant d'estimer la performance des actions explorées dans le cas où l'état du jeu étudié à la profondeur maximale n'est pas terminal.
L'avantage de cette méthode est sa performance, son inconvénient étant son temps d'exécution en cas de forte combinatoire, et sa dépendance en termes de performance à la fonction d'évaluation.

### Alpha-Beta avec cache
Cette stratégie est la même que la stratégie précédente avec une amélioration du temps d'exécution liée à l'ajout d'une technique de cache pour les états de jeux déjà explorées.
Elle garde néanmoins les mêmes inconvénients

### Monte Carlo
Cette stratégie étudie de façon probabiliste le taux de victoire de chacune des possibilité en effectuant des simulations aléatoires de fin de partie à partir de chacuns des coups possibles. Pour cette méthode, chacun d'eux est testé uniformément (même nombre de simulations).
L'action renvoyée est celle pour laquelle la probabilité de victoire est la plus haute.
L'avantage de cette méthode est sa rapidité d'exécution (varie en fonction du nombre de simulations choisi).
Son inconvénient et que sa performance est très fortement dépendante de nombre de simulations réalisées (convergence des estimations du taux de victoire vers le taux réel quand le nombre d'estimations tend vers l'infini (cf:SY02, Théorème central limite)).

### Monte Carlo Tree Search (MCTS)
Cette strategie étudie l'ensemble des coups jouables et évalue les probabilités de victoires de ceux-ci simulant aléatoirement la fin de partie. 
Dans cet algorithme, l'étude des probabilités de victoires n'est pas la même en fonction des coups légaux. En effet, les coups jugés les plus "intéressants" par la méthode de l'UBC (Upper Bound Confidence) sont ceux qui bénéficieront du plus de simulation aléatoire.
L'avantage de cette méthode est sa rapidité d'exécution (varie en fonction du nombre de simulations choisi).
Son inconvénient et que sa performance (en termes de qualité des coups joués) est très fortement dépendante de nombre de simulations réalisées (convergence des estimations du taux de victoire vers le taux réel quand le nombre d'estimations tend vers l'infini (cf: SY02, Théorème central limite)).
Également, la performance du MCTS dépend de la qualité de l'heuristique de choix des branches explorées (ici UBC). 

Remarque : Pour gagner en qualité des coups joués, nous avons fait le choix de conserver l'arbre construit par le MCTS et changeons de racine au cours du jeu en fonctions des coups joués. Cela nous permet de conserver les résultats des simulations déjà effectuées dans la branche lors des tours précédent (donc de converger vers des résultats plus proche de la réalité (cf: SY02))

## Notre choix d'utilisation
Après beaucoup de simulations, nous avons décidé de partir sur une stratégie alpha-beta avec cache pour le jeu Gopher, avec une fonction d'évaluation basée sur le nombre de coups légaux (nous essayons de maximiser le nombre de coups possibles) et comme paramètre la profondeur souhaitée.

Pour Dodo, nous sommes partis sur un MCTS avec conservation de la racine pour garder une trace des simulations précédentes. Nous utilisons un paramètre basé sur le nombre de simulations, cependant, nous avons aussi tenté une implémentation basée sur le temps disponible pour jouer un coup (voir branche time_implementation) qui nous poses quelques problèmes de fiabiltés (certaines branches ne peuevent pas être explorées du fait d'un temp restant très faible).

---

Crédits : Aubin Vert & Théo Guegan - GI02 - P24