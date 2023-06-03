# CVT_medics
 
Allgemeine Informationen

-	Login
	user: 	zhaw
	pw:		456

-	Die Funktionalität beschränkt sich auf den Reiter "Routine", das Bestellsystem ist WIP. Aktuell erscheint hier eine Auflistung aller Produkte aus
  	der Datenbank mit Abgleich von Soll- und Ist-Beständen. Die Funktionalität wird um die Erzeugung eines PDF-files für jeden Lieferanten ergänzt, hierbei 
  	wird automatisch auf den Soll-Bestand aufgefüllt. Die Bestell-Referenznummern hierfür sind bereits in der Datenbank hinterlegt. 

-	Die Datenbank läuft auf der Google Cloud. Credentials sind outsourced und wurden mittels Google SDK lokal erstellt. Secrets werden daher keine verwendet,
	insb. auch, da nur gehashte Passwörter in der usderdb.yaml verwendet werden. 

-	Die Funktion des physischen Barcode-Drucks wurde symbolisch durch den Druck eines Barcode-Bilds in der Anwendung ersetzt. Der entsprechende Code wurde
	auskommentiert (Funktion "print_barcode(barcode)"). Im Testbetrieb in unserem Labor wurde der Barcode-Drucker verwendet, um die Produktpackungen damit zu bekleben und die Aktivierung mit einem Barcodescanner durchzuführen. Dies hat einwandfrei funktioniert (kann, falls erwünscht, mit einem Video dokumentiert
	und nachgereicht werden). 

-	Hinweis zum Filtern nach "Analysesystem": Diese Funktion ist v.a. mit dem Hersteller "Roche" interessant, da wir im Labor mehrere Analysesysteme
	dieses Herstellers verwenden. Bei den meisten anderen Herstellern ist diese Funktion unnötig, kann jedoch angewählt werden. 

-	Hinweis zum Filtern nach "Produkttyp": Falls der gewünschte Produkttyp nicht vorhanden ist, bspw. weil zu dem ausgewählten Hersteller keine QC sondern
	ausschliesslich Consumables vorhanden sind, wird eine Exception angezeigt. Diese wird durch eine "try - except" - Abfrage in Zukunft verhindert.
	Zusätzlich sollen nur die jeweils vorhandenen Produkttypen auswählbar sein (WIP). 