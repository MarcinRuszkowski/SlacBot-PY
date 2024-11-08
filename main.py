from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
from dotenv import load_dotenv
import os

load_dotenv()

# aplikacja Slack
app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

ALLOWED_CHANNEL_IDS = ["C07UQQ42SG2", "C07UT9KSY1J"]  # ID kanałów
ALLOWED_WORKSPACE_IDS = ["T07UA81QNKZ"]  # ID workspace

@app.command("/formularz")
def handle_form(ack, body, client):
    ack()

    if body["team_id"] not in ALLOWED_WORKSPACE_IDS:
        client.chat_postMessage(
            channel=body["user_id"],
            text="Ta komenda jest niedostępna na tym workspace."
        )
        return

    if body["channel_id"] not in ALLOWED_CHANNEL_IDS and not is_app_generated_channel(body):
        client.chat_postMessage(
            channel=body["user_id"],
            text="Ta komenda jest niedostępna na tym kanale."
        )
        return

    # otwórz modal z formularzem
    client.views_open(
        trigger_id=body["trigger_id"],
         view={
        "type": "modal",
        "callback_id": "form_view",
        "title": {"type": "plain_text", "text": "Formularz do kodu"},
        "blocks": [
            {
                "type": "input",
                "block_id": "license_version",
                "element": {
                    "type": "static_select",
                    "action_id": "version_select",
                    "placeholder": {"type": "plain_text", "text": "Wybierz wersję licencji"},
                    "options": [
                        {"text": {"type": "plain_text", "text": "2.0 by"}, "value": "2.0 by"},
                        {"text": {"type": "plain_text", "text": "2.0 by-nc"}, "value": "2.0 by-nc"},
                        {"text": {"type": "plain_text", "text": "2.0 by-nc-nd"}, "value": "2.0 by-nc-nd"},
                        {"text": {"type": "plain_text", "text": "2.0 by-nc-sa"}, "value": "2.0 by-nc-sa"},
                        {"text": {"type": "plain_text", "text": "2.0 by-nd"}, "value": "2.0 by-nd"},
                        {"text": {"type": "plain_text", "text": "2.0 by-sa"}, "value": "2.0 by-sa"},
                        {"text": {"type": "plain_text", "text": "3.0 by"}, "value": "3.0 by"},
                        {"text": {"type": "plain_text", "text": "3.0 by-nc"}, "value": "3.0 by-nc"},
                        {"text": {"type": "plain_text", "text": "3.0 by-nc-nd"}, "value": "3.0 by-nc-nd"},
                        {"text": {"type": "plain_text", "text": "3.0 by-nc-sa"}, "value": "3.0 by-nc-sa"},
                        {"text": {"type": "plain_text", "text": "3.0 by-nd"}, "value": "3.0 by-nd"},
                        {"text": {"type": "plain_text", "text": "3.0 by-sa"}, "value": "3.0 by-sa"},
                        {"text": {"type": "plain_text", "text": "4.0 by"}, "value": "4.0 by"},
                        {"text": {"type": "plain_text", "text": "4.0 by-nc"}, "value": "4.0 by-nc"},
                        {"text": {"type": "plain_text", "text": "4.0 by-nc-nd"}, "value": "4.0 by-nc-nd"},
                        {"text": {"type": "plain_text", "text": "4.0 by-nc-sa"}, "value": "4.0 by-nc-sa"},
                        {"text": {"type": "plain_text", "text": "4.0 by-nd"}, "value": "4.0 by-nd"},
                        {"text": {"type": "plain_text", "text": "4.0 by-sa"}, "value": "4.0 by-sa"},
                    ],
                },
                "label": {"type": "plain_text", "text": "Wybierz wersję licencji"},
            },
            {
                "type": "input",
                "block_id": "image_author",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "author_input",
                    "placeholder": {"type": "plain_text", "text": "Imie i nazwisko"}
                },
                "label": {"type": "plain_text", "text": "Autor obrazu"},
            },
            {
                "type": "input",
                "block_id": "image_source",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "source_input",
                    "placeholder": {"type": "plain_text", "text": "wikipedia"}
                },
                "label": {"type": "plain_text", "text": "Żródło obrazu"},
            },
            {
                "type": "input",
                "block_id": "work_title",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "title_input",
                    "placeholder": {"type": "plain_text", "text": "MCK z tarasu widokowego"}
                },
                "label": {"type": "plain_text", "text": "Tytuł pracy"},
            },
            {
                "type": "input",
                "block_id": "image_link",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "link_input",
                    "placeholder": {"type": "plain_text", "text": "https://pl.wikipedia.org/wiki/MCK..."}
                },
                "label": {"type": "plain_text", "text": "Link do obrazu"},
            },
        ],
        "submit": {"type": "plain_text", "text": "Generuj"},
    },
    )

def is_app_generated_channel(body):
    return body["channel_id"].startswith("D") 

# Obsługa danych z formularza
@app.view("form_view")
def handle_submission(ack, body, client):
    ack()

    try:
        # Pobieranie wartości z formularza
        values = body["view"]["state"]["values"]
        version = values["license_version"]["version_select"]["selected_option"]["value"]
        author = values["image_author"]["author_input"]["value"]
        source = values["image_source"]["source_input"]["value"]
        title = values.get("work_title", {}).get("title_input", {}).get("value", "")
        link = values.get("image_link", {}).get("link_input", {}).get("value", "")

        # walidacja linka
        if link and not link.startswith("https://"):
            raise ValueError("Link do obrazu musi zaczynać się od 'https://'.")


        # Generowanie opisu
        license_parts = version.split(" ")
        license_type = license_parts[1].lower() if len(license_parts) > 1 else license_parts[0].lower()
        license_version = license_parts[0]
        license_link = f"https://creativecommons.org/licenses/{license_type}/{license_version}/"

        if version.startswith("2.0"):
            description = f'<a href="{link}">{title}</a>/{author}/{source}/<a href="{license_link}">CC {version}</a>'
        else:
            description = f'{author}/{source}/<a href="{license_link}">CC {version}</a>'

        # Wysłanie wiadomości do użytkownika
        client.chat_postMessage(
            channel=body["user"]["id"],
            text=f"Wygenerowany kod:\n{description}"
        )
    except ValueError as ve:
        # Obsługa błędów walidacji
        client.chat_postMessage(
            channel=body["user"]["id"],
            text=f"Wystąpił błąd: {ve}"
        )
    except Exception as e:
        print(f"Błąd podczas przetwarzania formularza: {e}")
        client.chat_postMessage(
            channel=body["user"]["id"],
            text="Wystąpił nieoczekiwany błąd."
        )



    
if __name__ == "__main__":
    flask_app.run(port=3000)
