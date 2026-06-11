@echo off 
echo Przetwarzanie pliku XML... 
python3 .\app_xml_to_xml.py source.xliff filtered.xliff
echo Przetwarzanie zakonczone. Wynik zapisano w pliku output.xml 
pause