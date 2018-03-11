# Intégration d'Algolia Search avec Pelican

Ce plugin [Pelican](http://docs.getpelican.com) vous permet d'indexer
automatiquement vos documents sur le service Cloud
[Algolia](https://www.algolia.com).

Vous trouverez un exemple [ici](https://tested-for-you.surge.sh/).

A chaque fois que vous lancerez la commande **pelican** pour mettre à jour votre
site, ce plugin mettra à jour vos indexes dans le cloud et supprimera les
documents qui n'existe plus.

## Installation & configuration

**Créez un compte gratuit chez Algolia:**

> La création du compte ne demande aucun moyen de paiement et le service est
> opérationnel en quelques secondes.

**Clonez ce dépôt dans votre répertoire de plugins:**

```bash
$ cd plugins
$ git clone https://github.com/srault95/pelican-algolia-search.git
```

**Installez les pré-requis:**

```bash
pip install algoliasearch beautifulsoup4
```

**Ajoutez dans pelicanconf.py:**

```python
PLUGINS = [
    #...
    'algolia_search'
]

ALGOLIA_APP_ID = "[A REMPLIR]"
ALGOLIA_SEARCH_API_KEY = "[A REMPLIR]"
ALGOLIA_ADMIN_API_KEY = "[A REMPLIR]"
ALGOLIA_INDEX_NAME = 'demoblog'
```

**Créez votre page de recherche:**

Il existe plusieurs méthodes pour intégrer les widgets Algolia dans votre site.
Pour ma part, j'ai choisi d'utiliser
[vue-instantsearch](https://community.algolia.com/vue-instantsearch)

J'ai complétement remplacer le template index.html pour que l'ouverture de mon
site, permette de rechercher directement l'information.
[ma page index](https://github.com/srault95/tested-for-you/blob/master/pelican/themes/alchemy/templates/index.html)

Vous trouverez également, tous les exemples nécessaires dans la
[documentation d'Algolia](https://www.algolia.com/doc/tutorials/search-ui/instant-search/build-an-instant-search-results-page/instantsearchjs/)

**Relancez la génération de votre site:**

```bash
$ pelican
```
