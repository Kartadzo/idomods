# Szablony Kodu - Szybka Referencja

Krótkie szablony kodu dla każdego języka do szybkiego wklejania i adaptacji.

## Python

### Plik Główny
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function"""
    logger.info("Starting script")
    try:
        # Your code here
        pass
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Czytanie CSV
```python
import pandas as pd

df = pd.read_csv('input.csv', encoding='utf-8')
print(df.head())
df.to_csv('output.csv', encoding='utf-8', index=False)
```

### Przetwarzanie XML
```python
from lxml import etree

tree = etree.parse('file.xml')
root = tree.getroot()

for element in root.findall('.//item'):
    name = element.find('name').text
    print(name)
```

---

## JavaScript

### DOM Manipulation
```javascript
// Bezpieczna modyfikacja
const elem = document.querySelector('#target');
if (elem) {
  elem.textContent = 'Nowy tekst';
  elem.classList.add('active');
}

// Event listener
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM załadowany');
});
```

### Fetch API
```javascript
const fetchData = async (url) => {
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Fetch error:', error);
  }
};
```

### Tracking (GTM/Analytics)
```javascript
// Check if GTM is available
if (typeof gtag !== 'undefined') {
  gtag('event', 'purchase', {
    transaction_id: '12345',
    value: 99.99,
    currency: 'PLN'
  });
}
```

---

## SQL

### Basic SELECT
```sql
SELECT 
  p.id,
  p.name,
  COUNT(o.id) as orders
FROM ps_product p
LEFT JOIN ps_order o ON p.id = o.product_id
WHERE p.active = 1
GROUP BY p.id
ORDER BY orders DESC
LIMIT 100;
```

### INSERT
```sql
INSERT INTO ps_product (name, price, active)
VALUES ('Product Name', 99.99, 1);
```

### UPDATE
```sql
UPDATE ps_product
SET price = price * 1.1
WHERE category_id = 5
  AND active = 1;
```

---

## XSLT

### Podstawowa Transformacja
```xml
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  
  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>
  
  <xsl:template match="/">
    <products>
      <xsl:apply-templates select="//product"/>
    </products>
  </xsl:template>
  
  <xsl:template match="product">
    <item>
      <id><xsl:value-of select="id"/></id>
      <name><xsl:value-of select="name"/></name>
      <price><xsl:value-of select="format-number(price, '0.00')"/></price>
    </item>
  </xsl:template>
  
</xsl:stylesheet>
```

### Conditional Processing
```xml
<xsl:choose>
  <xsl:when test="@status = 'active'">
    <status>Aktywny</status>
  </xsl:when>
  <xsl:otherwise>
    <status>Nieaktywny</status>
  </xsl:otherwise>
</xsl:choose>
```

---

## PHP

### Database Query
```php
<?php
$dsn = 'mysql:host=localhost;dbname=mydb;charset=utf8mb4';
$pdo = new PDO($dsn, 'user', 'password');

$stmt = $pdo->prepare('SELECT * FROM products WHERE category_id = ?');
$stmt->execute([5]);

while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
    echo $row['name'];
}
?>
```

### HTTP Request
```php
<?php
$url = 'https://api.example.com/endpoint';
$ch = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($http_code === 200) {
    $data = json_decode($response, true);
    var_dump($data);
}
?>
```

### File Operations
```php
<?php
// Read CSV
if (($handle = fopen('file.csv', 'r')) !== false) {
    while (($row = fgetcsv($handle)) !== false) {
        echo implode(',', $row);
    }
    fclose($handle);
}

// Write File
$content = "Jakiś tekst\n";
file_put_contents('output.txt', $content, FILE_APPEND);
?>
```

---

## Cross-Language Patterns

### Error Handling
| Język | Pattern |
|-------|---------|
| Python | `try: ... except Exception as e:` |
| JS | `try { } catch(e) { }` |
| SQL | `BEGIN; ... ON ERROR ROLLBACK;` |
| PHP | `try { } catch (Exception $e) { }` |

### UTF-8 Deklaracja
| Język | Code |
|-------|------|
| Python | `# -*- coding: utf-8 -*-` |
| JS | `<meta charset="utf-8">` |
| SQL | `SET NAMES utf8mb4;` |
| XSLT | `<?xml version="1.0" encoding="UTF-8"?>` |
| PHP | `header('Content-Type: text/html; charset=utf-8');` |

### Logging
| Język | Pattern |
|-------|---------|
| Python | `logging.info("msg")` |
| JS | `console.log("msg")` |
| SQL | N/A (use app logging) |
| PHP | `error_log("msg")` |

---

## Tips & Tricks

### Testing Zanim Wdrażać
1. Testuj na małych danych
2. Weryfikuj encoding wyjścia
3. Sprawdzaj liczby wierszy/rekordów
4. Porównaj z oczekiwanym formatem

### Performance
1. Indeks na kolumny WHERE/JOIN
2. Limit dużych wyników
3. Cache/memorize obliczenia
4. Avoid N+1 queries

### Security Always
1. Sanitize inputs
2. Prepared statements
3. Escape outputs
4. No hardcoded secrets
5. Validate on server side

---

**Więcej szczegółów w plikach `instructions.md` w poszczególnych folderach.**
