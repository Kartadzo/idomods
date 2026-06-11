import csv
from lxml import etree

# Load the XML and XSLT files
xml_file = 'source.xml'
xslt_file = 'feediai_ceny_omnibus_for_csv.xslt'

xml = etree.parse(xml_file)
xslt = etree.parse(xslt_file)

# Perform the transformation
transform = etree.XSLT(xslt)
result = transform(xml)

# Define the CSV header
header = ["id", "alert_omnibus_jest_mniejszy", "omnibus_minus_price_roznica_10gr", "price", "omnibus_price_retail", "strikethrough_retail_price", "promotion"]

# Save the result to a CSV file
with open('output.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(header)
    for product in result.iter('product'):
        row = [
            product.get('id'),
            product.find('alert_omnibus_jest_mniejszy').text,
            product.find('omnibus_minus_price_roznica_10gr').text,
            product.find('price').text,
            product.find('omnibus_price_retail').text,
            product.find('strikethrough_retail_price').text,
            product.find('promotion').text
        ]
        writer.writerow(row)
