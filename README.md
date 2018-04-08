# HttpStatus

Interface web réalisée en **python** à l'aide du micro-framework **Flask** permettant de gérer une liste de sites web pour lesquels un compte rendu de leur statuts est effectué toutes les 2 minutes.    
En cas de problème sur l'un des sites, un message _slack_ et _Telegram_ est envoyé à l'administrateur des sites.

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

Pour finir, vous aurez aussi besoin de l'id de la personne que vous voudrez contacter, en l'occurence l'administrateur du site ! 
