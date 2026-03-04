import speech_recognition as sr

r = sr.Recognizer()

while True:
    with sr.Microphone() as source:
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio, language='ru-RU')
        print(text)
    except:
        continue
