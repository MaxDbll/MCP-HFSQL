# Serveur MCP pour Bases de Données HFSQL

## Description

Ce projet fournit un serveur basé sur le **Model Context Protocol (MCP)**, permettant aux modèles de langage (comme les agents IA conversationnels) d'interagir avec des bases de données HFSQL C/S.

**Objectif :** Faciliter l'exploration et l'interrogation des bases de données HFSQL par les utilisateurs finaux via une interface en langage naturel, grâce à l'IA.

**MCP ?** Le Model Context Protocol est un standard ouvert conçu pour permettre aux modèles de langage d'appeler de manière fiable des outils externes (API, bases de données, fonctions, etc.).

Apprenez-en plus sur les serveurs MCP avec les resosurces d'Anthropic : https://docs.anthropic.com/fr/docs/agents-and-tools/mcp

## Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants :

* **SDK Python pour MCP** : Vous pouvez suivre les instructions d'installation ici : https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#installation
* **Python :** Version 3.10 ou supérieure (vérifiez la documentation du SDK MCP pour les exigences spécifiques si nécessaire).
* **Pip :** Pour l'installation des paquets Python.
* **Driver ODBC HFSQL :** Installez le driver ODBC approprié pour votre système d'exploitation. Vous pouvez généralement le trouver sur le site de PC SOFT : [https://download.windev.com/fr/download/packs/HFSQL/2025.awp](https://download.windev.com/fr/download/packs/HFSQL/2025.awp) (Adaptez la version si besoin).
* **Accès à une base de données HFSQL C/S :** Avec les informations de connexion nécessaires (hôte, port, nom de base, utilisateur, mot de passe).
* **Git :** Pour cloner le dépôt.

## Installation

Suivez ces étapes pour mettre en place le projet :

1.  **Cloner le dépôt GitHub :**
    ```bash
    git clone https://github.com/MaxDbll/MCP-HFSQL.git
    cd mcp-hfsql
    ```

2.  **Créer un environnement virtuel (Fortement Recommandé) :**
    ```bash
    python -m venv venv
    # Sur Linux/macOS
    source venv/bin/activate
    # Sur Windows (cmd/powershell)
    .\venv\Scripts\activate
    ```

3.  **Installer les dépendances Python :**
    Le fichier `requirements.txt` contient toutes les bibliothèques nécessaires, y compris le SDK `mcp` et le connecteur de base de données (`pypyodbc`).
    ```bash
    pip install -r requirements.txt
    ```
    *il faut également installer mcp[cli]*

## Configuration du Serveur

Ce serveur MCP récupère ses informations de connexion à la base de données HFSQL à partir des **variables d'environnement**. Avant de lancer le serveur, vous devez définir les variables suivantes :

* `HFSQL_HOST`: Adresse IP ou nom d'hôte du serveur HFSQL.
* `HFSQL_PORT`: Port d'écoute du serveur HFSQL (par défaut souvent 4900).
* `HFSQL_DATABASE`: Nom de la base de données à utiliser.
* `HFSQL_USER`: Nom d'utilisateur pour la connexion.
* `HFSQL_PASSWORD`: Mot de passe associé à l'utilisateur.

**Comment définir les variables d'environnement ?**

* **Sur Linux/macOS (Terminal) :**
    ```bash
    export HFSQL_HOST="votre_hote"
    export HFSQL_PORT="4900"
    export HFSQL_DATABASE="votre_base"
    export HFSQL_USER="votre_user"
    export HFSQL_PASSWORD="votre_mot_de_passe"
    ```
* **Sur Windows (PowerShell) :**
    ```bash
    $env:HFSQL_HOST = "votre_hote"
    $env:HFSQL_PORT = "4900"
    $env:HFSQL_DATABASE = "votre_base"
    $env:HFSQL_USER = "votre_user"
    $env:HFSQL_PASSWORD = "votre_mot_de_passe"
    ```
* **Alternative : Fichier `.env`**
    Vous pouvez également utiliser un fichier `.env` à la racine de votre projet et une bibliothèque comme `python-dotenv` (ajoutez-la à `requirements.txt` si vous choisissez cette option) pour charger ces variables automatiquement au démarrage de votre script `server.py`.

    **Voir plus bas pour définir les paramètres d'environnement en utilisant Claude Desktop.**

## Utilisation

1.  **Tester le serveur MCP :**
    Une fois l'environnement virtuel activé et les variables d'environnement configurées, testez le serveur en utilisant la commande fournie par le SDK MCP :
    ```bash
    mcp dev server.py
    ```

    Vous pouvez également installer le serveur sur une application d'agent IA compatible MCP (comme Claude Desktop) pour l'utiliser directement.

    ```bash
    mcp install server.py
    ```


2.  **Outils MCP Disponibles :**
    Ce serveur expose des tools, des ressources et des prompts pour interagir avec la base de données HFSQL. L'agent IA peut utiliser ces outils pour exécuter des requêtes SQL, explorer les données et obtenir des informations sur le schéma de la base de données. 

3.  **Exemples d'Interaction avec une IA :**

    * **Scénario 1 : Découverte du schéma**
        * *Utilisateur :* "Peux-tu me dire quelles tables existent dans ma base de contacts ?"

    * **Scénario 2 : Exploration Simple**
        * *Utilisateur :* "Affiche-moi les 3 premiers contacts de la table `Contacts`."

    * **Scénario 3 : Requête Assistée**
        * *Utilisateur :* "Je cherche les contacts de la société 'InnovTech' ajoutés cette année."

    * **Scénario 3 : Chiffre d'affaire**
        * *Utilisateur :* "Quel est le trimestre avec le chiffre d'affaire le plus elevé et celui avec le moins elevé ?"

## Exemple d'Intégration Client (Claude Desktop)

Si vous utilisez un client MCP comme Claude Desktop, vous devrez lui indiquer comment lancer *votre* serveur MCP. Voici un exemple de configuration à ajouter dans le fichier `claude_desktop_config.json` (le chemin peut varier) :

```json
   "HFSQL Assistant": {
     "command": "uv",  
     "args": [
       "run",
       // Les lignes suivantes avec 'uv' sont spécifiques à son usage
       // Elles assurent que mcp[cli] et pypyodbc sont disponibles
       // Si vous n'utilisez pas 'uv', adaptez la commande et les args
       "--with",
       "mcp[cli]",
       "--with",
       "pypyodbc",
       // --- Fin des args spécifiques à 'uv' ---
       "mcp", // La commande principale du SDK
       "run", // La sous-commande pour lancer un serveur
       // Chemin ABSOLU vers votre script serveur principal
       "C:\\Chemin\\Complet\\Vers\\Votre\\Projet\\mcp-hfsql\\server.py"
     ],
     "env": {
       // Ces variables sont passées par le client au serveur lors du lancement
       "HFSQL_HOST": "localhost",
       "HFSQL_PORT": "4900",
       "HFSQL_DATABASE": "gestioncontacts",
       "HFSQL_USER": "admin",
       "HFSQL_PASSWORD": "" // Laissez vide si pas de mot de passe
     }
   }