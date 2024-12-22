*Cyfrowa Biblioteka*, *libApp* to aplikacja stworzona w ramach pracy inżynierskiej na studiach. Jej głównym celem jest wspomaganie automatyzacji procesów bibliotecznych, takich jak zarządzanie zbiorami, wypożyczeniami, rejestracja użytkowników oraz integracja z wirtualnym asystentem.


### Instrukcja instalacji projektu Django *libApp*


Poniżej przedstawiono kroki instalacji i uruchomienia aplikacji:

#### 1. Pobranie projektu
Sklonuj repozytorium projektu na lokalną maszynę za pomocą komendy:
```bash
git clone https://github.com/Marcin00000/libApp.git
cd libApp
```

#### 2. Skonfigurowanie środowiska wirtualnego
Utwórz środowisko wirtualne i aktywuj je:
```bash
python -m venv venv
source venv/bin/activate  # Na systemach Unix/Mac
venv\Scripts\activate     # Na systemach Windows
```

#### 3. Instalacja zależności
Zainstaluj wszystkie wymagane pakiety, używając pliku `requirements.txt`:
```bash
pip install -r requirements.txt
```

#### 4. Dodanie pliku `.env`
Utwórz w głównym katalogu projektu plik `.env` z poniższą strukturą i uzupełnij dane odpowiednimi wartościami:
```
SECRET_KEY=your_secret_key
DB=oracle
NAME=your_database_name
USER=your_username
PASSWORD=your_password
RECAPTCHA_PUBLIC_KEY=your_recaptcha_public_key
RECAPTCHA_PRIVATE_KEY=your_recaptcha_private_key
```
> **Uwaga:** Jeśli chcesz używać bazy SQLite zamiast Oracle, zmień wartość `DB` na `sqlite`.

#### 5. Wykonanie migracji
Wykonaj migracje baz danych za pomocą poniższych poleceń:
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 6. Utworzenie superużytkownika
Utwórz superużytkownika, który pozwoli na dostęp do panelu administracyjnego:
```bash
python manage.py createsuperuser
```

#### 7. Uruchomienie serwera
Uruchom serwer deweloperski:
```bash
python manage.py runserver
```

Po wykonaniu powyższych kroków aplikacja będzie dostępna pod adresem: [http://127.0.0.1:8000](http://127.0.0.1:8000).
