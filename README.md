# Sync Homi and GoogleAgenda
Een manier om je Lyceo homi afspraken te synchroniseren met je Google Agenda

## Benodigdheden voor een server
- Raspberry pi met Ubuntu (64 bit, mag ook een andere soort computer zijn)

## 1. Server instellen
Allereerst gaan we mysql installeren zodat de afspraken daarin kunnen worden opgeslagen. Hiervoor is het nodig dat je in staat bent om je server te bereiken via ssh.  
Dit kan met de volgende tutorial: https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04  
Als je de mogelijkheid wil om de mysql server te bereiken buiten je lokale netwerk dan moet je deze stappen uitvoeren  
```
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
```  
Vervang vervolgens bind-address  
```
#By default we only accept connections from localhost
bind-address = 127.0.0.1
bind-address = 0.0.0.0
```
Nu is het mogelijk om je mysql server te bereiken

## 2. Maak de database
Nu gaan we de databases maken voor het programma.  
Voer het python bestand uit met de naam `Make DB.py`. Dit hoeft niet uitgevoerd te worden op de server.  
Er zal je om een paar dingen gevraagd worden:  
Hostname: De hostname van je mysql server ex. 192.168.1.20, localhost of example.nl  
Username: De gebruikersnaam van je mysql server  
User password: Het wachtwoord van je mysql server  
Database name: Vul hier `homi` in  
Email: Vul hier je email die je gebruikt om in Homi in te loggen in.  

## 3. Google Agenda API
Nu is het tijd om de Google Agenda API in te stellen.  
Ga naar https://console.cloud.google.com/ en log in met je Google account.  
Je komt nu op een pagina met linksboven `Select a project`. Klik hierop en maak een nieuw project.  
Geef je project een naam ex. HomiAgenda en klik op `CREATE`.  
Het duurt even voordat het project is gemaakt. Nadat het project is gemaakt kan je via `Select a project` op jouw zojuist gemaakte project klikken.  
Ga vervolgens via het hamburger menu linksboven naar `APIs & Services`. Dit kan onder pinned items staan maar ook onder andere services.  
Klik vervolgens op `+ ENABLE APIS AND SERVICES` en zoek naar `Google Calendar API`. Klik hierop en selecteer `ENABLE`. Dit kan even duren.  
Als dit gelukt is kom je op een pagina waar rechtboven staat `CREATE CREDENTIALS`. Klik hierop.  
Selecteer in het volgende menu `User Data` en klik op `NEXT`.  
Geef het een naam, support email en contact information. Klik dan op `SAVE AND CONTINUE`.  
Nu moet je een scope gaan toevoegen. Klik op `ADD OR REMOVE SCOPES` en zoek vervolgens naar `calendar.events`. Klik op het eerste resultaat en klik op `UPDATE`.  
Klik vervolgens op `SAVE AND CONTINUE` en je scope is ingesteld.  
Selecteer voor application type `Desktop app` en geef het een naam. Klik dan op `CREATE`.  
Download vervolgens je credentials en bewaar deze. Klik daarna op `DONE`.  
Nu ben je klaar met de Google Agenda API!

## 4. Start het programma

