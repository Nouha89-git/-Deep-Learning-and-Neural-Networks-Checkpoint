import streamlit as st
import speech_recognition as sr
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import random
import string
import time

# Télécharger les ressources NLTK nécessaires
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

# Initialiser le lemmatiseur
lemmatizer = WordNetLemmatizer()


# Fonction pour prétraiter le texte
def preprocess_text(text):
    # Convertir en minuscules et tokeniser
    tokens = word_tokenize(text.lower())
    # Supprimer la ponctuation
    tokens = [token for token in tokens if token not in string.punctuation]
    # Lemmatiser chaque token
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return tokens


# Fonction simple de réponse (à adapter selon votre fichier de texte)
def respond(user_input):
    # Liste de réponses génériques
    responses = [
        "Bonjour! Comment puis-je vous aider?",
        "C'est intéressant, dites-m'en plus.",
        "Je comprends votre question.",
        "Pouvez-vous être plus précis?",
        "Merci pour cette information.",
        "Je ne suis pas sûr de comprendre, pouvez-vous reformuler?",
    ]

    # Mots-clés et réponses associées
    keywords = {
        "bonjour": ["Bonjour! Comment allez-vous?", "Salut! Que puis-je faire pour vous?"],
        "aide": ["Je suis là pour vous aider. Que voulez-vous savoir?", "Comment puis-je vous assister?"],
        "merci": ["De rien!", "C'est un plaisir de vous aider."],
        "au revoir": ["Au revoir! À bientôt.", "Passez une bonne journée!"]
    }

    # Prétraiter l'entrée utilisateur
    preprocessed_input = preprocess_text(user_input)

    # Vérifier si des mots-clés sont présents
    for keyword, responses_list in keywords.items():
        if keyword in user_input.lower():
            return random.choice(responses_list)

    # Si aucun mot-clé n'est trouvé, retourner une réponse générique
    return random.choice(responses)


# Fonction pour transcrire la parole en texte
def transcribe_speech():
    # Initialiser le recognizer
    r = sr.Recognizer()

    with st.spinner("Écoute en cours... Parlez maintenant"):
        # Utiliser le microphone comme source
        with sr.Microphone() as source:
            st.write("Ajustement au bruit ambiant...")
            # Ajuster pour le bruit ambiant
            r.adjust_for_ambient_noise(source, duration=0.5)
            st.write("Parlez maintenant!")

            # Enregistrer l'audio
            audio = r.listen(source, timeout=5, phrase_time_limit=5)

            try:
                # Reconnaissance de la parole
                text = r.recognize_google(audio, language="fr-FR")
                return text
            except sr.UnknownValueError:
                return "Désolé, je n'ai pas compris ce que vous avez dit."
            except sr.RequestError:
                return "Désolé, le service de reconnaissance vocale n'est pas disponible actuellement."


# Interface Streamlit
def main():
    st.title("Chatbot avec Reconnaissance Vocale")

    # Initialiser l'historique des messages s'il n'existe pas
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Afficher l'historique des messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Options d'entrée (texte ou voix)
    input_option = st.radio("Choisissez votre méthode d'entrée:", ("Texte", "Voix"))

    if input_option == "Texte":
        # Entrée de texte
        user_input = st.text_input("Votre message:", key="text_input")
        if st.button("Envoyer") or user_input:
            if user_input:  # Vérifier que l'entrée n'est pas vide
                # Ajouter le message de l'utilisateur à l'historique
                st.session_state.messages.append({"role": "user", "content": user_input})

                # Générer une réponse
                response = respond(user_input)

                # Ajouter la réponse à l'historique
                st.session_state.messages.append({"role": "assistant", "content": response})

                # Recharger la page pour afficher les nouveaux messages
                st.experimental_rerun()

    else:  # Option "Voix"
        if st.button("Commencer l'enregistrement"):
            # Transcrire la parole en texte
            user_input = transcribe_speech()

            if user_input and user_input != "Désolé, je n'ai pas compris ce que vous avez dit." and user_input != "Désolé, le service de reconnaissance vocale n'est pas disponible actuellement.":
                # Afficher ce que l'utilisateur a dit
                st.write(f"Vous avez dit: {user_input}")

                # Ajouter le message de l'utilisateur à l'historique
                st.session_state.messages.append({"role": "user", "content": user_input})

                # Générer une réponse
                response = respond(user_input)

                # Ajouter la réponse à l'historique
                st.session_state.messages.append({"role": "assistant", "content": response})

                # Recharger la page pour afficher les nouveaux messages
                time.sleep(1)  # Pause pour laisser l'utilisateur voir la transcription
                st.experimental_rerun()
            else:
                st.write(user_input)  # Afficher le message d'erreur


if __name__ == "__main__":
    main()