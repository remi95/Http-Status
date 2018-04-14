# HttpStatus

Interface web réalisée en **python** à l'aide du micro-framework **Flask** permettant de gérer une liste de sites web pour lesquels un compte rendu de leurs statuts est effectué toutes les 2 minutes.    
Si 3 erreurs consécutives surviennent sur l'un des sites, un message _slack_ et _Telegram_ est envoyé à l'administrateur des sites. Ensuite, si l'erreur est toujours d'actualité au bout de deux heures, le message est renvoyé.   

- [Prérequis pour les messages Slack](#prérequis-pour-les-messages-slack)
- [Prérequis pour les messages Telegram](#prérequis-pour-les-messages-telegram)
- [Prérequis pour l'automatisation du monitoring](#prérequis-pour-lautomatisation-du-monitoring)
- [Installation](#installation)

## Prérequis pour les messages Slack

```sh
sudo pip install slackclient
```

[Créez une application Slack](https://api.slack.com/apps) et associez-là à votre Workspace Slack.   
Ajoutez un _Bot_ à votre application et donnez-lui un nom.      
Installez votre application dans votre Team.    
A ce moment, Slack vous donnera le **Bot User OAuth Access Token**. Copiez-le et mettez le dans le fichier _secret_config.py_ à la racine du projet, c'est l'identifiant de votre Bot qui vous permettra d'envoyer des messages par son biais.

Vous aurez aussi besoin du **Channel ID** de la chaîne sur laquelle vous voulez que votre Bot envoie un message.

## Prérequis pour les messages Telegram

```sh
sudo pip install python-telegram-bot
```

[Créez un Bot Telegram](https://web.telegram.org/#/im?p=@BotFather) en parlant au _BotFather_ de l'application.   
Pour cela envoyez lui `\newbot`.    
Il vous demandera alors comment vous voulez nommer votre Bot, répondez-lui.    
Il vous demandera ensuite un _username_ pour cotre Bot, répondez-lui.    
Et voilà ! BotFather vous donne le **Token** de votre Bot dont vous aurez besoin pour envoyer des messages depuis le site.   

Pour finir, vous aurez aussi besoin de l'id de la personne que vous voudrez contacter, en l'occurrence l'administrateur du site !

## Prérequis pour l'automatisation du monitoring

```sh
sudo pip install apscheduler
```

## Installation

```sh
git clone https://github.com/remi95/Http-Status.git
cd Http-Status
mysql -u root -p < http_status.sql
sudo cp http-status.conf /etc/apache2/sites-available/http-status.conf
sudo ln -s /etc/apache2/sites-available/http-status.conf /etc/apache2/sites-enabled/http-status.conf
sudo /etc/init.d/apache2 restart
```

Modifiez le fichier _/etc/hosts_ et ajoutez-y la ligne suivante `127.0.0.1	dev.http-status.loc`.      

Vous trouverez dans le dossier un fichier nommé _configure_secret_config.py_, copiez-le ou renommez-le en **secret_config.py**. Remplacez les valeurs avec celles qui correspondent à votre serveur, ainsi qu'avec vos tokens et identifiants de Chat Slack et Telegram, comme vu précédemment.     

Pour vous connecter à la partie Admin vous aurez besoin des identifiants suivants : `admin / erty`
