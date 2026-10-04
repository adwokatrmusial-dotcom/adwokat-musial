import csv
from datetime import datetime
import os  # <- Dodaliśmy to do czytania zmiennych z Render
import smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'super-tajny-klucz-kancelarii'

# ---- KONFIGURACJA SKRZYNKI POCZTOWEJ Z RENDER ENVIRONMENT VARIABLES ----
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 465))
MOJ_EMAIL = os.environ.get("MOJ_EMAIL", "adwokat.rmusial@gmail.com")
HASLO_APLIKACJI = os.environ.get("HASLO_APLIKACJI")
EMAIL_ODBIORCY = os.environ.get("MOJ_EMAIL", "adwokat.rmusial@gmail.com")

def zapisz_do_pliku(rola, imie, email, wiadomosc):
    """Zapisuje zgłoszenie do pliku CSV z aktualną datą."""
    data_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open('zgloszenia.csv', mode='a', newline='', encoding='utf-8') as plik:
        writer = csv.writer(plik, delimiter=';')
        # Jeśli plik jest pusty, opcjonalnie można dodać nagłówki (zrobimy to automatycznie)
        writer.writerow([data_str, rola, imie, email, wiadomosc])


def wyslij_powiadomienie_email(rola, imie):
    """Wysyła uproszczone powiadomienie e-mail o nowym zgłoszeniu."""
    temat = f"Nowe zgłoszenie na stronie - {rola}"
    tresc = f"Otrzymałeś nową wiadomość od: {imie} w zakładce {rola}.\n\nPełną treść wiadomości oraz kontakt znajdziesz w pliku zgloszenia.csv na serwerze."

    msg = MIMEText(tresc, _charset='utf-8')
    msg['Subject'] = temat
    msg['From'] = MOJ_EMAIL
    msg['To'] = EMAIL_ODBIORCY

    try:
        # Zmieniamy SMTP_SSL na zwykłe SMTP, ponieważ port 587 wymaga procedury STARTTLS
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.starttls()  # To uruchamia bezpieczne szyfrowanie na porcie 587
            server.login(MOJ_EMAIL, HASLO_APLIKACJI)
            server.sendmail(MOJ_EMAIL, [EMAIL_ODBIORCY], msg.as_string())
        print("Powiadomienie e-mail zostało wysłane.")
    except Exception as e:
        print(f"Błąd wysyłki e-mail: {e}")

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/adwokat', methods=['GET', 'POST'])
def adwokat():
    if request.method == 'POST':
        honeypot = request.form.get('honeypot_field')
        if honeypot:
            print("Wykryto i zablokowano bota spamującego (Adwokat)!")
            flash('Dziękujemy za kontakt. Wiadomość została zapisana i wysłana pomyślnie!', 'success')
            return redirect(url_for('adwokat') + '#kontakt')

        # Weryfikacja akceptacji RODO
        if not request.form.get('rodo_accept'):
            flash('Musisz zaakceptować klauzulę przetwarzania danych osobowych, aby wysłać wiadomość.', 'danger')
            return redirect(url_for('adwokat') + '#kontakt')

        imie = request.form.get('name')
        email = request.form.get('email')
        wiadomosc = request.form.get('message')

        # 1. Zabezpieczamy dane w pliku Excel/CSV
        zapisz_do_pliku("Adwokat", imie, email, wiadomosc)

        # 2. Wysyłamy szybkie powiadomienie na maila
        wyslij_powiadomienie_email("Adwokat", imie)

        flash('Dziękujemy za kontakt. Wiadomość została zapisana i wysłana pomyślnie!', 'success')
        return redirect(url_for('adwokat') + '#kontakt')

    return render_template('adwokat.html')


@app.route('/doradca-restrukturyzacyjny', methods=['GET', 'POST'])
def doradca():
    if request.method == 'POST':
        honeypot = request.form.get('honeypot_field')
        if honeypot:
            print("Wykryto i zablokowano bota spamującego (Doradca)!")
            flash('Dziękujemy za kontakt. Formularz restrukturyzacyjny został bezpiecznie zapisany.', 'success')
            return redirect(url_for('doradca') + '#kontakt')

        # Weryfikacja akceptacji RODO
        if not request.form.get('rodo_accept'):
            flash('Musisz zaakceptować klauzulę przetwarzania danych osobowych, aby wysłać wiadomość.', 'danger')
            return redirect(url_for('doradca') + '#kontakt')

        imie = request.form.get('name')
        email = request.form.get('email')
        wiadomosc = request.form.get('message')

        # 1. Zabezpieczamy dane w pliku Excel/CSV
        zapisz_do_pliku("Doradca Restrukturyzacyjny", imie, email, wiadomosc)

        # 2. Wysyłamy szybkie powiadomienie na maila
        wyslij_powiadomienie_email("Doradca Restrukturyzacyjny", imie)

        flash('Dziękujemy za kontakt. Formularz restrukturyzacyjny został bezpiecznie zapisany.', 'success')
        return redirect(url_for('doradca') + '#kontakt')

    return render_template('doradca.html')

@app.route('/polityka-prywatnosci')
def polityka_prywatnosci():
    return render_template('polityka.html')

if __name__ == '__main__':
    app.run(debug=True)
