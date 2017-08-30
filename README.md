Herzlichen Willkommen beim Signal Video Player!

Der Signal Video Player spielt jedes Mal,
wenn ein Signal auf einem GPIO Pin ankommt das zugehörige Video ab.


# Raspberry Pi Pin Header
Das Raspberry Pi B+ hat 23 GPIO (General Purpose Input/Output) Pins,
über die er Signale empfangen kann.
Jeder dieser Pins kann mit einem Video belegt werden,
dass abgespielt wird, sobald dieser Pin mit einem GND Pin verbunden wird.
Dies geschieht am besten über ein Relais oder einen Optokoppler,
um eine galvanische Trennung zu erreichen.
Verbinde niemals etwas anderes mit diesen Pins,
es sei denn du weißt, was du tust,
da du dein Raspberry Pi ansonsten ernsthaft beschädigen kannst.

Im folgenden Bild siehst du die Nummerierung der Pins.
Über diese Nummern werden die Videos einem Pin zugeordnet.

![Belegung der Pins im Raspberry Pi](./images/pin_layout.svg)

# Dateiformat
Es wird eine Vielzahl unterschiedlicher Video- und Audioformate unterstützt.
Achte bitte darauf nur 25fps zu verwenden.
50fps schafft der Raspberry Pi leider nicht.

Um Videos auf den Raspberry Pi zu laden,
stecke einen USB Stick mit allen Dateien in einen USB Port und starte den Raspberry Pi neu.
Wenn alle Dateien fertig kopiert wurden, sagt das Programm bescheid,
dass der USB Stick entfernt werden kann und startet nach 10 Sekunden den Video Dienst.

Die Zuordnung der einzelnen Videos zu den Pins erfolgt über die Dateinamen.
Der Dateiname muss mit zwei Ziffern beginnen, welche die Pinnummer angibt.
Danach folgt ein Unterstrich und der frei wählbare Teil des Dateinamens.
Ein Beispiel:

    02_Katzenvideo.avi

Zusätzlich zu den Videodateien gibt es noch eine besondere Datei mit dem Namen "background.jpg",
die zwischen den Videos im Leerlauf gezeigt wird.
Wenn diese Datei nicht vorhanden ist, zeigt der Raspberry Pi Analyse Informationen an.

# Reaktionszeiten
Der Raspberry Pi hat nur begrenzt Speicher in seiner Grafikeinheit,
sodass nur ein Videostrom gleichzeitig vorgehalten werden kann.
Der Wechsel zwischen zwei unterschiedlichen Videos benötigt eine gewisse Zeit,
die abhängig von der Qualität und Größe der beiden Videos ist.
In den Tests waren das bis zu 2 Sekunden.
Um dieses Problem einzudämmen, hält der Signal Player das jeweils zuletzt gespielte Video im Speicher,
in der Hoffnung, dass es in Zukunft wieder gebraucht wird.
Das führt dazu, das wenn immer wieder das gleiche Video abgespielt werden soll, es keine spürbare Verzögerung gibt.
Wenn jedoch unterschiedliche Video hintereinander gespielt werden sollen,
gibt es eine kurze Verzögerung zwischen Signal und Start.
Dies ist bei der Planung zu berücksichtigen.

# SD Karten vorbereiten
Du bekommst von mir eine Datei, ein sogennantes "Image", welches auf eine SD Karte geflasht werden muss,
die man dann in ein Raspberry Pi stecken kann.
Unter Windows gibt es die Software [Etcher](https://etcher.io/), die diese Aufgabe übernimmt.
Dabei ist es sehr wichtig, dass man auch wirklich die SD Karte als Ziel auswählt.

Wenn man sich hier vertut, kann es sein dass man versehentlich **alle Daten auf seinem Computer unwideruflich löscht!**
Also Vorsicht!




