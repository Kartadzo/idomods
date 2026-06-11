@echo off
echo Przetwarzanie plików CSV...
python "%~dp0app.py" --input "%~dp0products_export.csv" --output "%~dp0filtered.csv" --cols "@id,/sizes/size@code_external,/sizes/size@code_producer,@currency,/price@gross,/price@net,/price@vat,/srp@gross,/srp@net,/srp@vat,/price_wholesale/site@gross,/price_wholesale/site@net,/price_wholesale/site@vat,/price_wholesale/site@id,/price_minimal/site@gross,/price_minimal/site@net,/price_minimal/site@vat,/price_minimal/site@id,/price_retail/site@gross,/price_retail/site@net,/price_retail/site@vat,/price_retail/site@id,/price_retail/site@size_id,/pricecomparator_price/site@gross,/pricecomparator_price/site@net,/pricecomparator_price/site@vat,/pricecomparator_price/site@id,/pricecomparator_price/site@service_id,/sizes/size@weight,/sizes/size/price@gross,/sizes/size/price@net" --langs "pol,lit,cze,hun,slo"
echo Przetwarzanie zakonczone. Wynik zapisano w plikach filtered.csv
pause
