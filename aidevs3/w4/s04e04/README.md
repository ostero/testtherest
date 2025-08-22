# Zadanie s04e04
`pilog.py` startuje http endpoint `/pilot` na `localhost` i  
 port podany w `api_key.yaml` `http:port`  
 `piilot_client.py` testowa aplikacja, pozwala wysłać  
 instrukcje lotu do pilota uruchomionego na `localhost`.  
 
 ## Zarejestrowanie w `centrali`
 Aby `cntrala` mogła wysyłać nam instrukcje lotu, potrzebujemy udostępnić endpoint `pilot` na publicznym ip.   
 Możemy to zrobić na `azylu`.  

 Po zalogowaniu na `azyl` dostajemy informacje o numerze portu tam dla nas wystawionego.   
 Oraz o url aplikacji, tam dla nas wystawionej np:  
 ```
  __ _ _____   _| |  __ _  __ _|___ / _ __ | |_ ___   ___  _ __ __ _ 
 / _` |_  / | | | | / _` |/ _` | |_ \| '_ \| __/ __| / _ \| '__/ _` |
| (_| |/ /| |_| | || (_| | (_| |___) | | | | |_\__ \| (_) | | | (_| |
 \__,_/___|\__, |_(_)__,_|\__, |____/|_| |_|\__|___(_)___/|_|  \__, |
           |___/          |___/                                |___/ 
---------------------------------------------------------------------
---------------------------------------------------------------------
Twoj numer portu to: 55264
---------------------------------------------------------------------
Spraw, aby Twoja aplikacja słuchała na tym porcie.
Aplikacja będzie dostępna np. pod https://azyl-55264.ag3nts.org
---------------------------------------------------------------------
```

Po uruchomieniu aplikacji `pilot.py`, należy:  
 - podać w `api_key.yaml` w `http:src` adres aplikacji wystawionej na azylu +  
  ścieżkę aplikacji pilot, np: `https://azyl-55264.ag3nts.org/pilot`  
 - Zrobić ssh port remote forwart z portu wystawionego dla nas na azylu do  
 portu aplikacji pilot na `localhost`, np:  
 `ssh -R 55264:localhost:30080 azyl`  

