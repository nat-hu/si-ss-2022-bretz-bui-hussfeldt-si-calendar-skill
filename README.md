# Lasten- und Pflichtenheft 

## 1	Allgemeines 

### Zweck und Ziel dieses Dokuments

Dieses Pflichtenheft beschreibt die Ziele für das „MyCroft Projekt“ im Rahmen der Vorlesung Speech Interaction im Sommersemester 2022.

### GitLab Repo 
https://gitlab.mi.hdm-stuttgart.de/nh087/si-ss-2022-bretz-bui-hussfeldt-si-calendar-skill

### Übersicht Projektmitglieder

**Gruppe** : si-ss-2022-bretz-bui-hussfeldt


| Rolle        | Name    | Kürzel |
|--------------|-----------|------------|
| Maintainer |Anh Thu Bui  | ab296      |
| Maintainer    |Lea Bretz | lb153    |
| Maintainer    |Natalie Hußfeldt | nh087   |



## 2	Konzept und Rahmenbedingungen

### Endanwender- und Technische-Dokumentation
- Es wird eine Dokumentation mit dem technischen Vorgehen und der Umsetzung sowie der Anleitung für den Endanwender im gitlab Repository hochgeladen.
- Dokumntierter Python-Code nach [Google Style Guidelines](https://google.github.io/styleguide/pyguide.html)

### Wie wird der Skill durch wen installierbar sein
- Skill wird über das GitLab-Repo installierbar sein
- Nur anwendbar für User, die einen NextCloud Kalender haben 
- Hardware-Ausstattung s. Ressourcen (Entwicklungskit und Accounts)

### In welchen Umgebungen wird das Produkt funktionieren und wie robust, ab welchen Umgebungsbedingungen wird keine Garantie mehr gegeben?
- Keine laute Umgebung mit zu vielen Hintergrundgeräuschen, die Mikrofoneingabe muss eindeutig identifizierbar sein
- Undeutliche Sprechweise kann nicht erkannt werden (z.B. Sprechen mit Maske kann nicht 100% korrekte Ausgaben erwarten)
- Eine Internet-Anbindung muss gegeben sein 
- Vermutung möglicher Konflikte mit anderen Skills, bei ähnlichen Key-Words


### Abgabe 
- Wann wird das Produkt abgegeben und wie?
- Abgabe über Link zu Gitlab-Repository
- Abgabetermin wie vorgegeben 24.06.2022

### Sonstiges 
- [Google Style Guidelines](https://google.github.io/styleguide/pyguide.html) werden befolgt 


### 2.1	Vorgaben : 
-	Verwendung Python als Programmiersprache
-	Verwendung CalDav Protokoll 
-	 Mit Mycroft einen neuen Skill entwickeln

### 2.2	Ressourcen : 

**Entwicklungskit : 
-	Raspberry Pi 4
-	MiFa Lautsprecher zur Wiedergabe
-	Logitech c270 Webcam als Mikrofon
-	SD-Karte mit einem eigenen auf Picroft aufbauenden Image

**Accounts : 
-	Mycroft Home auf einem HdM-Server : https://mycroft.humanoidlab.hdm-stuttgart.de/
-	NextCloud Account : https://nextcloud.humanoidlab.hdm-stuttgart.de/index.php/apps/registration/

### 2.3	Beschreibungen und Anforderungen : 

Für die Umsetzung der Anforderungen soll mit HdM eigenen, privaten GitLab Repository gearbeitet werden

#### Anforderung 1 

| Nr.       | Titel   | Priorität |
|--------------|-----------|------------|
| 1 | Python Skript CalDav Code  |1|


Beschreibung

-	NextCloud Kalender mit CalDAV-Protokoll ansprechen

Python- Skript : 
-	Termine der kommenden X Tage abfragen, parsen 
-	Antwort mit Datum, Zeit, Titel des Termins zurückgeben

## Skills 

Hinweise : 

- Die Eingabe darf nicht von unseren definierten Mustern abweichen.
- Bei nicht verstehen, wird ein default Dialog gestartet, welcher fragt, ob abgebrochen werden soll, oder die Eingabe wiederholt werden soll.


#### Anforderung 2

| Nr.       | Titel   | Priorität |
|--------------|-----------|------------|
| 2|   Mycroft- Skill  „Abfrage Termine“   |1|

Beschreibung
-	Eigener Mycroft Skill zur Abfrage von den nächsten Terminen im NextCloud- Kalender
-	Mycroft soll nach folgenden Gesprächsmodell antworten können : 

Szenario 1 : 
-	“Hey Mycroft”
-	"What is my next appointment?"

-	"Your next appointment is on "MONTH, DAY, YEAR"  at "TIME" and is entitled "SUMMARY"

Szenario 2 : 
-	“Hey Mycroft”
-	"What are my plans on "DATE"

-	Your plans for "DAY" the "DATE" are as follows :
-	You have a total of "X" appointments
-	These are : 
-	1. "SUMMARY" at "TIME"
-	2. "SUMMARY" at "TIME"
-	…

Szenario 3 : 
-	“Hey Mycroft”
-	"What are my plans for last/next "WEEKDAY"

-	Your plans for the last/next "WEEKDAY" are as follows :
-	You have a total of "X" appointments
-	These are : 
-	1. "SUMMARY" at "TIME"
-	2. "SUMMARY" at "TIME"
-	…

Szenario 4 : 
-	“Hey Mycroft”
-	"What are my plans for "TOMORROW/DAY AFTER TOMORROW"

-	Your plans for the last/next "WEEKDAY" are as follows :
-	You have a total of "X" appointments
-	These are : 
-	1. "SUMMARY" at "TIME"
-	2. "SUMMARY" at "TIME"
-	…

Szenario 5 : 
-	“Hey Mycroft”
-	"What are my next "NUMBER" appointments ?
-	Your next 5 appointments are: 
-	1. "SUMMARY" at "TIME"
-	2. "SUMMARY" at "TIME"
-	…

Explizit ausgeschlossen : 
- Frage nach spezifischen Ereignissen : "Am I going to eat ice cream tomorrow?"
- Frage nach einer genauen Uhrzeit 



### Anforderung 3

| Nr.       | Titel   | Priorität |
|--------------|-----------|------------|
| 3| Zusatzaufgabe 1 “Kalendereintrag“     |2|


Beschreibung
-	Per Sprachkommando über Mycroft-Skill einen neuen Kalendereintrag machen

Szenario : 
-	Hey Microft
-	Create a new event
-	Tell me the title of the new event 
-   "New TITLE"
-	For which date should I enter the appointment ?
-	"DAY, MONTH, YEAR"
-	At what time the event starts?
-	"TIME"
-	At what time the event ends?
-	"TIME"
- I added the event "NEW TITLE" to your calendar at "DATE" from "TIME" to "TIME". Is that correct ? 
- "NO"
- (again create event dialog)

Explizit ausgeschlossen : 
- Event mit einer Spracheingabe anzulegen => durch begrenzte Aufnahmezeit, kann nicht alles am Stück benannt werden


#### Anforderung 4

| Nr.       | Titel   | Priorität |
|--------------|-----------|------------|
| 4|  Zusatzaufgabe 2 “Event löschen“   |2|


Beschreibung
-	Per Sprachkommando über Mycroft-Skill ein Event löschen

Szenario : 
-	Hey Microft
-   Delete event 
-   For which date should I delete the appointment ?
-	"DAY, MONTH, YEAR"
-   Your plans for the day are as follows :
-	You have a total of "X" appointments
-	These are : 
-	1. "SUMMARY" at "TIME"
-	2. "SUMMARY" at "TIME"
-   Wich one do you want to delete ? 
-   "SUMMARY"
-   Should I delete your event "SUMMARY" ?
-   "YES" / "NO" => Stop 
- I deleted your event "SUMMARY"


Explizit ausgeschlossen : 
- Es reicht nicht aus, nur einen Namen zu sagen, oder eine Uhrzeit, um ein Event zu löschen.

#### Anforderung 5

| Nr.       | Titel   | Priorität |
|--------------|-----------|------------|
| 5|  Zusatzaufgabe 3 “Event umbenennen“  |2|


Beschreibung
-	Per Sprachkommando über Mycroft-Skill ein Event umbenennen 


Szenario : 

Hey Microft
-   Rename event 
-   On which day should I rename an event ?
-	"DAY, MONTH, YEAR"
-   Your plans for the day are as follows :
-	You have a total of "X" appointments
-	These are : 
-	1. "SUMMARY" at "TIME"
-	2. "SUMMARY" at "TIME"
-   Wich one do you want to rename ? 
-   "SUMMARY"
-   Should I rename your event "SUMMARY" ?
-   "YES" / "NO" => Stop 
-	I renamed the event "SUMMARY" to "NEW TITLE" 

Explizit ausgeschlossen : 
- Es reicht nicht aus, nur einen Namen zu sagen, oder eine Uhrzeit, um ein Event umzubennen.

## Meilensteine 

| Meilenstein       | Personen   | Datum |
|--------------|-----------|-------------|
| CalDAV Code (grundlegend)| Team  |10.05.2022 |
|  Mycroft- Skill  „Abfrage Termine“ |Team | 17.05.2022|
| Zusatzaufgabe 1 “Kalendereintrag“  |Team |24.05.2022|
| Zusatzaufgabe 2 “Event löschen“  |Team  | 07.06.2022 |
| Zusatzaufgabe 3 “Event umbennen“ |Team  |07.06.2022  |
| Dokumentation |Team  | Abgabetermin|24.06.2022 |







