SELECT
    product.id_product AS 'id_product',
    product.active AS 'active',
    manufacturer.name AS 'manufacturer',
    GROUP_CONCAT(DISTINCT(category_lang.name) SEPARATOR '\\') AS 'Category',
    product.ean13 AS 'ean13',
    product.mpn AS 'mpn',
    product.quantity AS 'product_quantity',
    stock.physical_quantity AS 'physical_quantity',
    stock.reserved_quantity AS 'reserved_quantity',
    stock.id_stock_available AS 'id_stock_available',
    stock.quantity AS 'stock_quantity',
    stock.location AS 'location',
    product.price AS 'price_net',
    product_shop.wholesale_price AS 'wholesale_price2',
    product.wholesale_price AS 'wholesale_price',
    product.reference AS 'reference',
    product.weight AS 'weight',
    lang.description AS 'description',
    lang.description_short AS 'description_short',
    lang.name AS 'name',
    (
        SELECT
            GROUP_CONCAT(
                feature_lang.name,
                '\\',
                feature_value_lang.value SEPARATOR '\n'
            )
        FROM
            ps_feature feature
            LEFT JOIN ps_feature_lang feature_lang ON (
                feature_lang.id_feature = feature.id_feature
                AND feature_lang.id_lang = 2
            )
            LEFT JOIN ps_feature_value feature_value ON (feature_value.id_feature = feature.id_feature)
            LEFT JOIN ps_feature_value_lang feature_value_lang ON (
                feature_value_lang.id_feature_value = feature_value.id_feature_value
                AND feature_value_lang.id_lang = 2
            )
            LEFT JOIN ps_feature_product feature_product ON feature_product.id_feature = feature.id_feature
        WHERE
            feature_product.id_product = product.id_product
    ) AS attributes,
    --  AS image_url,
    GROUP_CONCAT(DISTINCT(CONCAT('https://',
        -- get the shop domain
        IFNULL(configuration .value, 'undefined_domain'),
        -- the path to the pictures folder
        '/img/p/',
        -- now take all the digits separetly as MySQL doesn't support loops in SELECT statements
        -- assuming we have smaller image id than 100'000 ;)
        IF(CHAR_LENGTH(image.id_image) >= 5, 
            -- if we have 5 digits for the image id
            CONCAT(
            -- take the first digit
            SUBSTRING(image.id_image, -5, 1),
            -- add a slash
            '/'),
            ''),
        -- repeat for the next digits
        IF(CHAR_LENGTH(image.id_image) >= 4, CONCAT(SUBSTRING(image.id_image, -4, 1), '/'), ''),
        IF(CHAR_LENGTH(image.id_image) >= 3, CONCAT(SUBSTRING(image.id_image, -3, 1), '/'), ''),
        IF(CHAR_LENGTH(image.id_image) >= 2, CONCAT(SUBSTRING(image.id_image, -2, 1), '/'), ''),
        IF(CHAR_LENGTH(image.id_image) >= 1, CONCAT(SUBSTRING(image.id_image, -1, 1), '/'), ''),
        -- add the image id
        image.id_image,
        -- put the image extension
        '.jpg')) SEPARATOR '\n') AS 'Photo',
    GROUP_CONCAT(DISTINCT(image.position) SEPARATOR '\n') AS 'Photo position'
FROM
    ps_product product
    LEFT JOIN ps_product_shop product_shop ON product_shop.id_product = product.id_product
    LEFT JOIN ps_product_lang lang ON lang.id_product = product.id_product
    LEFT JOIN ps_manufacturer manufacturer ON manufacturer.id_manufacturer = product.id_manufacturer
    LEFT JOIN ps_supplier supplier ON supplier.id_supplier = product.id_supplier
    LEFT JOIN ps_stock_available stock ON stock.id_product = product.id_product
    LEFT JOIN ps_category_product category_product ON (product.id_product = category_product.id_product)
    LEFT JOIN ps_category_lang category_lang ON (category_product.id_category = category_lang.id_category)
    LEFT JOIN ps_image image ON (product.id_product = image.id_product)
    LEFT JOIN ps_configuration configuration ON configuration.name = 'PS_SHOP_DOMAIN'
WHERE
    lang.id_lang = 2
GROUP BY product.id_product
ORDER BY
    product.id_product ASC
LIMIT
    12




-- kategorie
SELECT
    pcp.id_product,
    CONCAT(COALESCE(p3.id_category, ''),'\\',COALESCE(p2.id_category, ''),'\\',COALESCE(p1.id_category, ''),'\\',COALESCE(c.id_category, '')) as cat_path,
    CONCAT(COALESCE(cl3.name, ''),'\\',COALESCE(cl2.name, ''),'\\',COALESCE(cl1.name, ''),'\\',COALESCE(cl.name, '')) as name_path,
    c.id_category,
    cl.name AS category_name,
    p1.id_category AS id_parent1,
    cl1.name AS p1_name,
    p2.id_category AS id_parent2,
    cl2.name AS p2_name,
    p3.id_category AS id_parent3,
    cl3.name AS p3_name,
    product.ean13 AS 'ean13'
FROM
    ps_category_product pcp
JOIN ps_product product ON pcp.id_product = product.id_product
JOIN
    ps_category c ON pcp.id_category = c.id_category
JOIN
    ps_category_lang cl ON c.id_category = cl.id_category AND cl.id_lang = 2
LEFT JOIN
    ps_category p1 ON c.id_parent = p1.id_category
LEFT JOIN
    ps_category_lang cl1 ON p1.id_category = cl1.id_category AND cl1.id_lang = 2
LEFT JOIN
    ps_category p2 ON p1.id_parent = p2.id_category
LEFT JOIN
    ps_category_lang cl2 ON p2.id_category = cl2.id_category AND cl2.id_lang = 2
LEFT JOIN
    ps_category p3 ON p2.id_parent = p3.id_category
LEFT JOIN
    ps_category_lang cl3 ON p3.id_category = cl3.id_category AND cl3.id_lang = 2
ORDER BY
    pcp.id_product, c.id_category;