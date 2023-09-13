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
Nu moet je een scope gaan toevoegen. Klik op `ADD OR REMOVE SCOPES` en zoek vervolgens naar `calendar.app.created`. Klik op het eerste resultaat en klik op `UPDATE`.  
Klik vervolgens op `SAVE AND CONTINUE` en je scope is ingesteld.  
Selecteer voor application type `Desktop app` en geef het een naam. Klik dan op `CREATE`.  
Download vervolgens je credentials en bewaar deze als `credentials.json`. Klik daarna op `DONE`.  
Ga vervolgens naar `OAuth consent screen` en klik op `PUBLISH`. Volg de stappen om je app actief te maken.  
Nu ben je klaar met de Google Agenda API!

## 4. Geckodriver en pip installeren
Het installeren van Geckodriver en pip op Ubuntu kan al voor je gedaan zijn, maar om er zeker van te zijn kan je de volgende commands runnen.  
```
sudo apt install firefox 
sudo apt install python3-pip
geckodriver --version
pip --version
```
Voor Windows is dit ook mogelijk. Je moet dan de geckodriver voor Windows hier downloaden: https://github.com/mozilla/geckodriver  
Plaats deze executable vervolgens op een locatie die in PATH staat. Om een locatie toe te voegen aan PATH moet je zoeken in windows naar `omgevingsvariabelen`. Hier staat kan je het tabje Path bewerken en een nieuwe locatie toevoegen.  
Als dit gelukt is dan is het tijd om de laatste libraries te installeren.  
```
pip install selenium
pip install mysql-connector-python
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```
Nu is alles klaar om het programma te starten.

## 5. Start het programma
Nu is het tijd om het programma op te starten.  
Bewerk alleereerst `HomiAgenda.py`. Vul je juiste informatie in voor de login credentials.  
Voordat we de file op de server gaan zetten voeren we deze eerst uit op je computer. Je zal gevraagd worden om in te loggen in Google. Als dit gelukt is zal er een bestand aangemaakt worden met de naam <email>.json. Nu kan je het programma sluiten.
Nu is het tijd om de bestanden over te zetten naar de server. Hiervoor kan je Filezilla gebruiken of de commandline.  
Zet `HomiAgenda.py, <email>.json en credentials.json` in een folder op je server bij elkaar. In Filezilla is dit drag and drop, maar met de commandline moet je alle bestanden één voor één toevoegen met `nano`.
Nu ben je klaar om het programma te starten op je server. `python3 HomiAgenda.py`
