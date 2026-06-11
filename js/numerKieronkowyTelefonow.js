function enforcePhoneNumberPattern(string, data, countryCode2) {
    for (let j = 0; j < data.length; j++) {
        if (countryCode2 == data[j].alpha2) {
            string = string.replace(/[^0-9]+/g,'');
            var newString = string.match(/[0-9 +]{0,20}/g);
            newString = newString.join('');
            let countryCode = data[j].country_code;
            let phoneNumberLengths = data[j].phone_number_lengths;
            let mobileBeginWith = data[j].mobile_begin_with;
            if (!newString.startsWith(countryCode) && !newString.startsWith('+' + countryCode)) {
                newString = '+' + countryCode + newString;
            }
            else{
                newString = '+' + newString;
            }
            if (phoneNumberLengths.includes((newString.length - countryCode.length - 1).toString())) {
                let beginWithMatched = false;
                if (mobileBeginWith.length == 0 || mobileBeginWith[0] == '') {
                    beginWithMatched = true;
                } else {
                    for (let i = 0; i < mobileBeginWith.length; i++) {
                        if (newString.startsWith('+' + countryCode + mobileBeginWith[i])) {
                            beginWithMatched = true;
                            break;
                        }
                    }
                }
                if (beginWithMatched) {
                    return newString.substring(0, 15);
                }
            }
        }
    }
    return '';
}


const data = [
    {
        alpha2: 'US',
        country_code: '1',
        mobile_begin_with: ['201', '202', '203', '205', '206', '207', '208', '209', '210', '212', '213', '214', '215',
            '216', '217', '218', '219', '220', '223', '224', '225', '227', '228', '229', '231', '234', '239', '240',
            '248', '251', '252', '253', '254', '256', '260', '262', '267', '269', '270', '272', '274', '276', '278',
            '281', '283', '301', '302', '303', '304', '305', '307', '308', '309', '310', '312', '313', '314', '315',
            '316', '317', '318', '319', '320', '321', '323', '325', '327', '330', '331', '332', '334', '336', '337',
            '339', '341', '346', '347', '351', '352', '360', '361', '364', '369', '380', '385', '386', '401', '402',
            '404', '405', '406', '407', '408', '409', '410', '412', '413', '414', '415', '417', '419', '423', '424',
            '425', '430', '432', '434', '435', '440', '441', '442', '443', '445', '447', '458', '463', '464', '469', '470', '475',
            '478', '479', '480', '484', '501', '502', '503', '504', '505', '507', '508', '509', '510', '512', '513',
            '515', '516', '517', '518', '520', '530', '531', '534', '539', '540', '541', '551', '557', '559', '561',
            '562', '563', '564', '567', '570', '571', '572', '573', '574', '575', '580', '582', '585', '586', '601', '602',
            '603', '605', '606', '607', '608', '609', '610', '612', '614', '615', '616', '617', '618', '619', '620',
            '623', '626', '627', '628', '629', '630', '631', '636', '640', '641', '646', '650', '651', '656', '657', '659', '660',
            '661', '662', '667', '669', '678', '679', '680', '681', '682', '689', '701', '702', '703', '704', '706', '707',
            '708', '712', '713', '714', '715', '716', '717', '718', '719', '720', '724', '725', '726', '727', '730', '731',
            '732', '734', '737', '740', '743', '747', '752', '754', '757', '760', '762', '763', '764', '765', '769', '770', '771',
            '772', '773', '774', '775', '779', '781', '785', '786', '787', '801', '802', '803', '804', '805', '806', '808',
            '810', '812', '813', '814', '815', '816', '817', '818', '820', '828', '830', '831', '832', '835', '838', '840', '843', '845',
            '847', '848', '850', '854', '856', '857', '858', '859', '860', '862', '863', '864', '865', '870', '872',
            '878', '901', '903', '904', '906', '907', '908', '909', '910', '912', '913', '914', '915', '916', '917',
            '918', '919', '920', '925', '927', '928', '929', '930', '931', '934', '935', '936', '937', '938', '939', '940', '941', '945',
            '947', '949', '951', '952', '954', '956', '957', '959', '970', '971', '972', '973', '975', '978', '979',
            '980', '984', '985', '986', '989', '888', '800', '833', '844', '855', '866', '877', '279', '340', '983', '448', '943', '363',
            '326', '839', '826', '948'
        ],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'AW',
        country_code: '297',
        mobile_begin_with: ['5', '6', '7', '9'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'AF',
        country_code: '93',
        mobile_begin_with: ['7'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'AO',
        country_code: '244',
        mobile_begin_with: ['9'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'AI',
        country_code: '1',
        mobile_begin_with: ['2645', '2647'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'AX',
        country_code: '358',
        mobile_begin_with: ['18'],
        phone_number_lengths: [6, 7, 8]
    },
    {
        alpha2: 'AL',
        country_code: '355',
        mobile_begin_with: ['6'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'AD',
        country_code: '376',
        mobile_begin_with: ['3', '4', '6'],
        phone_number_lengths: [6]
    },
    {
        alpha2: 'AE',
        country_code: '971',
        mobile_begin_with: ['5'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'AR',
        country_code: '54',
        mobile_begin_with: ['1', '2', '3'],
        phone_number_lengths: [8, 9, 10, 11, 12]
    },
    {
        alpha2: 'AM',
        country_code: '374',
        mobile_begin_with: ['3', '4', '5', '7', '9'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'AS',
        country_code: '1',
        mobile_begin_with: ['684733', '684258'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'AG',
        country_code: '1',
        mobile_begin_with: ['2687'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'AU',
        country_code: '61',
        mobile_begin_with: ['4'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'AT',
        country_code: '43',
        mobile_begin_with: ['6'],
        phone_number_lengths: [10, 11, 12, 13, 14]
    },
    {
        alpha2: 'AZ',
        country_code: '994',
        mobile_begin_with: ['4', '5', '6', '7'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'BI',
        country_code: '257',
        mobile_begin_with: ['7', '29'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'BE',
        country_code: '32',
        mobile_begin_with: ['4', '3'],
        phone_number_lengths: [9, 8]
    },
    {
        alpha2: 'BJ',
        country_code: '229',
        mobile_begin_with: ['4', '6', '9'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'BF',
        country_code: '226',
        mobile_begin_with: ['6', '7'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'BD',
        country_code: '880',
        mobile_begin_with: ['1'],
        phone_number_lengths: [8, 9, 10]
    },
    {
        alpha2: 'BG',
        country_code: '359',
        mobile_begin_with: ['87', '88', '89', '98', '99', '43'],
        phone_number_lengths: [8, 9]
    },
    {
        alpha2: 'BH',
        country_code: '973',
        mobile_begin_with: ['3'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'BS',
        country_code: '1',
        mobile_begin_with: ['242'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'BA',
        country_code: '387',
        mobile_begin_with: ['6'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'BY',
        country_code: '375',
        mobile_begin_with: ['25', '29', '33', '44'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'BZ',
        country_code: '501',
        mobile_begin_with: ['6'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'BM',
        country_code: '1',
        mobile_begin_with: ['4413', '4415', '4417'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'BO',
        country_code: '591',
        mobile_begin_with: ['6', '7'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'BR',
        country_code: '55',
        mobile_begin_with: [
            '119', '129', '139', '149', '159', '169', '179', '189', '199', '219', '229', '249', '279', '289',
            '319', '329', '339', '349', '359', '379', '389',
            '419', '429', '439', '449', '459', '469', '479', '489', '499',
            '519', '539', '549', '559',
            '619', '629', '639', '649', '659', '669', '679', '689', '699',
            '719', '739', '749', '759', '779', '799',
            '819', '829', '839', '849', '859', '869', '879', '889', '899',
            '919', '929', '939', '949', '959', '969', '979', '989', '999',
        ],
        phone_number_lengths: [10, 11]
    },
    {
        alpha2: 'BB',
        country_code: '1',
        mobile_begin_with: ['246'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'BN',
        country_code: '673',
        mobile_begin_with: ['7', '8'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'BT',
        country_code: '975',
        mobile_begin_with: ['17'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'BW',
        country_code: '267',
        mobile_begin_with: ['71', '72', '73', '74', '75', '76'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'CF',
        country_code: '236',
        mobile_begin_with: ['7'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'CA',
        country_code: '1',
        mobile_begin_with: [
            '204', '226', '236', '249', '250', '263', '289', '306', '343', '354',
            '365', '367', '368', '403', '416', '418', '431', '437', '438', '450',
            '468', '474', '506', '514', '519', '548', '579', '581', '584', '587',
            '600', '604', '613', '639', '647', '672', '683', '705', '709', '742',
            '753', '778', '780', '782', '807', '819', '825', '867', '873', '902',
            '905', '428', '382'
        ],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'CH',
        country_code: '41',
        mobile_begin_with: ['74', '75', '76', '77', '78', '79'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'CL',
        country_code: '56',
        mobile_begin_with: ['9'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'CN',
        country_code: '86',
        mobile_begin_with: ['13', '14', '15', '17', '18', '19', '16'],
        phone_number_lengths: [11]
    },
    {
        alpha2: 'CI',
        country_code: '225',
        mobile_begin_with: ['0', '4', '5', '6', '7', '8'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'CM',
        country_code: '237',
        mobile_begin_with: ['6'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'CD',
        country_code: '243',
        mobile_begin_with: ['8', '9'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'CG',
        country_code: '242',
        mobile_begin_with: ['0'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'CK',
        country_code: '682',
        mobile_begin_with: ['5', '7'],
        phone_number_lengths: [5]
    },
    {
        alpha2: 'CO',
        country_code: '57',
        mobile_begin_with: ['3'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'CW',
        country_code: '5999',
        mobile_begin_with: ['5', '6'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'KM',
        country_code: '269',
        mobile_begin_with: ['3', '76'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'CV',
        country_code: '238',
        mobile_begin_with: ['5', '9'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'CR',
        country_code: '506',
        mobile_begin_with: ['5', '6', '7', '8'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'CU',
        country_code: '53',
        mobile_begin_with: ['5'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'KY',
        country_code: '1',
        mobile_begin_with: ['345'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'CY',
        country_code: '357',
        mobile_begin_with: ['9'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'CZ',
        country_code: '420',
        mobile_begin_with: ['6', '7'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'DE',
        country_code: '49',
        mobile_begin_with: ['15', '16', '17'],
        phone_number_lengths: [10, 11]
    },
    {
        alpha2: 'DJ',
        country_code: '253',
        mobile_begin_with: ['77'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'DM',
        country_code: '1',
        mobile_begin_with: ['767'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'DK',
        country_code: '45',
        mobile_begin_with: ['2', '30', '31', '40', '41', '42', '50', '51', '52', '53', '60', '61', '71', '81', '91', '92', '93'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'DO',
        country_code: '1',
        mobile_begin_with: ['809', '829', '849'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'DZ',
        country_code: '213',
        mobile_begin_with: ['5', '6', '7'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'EC',
        country_code: '593',
        mobile_begin_with: ['9'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'EG',
        country_code: '20',
        mobile_begin_with: ['1'],
        phone_number_lengths: [10, 8]
    },
    {
        alpha2: 'ER',
        country_code: '291',
        mobile_begin_with: ['1', '7', '8'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'ES',
        country_code: '34',
        mobile_begin_with: ['6', '7'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'EE',
        country_code: '372',
        mobile_begin_with: ['5', '81', '82', '83'],
        phone_number_lengths: [7, 8]
    },
    {
        alpha2: 'ET',
        country_code: '251',
        mobile_begin_with: ['9'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'FI',
        country_code: '358',
        mobile_begin_with: ['4', '5'],
        phone_number_lengths: [9, 10]
    },
    {
        alpha2: 'FJ',
        country_code: '679',
        mobile_begin_with: ['2', '7', '8', '9'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'FK',
        country_code: '500',
        mobile_begin_with: ['5', '6'],
        phone_number_lengths: [5]
    },
    {
        alpha2: 'FR',
        country_code: '33',
        mobile_begin_with: ['6', '7'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'FO',
        country_code: '298',
        mobile_begin_with: [],
        phone_number_lengths: [6]
    },
    {
        alpha2: 'FM',
        country_code: '691',
        mobile_begin_with: [],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'GA',
        country_code: '241',
        mobile_begin_with: ['2', '3', '4', '5', '6', '7'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'GB',
        country_code: '44',
        mobile_begin_with: ['7'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'GE',
        country_code: '995',
        mobile_begin_with: ['5', '7'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'GH',
        country_code: '233',
        mobile_begin_with: ['2', '5'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'GI',
        country_code: '350',
        mobile_begin_with: ['5'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'GN',
        country_code: '224',
        mobile_begin_with: ['6'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'GP',
        country_code: '590',
        mobile_begin_with: ['690'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'GM',
        country_code: '220',
        mobile_begin_with: ['7', '9'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'GW',
        country_code: '245',
        mobile_begin_with: ['5', '6', '7'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'GQ',
        country_code: '240',
        mobile_begin_with: ['222', '551'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'GR',
        country_code: '30',
        mobile_begin_with: ['6'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'GD',
        country_code: '1',
        mobile_begin_with: ['473'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'GL',
        country_code: '299',
        mobile_begin_with: ['2', '4', '5'],
        phone_number_lengths: [6]
    },
    {
        alpha2: 'GT',
        country_code: '502',
        mobile_begin_with: ['3', '4', '5'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'GF',
        country_code: '594',
        mobile_begin_with: ['694'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'GU',
        country_code: '1',
        mobile_begin_with: ['671'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'GY',
        country_code: '592',
        mobile_begin_with: ['6'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'HK',
        country_code: '852',
        mobile_begin_with: ['4', '5', '6', '70', '71', '72', '73', '81', '82', '83', '84', '85', '86', '87', '88', '89', '9'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'HN',
        country_code: '504',
        mobile_begin_with: ['3', '7', '8', '9'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'HR',
        country_code: '385',
        mobile_begin_with: ['9'],
        phone_number_lengths: [8, 9]
    },
    {
        alpha2: 'HT',
        country_code: '509',
        mobile_begin_with: ['3', '4'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'HU',
        country_code: '36',
        mobile_begin_with: ['20', '30', '31', '50', '70'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'ID',
        country_code: '62',
        mobile_begin_with: ['8'],
        phone_number_lengths: [9, 10, 11, 12]
    },
    {
        alpha2: 'IN',
        country_code: '91',
        mobile_begin_with: ['6', '7', '8', '9'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'IE',
        country_code: '353',
        mobile_begin_with: ['82', '83', '84', '85', '86', '87', '88', '89'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'IR',
        country_code: '98',
        mobile_begin_with: ['9'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'IQ',
        country_code: '964',
        mobile_begin_with: ['7'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'IS',
        country_code: '354',
        mobile_begin_with: ['6', '7', '8'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'IL',
        country_code: '972',
        mobile_begin_with: ['5'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'IT',
        country_code: '39',
        mobile_begin_with: ['3'],
        phone_number_lengths: [9, 10]
    },
    {
        alpha2: 'JM',
        country_code: '1',
        mobile_begin_with: ['876'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'JO',
        country_code: '962',
        mobile_begin_with: ['7'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'JP',
        country_code: '81',
        mobile_begin_with: ['70', '80', '90'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'KZ',
        country_code: '7',
        mobile_begin_with: ['70', '74', '77'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'KE',
        country_code: '254',
        mobile_begin_with: ['7', '1'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'KG',
        country_code: '996',
        mobile_begin_with: ['5', '7', '8', '9'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'KH',
        country_code: '855',
        mobile_begin_with: ['1', '6', '7', '8', '9'],
        phone_number_lengths: [8, 9]
    },
    {
        alpha2: 'KI',
        country_code: '686',
        mobile_begin_with: ['9', '30'],
        phone_number_lengths: [5]
    },
    {
        alpha2: 'KN',
        country_code: '1',
        mobile_begin_with: ['869'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'KR',
        country_code: '82',
        mobile_begin_with: ['1'],
        phone_number_lengths: [9, 10]
    },
    {
        alpha2: 'KW',
        country_code: '965',
        mobile_begin_with: ['5', '6', '9'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'LA',
        country_code: '856',
        mobile_begin_with: ['20'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'LB',
        country_code: '961',
        mobile_begin_with: ['3', '7', '8'],
        phone_number_lengths: [7, 8]
    },
    {
        alpha2: 'LR',
        country_code: '231',
        mobile_begin_with: ['4', '5', '6', '7'],
        phone_number_lengths: [7, 8]
    },
    {
        alpha2: 'LY',
        country_code: '218',
        mobile_begin_with: ['9'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'LC',
        country_code: '1',
        mobile_begin_with: ['758'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'LI',
        country_code: '423',
        mobile_begin_with: ['7'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'LK',
        country_code: '94',
        mobile_begin_with: ['7'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'LS',
        country_code: '266',
        mobile_begin_with: ['5', '6'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'LT',
        country_code: '370',
        mobile_begin_with: ['6'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'LU',
        country_code: '352',
        mobile_begin_with: ['6'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'LV',
        country_code: '371',
        mobile_begin_with: ['2'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'MO',
        country_code: '853',
        mobile_begin_with: ['6'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'MA',
        country_code: '212',
        mobile_begin_with: ['6', '7'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'MC',
        country_code: '377',
        mobile_begin_with: ['4', '6'],
        phone_number_lengths: [8, 9]
    },
    {
        alpha2: 'MD',
        country_code: '373',
        mobile_begin_with: ['6', '7'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'MG',
        country_code: '261',
        mobile_begin_with: ['3'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'MV',
        country_code: '960',
        mobile_begin_with: ['7', '9'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'MX',
        country_code: '52',
        mobile_begin_with: [],
        phone_number_lengths: [10, 11]
    },
    {
        alpha2: 'MH',
        country_code: '692',
        mobile_begin_with: [],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'MK',
        country_code: '389',
        mobile_begin_with: ['7'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'ML',
        country_code: '223',
        mobile_begin_with: ['6', '7'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'MT',
        country_code: '356',
        mobile_begin_with: ['7', '9'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'MM',
        country_code: '95',
        mobile_begin_with: ['9'],
        phone_number_lengths: [8, 9, 10]
    },
    {
        alpha2: 'ME',
        country_code: '382',
        mobile_begin_with: ['6'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'MN',
        country_code: '976',
        mobile_begin_with: ['5', '8', '9'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'MP',
        country_code: '1',
        mobile_begin_with: ['670'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'MZ',
        country_code: '258',
        mobile_begin_with: ['8'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'MR',
        country_code: '222',
        mobile_begin_with: [],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'MS',
        country_code: '1',
        mobile_begin_with: ['664'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'MQ',
        country_code: '596',
        mobile_begin_with: ['696'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'MU',
        country_code: '230',
        mobile_begin_with: ['5'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'MW',
        country_code: '265',
        mobile_begin_with: ['77', '88', '99'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'MY',
        country_code: '60',
        mobile_begin_with: ['1', '6'],
        phone_number_lengths: [9, 10, 8]
    },
    {
        alpha2: 'YT',
        country_code: '262',
        mobile_begin_with: ['639'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'NA',
        country_code: '264',
        mobile_begin_with: ['60', '81', '82', '85'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'NC',
        country_code: '687',
        mobile_begin_with: ['7', '8', '9'],
        phone_number_lengths: [6]
    },
    {
        alpha2: 'NE',
        country_code: '227',
        mobile_begin_with: ['9'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'NF',
        country_code: '672',
        mobile_begin_with: ['5', '8'],
        phone_number_lengths: [5]
    },
    {
        alpha2: 'NG',
        country_code: '234',
        mobile_begin_with: ['70', '80', '81', '90', '91'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'NI',
        country_code: '505',
        mobile_begin_with: ['8'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'NU',
        country_code: '683',
        mobile_begin_with: [],
        phone_number_lengths: [4]
    },
    {
        alpha2: 'NL',
        country_code: '31',
        mobile_begin_with: ['6'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'NO',
        country_code: '47',
        mobile_begin_with: ['4', '9'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'NP',
        country_code: '977',
        mobile_begin_with: ['97', '98'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'NR',
        country_code: '674',
        mobile_begin_with: ['555'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'NZ',
        country_code: '64',
        mobile_begin_with: ['2'],
        phone_number_lengths: [8, 9, 10]
    },
    {
        alpha2: 'OM',
        country_code: '968',
        mobile_begin_with: ['9'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'PK',
        country_code: '92',
        mobile_begin_with: ['3'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'PA',
        country_code: '507',
        mobile_begin_with: ['6'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'PE',
        country_code: '51',
        mobile_begin_with: ['9'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'PH',
        country_code: '63',
        mobile_begin_with: ['9'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'PW',
        country_code: '680',
        mobile_begin_with: [],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'PG',
        country_code: '675',
        mobile_begin_with: ['7'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'PL',
        country_code: '48',
        mobile_begin_with: ['4', '5', '6', '7', '8'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'PR',
        country_code: '1',
        mobile_begin_with: ['787', '939'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'PT',
        country_code: '351',
        mobile_begin_with: ['9'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'PY',
        country_code: '595',
        mobile_begin_with: ['9'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'PS',
        country_code: '970',
        mobile_begin_with: ['5'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'PF',
        country_code: '689',
        mobile_begin_with: ['8'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'QA',
        country_code: '974',
        mobile_begin_with: ['3', '5', '6', '7'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'RE',
        country_code: '262',
        mobile_begin_with: ['692', '693'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'RO',
        country_code: '40',
        mobile_begin_with: ['7'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'RU',
        country_code: '7',
        mobile_begin_with: ['9', '495', '498', '499', '835'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'RW',
        country_code: '250',
        mobile_begin_with: ['7'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'SA',
        country_code: '966',
        mobile_begin_with: ['5'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'SD',
        country_code: '249',
        mobile_begin_with: ['9'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'SS',
        country_code: '211',
        mobile_begin_with: ['9'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'SN',
        country_code: '221',
        mobile_begin_with: ['7'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'SG',
        country_code: '65',
        mobile_begin_with: ['8', '9'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'SH',
        country_code: '290',
        mobile_begin_with: [],
        phone_number_lengths: [4]
    },
    {
        alpha2: 'SJ',
        country_code: '47',
        mobile_begin_with: ['79'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'SB',
        country_code: '677',
        mobile_begin_with: ['7', '8'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'SL',
        country_code: '232',
        mobile_begin_with: ['21', '25', '30', '33', '34', '40', '44', '50', '55', '76', '77', '78', '79', '88'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'SV',
        country_code: '503',
        mobile_begin_with: ['7'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'SM',
        country_code: '378',
        mobile_begin_with: ['3', '6'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'SO',
        country_code: '252',
        mobile_begin_with: ['61', '62', '63', '65', '66', '68', '69', '71', '90'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'SX',
        country_code: '1',
        mobile_begin_with: ['721'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'PM',
        country_code: '508',
        mobile_begin_with: ['55', '41'],
        phone_number_lengths: [6]
    },
    {
        alpha2: 'RS',
        country_code: '381',
        mobile_begin_with: ['6'],
        phone_number_lengths: [8, 9]
    },
    {
        alpha2: 'ST',
        country_code: '239',
        mobile_begin_with: ['98', '99'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'SR',
        country_code: '597',
        mobile_begin_with: ['6', '7', '8'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'SK',
        country_code: '421',
        mobile_begin_with: ['9'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'SI',
        country_code: '386',
        mobile_begin_with: ['3', '4', '5', '6', '7'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'SE',
        country_code: '46',
        mobile_begin_with: ['7'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'SC',
        country_code: '248',
        mobile_begin_with: ['2'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'SY',
        country_code: '963',
        mobile_begin_with: ['9'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'TC',
        country_code: '1',
        mobile_begin_with: ['6492', '6493', '6494'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'TD',
        country_code: '235',
        mobile_begin_with: ['6', '7', '9'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'TG',
        country_code: '228',
        mobile_begin_with: ['9'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'TH',
        country_code: '66',
        mobile_begin_with: ['6', '8', '9'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'TJ',
        country_code: '992',
        mobile_begin_with: ['9'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'TK',
        country_code: '690',
        mobile_begin_with: [],
        phone_number_lengths: [4]
    },
    {
        alpha2: 'TM',
        country_code: '993',
        mobile_begin_with: ['6'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'TL',
        country_code: '670',
        mobile_begin_with: ['7'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'TO',
        country_code: '676',
        mobile_begin_with: [],
        phone_number_lengths: [5]
    },
    {
        alpha2: 'TT',
        country_code: '1',
        mobile_begin_with: ['868'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'TN',
        country_code: '216',
        mobile_begin_with: ['2', '4', '5', '9'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'TR',
        country_code: '90',
        mobile_begin_with: ['5'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'TV',
        country_code: '688',
        mobile_begin_with: [],
        phone_number_lengths: [5]
    },
    {
        alpha2: 'TW',
        country_code: '886',
        mobile_begin_with: ['9'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'TZ',
        country_code: '255',
        mobile_begin_with: ['7', '6'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'UG',
        country_code: '256',
        mobile_begin_with: ['7'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'UA',
        country_code: '380',
        mobile_begin_with: ['39', '50', '63', '66', '67', '68', '73', '9'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'UY',
        country_code: '598',
        mobile_begin_with: ['9'],
        phone_number_lengths: [8]
    },
    {
        alpha2: 'UZ',
        country_code: '998',
        mobile_begin_with: ['9', '88', '33'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'VC',
        country_code: '1',
        mobile_begin_with: ['784'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'VE',
        country_code: '58',
        mobile_begin_with: ['4'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'VG',
        country_code: '1',
        mobile_begin_with: ['284'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'VI',
        country_code: '1',
        mobile_begin_with: ['340'],
        phone_number_lengths: [10]
    },
    {
        alpha2: 'VN',
        country_code: '84',
        mobile_begin_with: ['8', '9', '3', '7', '5'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'VU',
        country_code: '678',
        mobile_begin_with: ['5', '7'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'WF',
        country_code: '681',
        mobile_begin_with: [],
        phone_number_lengths: [6]
    },
    {
        alpha2: 'WS',
        country_code: '685',
        mobile_begin_with: ['7'],
        phone_number_lengths: [7]
    },
    {
        alpha2: 'YE',
        country_code: '967',
        mobile_begin_with: ['7'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'ZA',
        country_code: '27',
        mobile_begin_with: ['1', '2', '3', '4', '5', '6', '7', '8'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'ZM',
        country_code: '260',
        mobile_begin_with: ['9', '7'],
        phone_number_lengths: [9]
    },
    {
        alpha2: 'ZW',
        country_code: '263',
        mobile_begin_with: ['71', '73', '77', '78'],
        phone_number_lengths: [9]
    }
];


var email_brandsmanago = '[iai:client_email]';
var tel_brandsmanago = enforcePhoneNumberPattern('[iai:client_phone]', data, '[iai:client_country_code]')
var name_brandsmanago = '[iai:client_name]';
var lastname_brandsmanago = '[iai:client_lastname]';
var adress_brandsmanago = '[iai:client_address]';
var city_brandsmanago = '[iai:client_city]';
var country_brandsmanago = '[iai:client_country]';
var zip_brandsmanago = '[iai:client_zip]';

// function enforcePhoneNumberPattern(e,n,o){for(let h=0;h<n.length;h++)if(o==n[h].alpha2){var t=(e=e.replace(/[^0-9]+/g,"")).match(/[0-9 +]{0,20}/g);t=t.join("");let i=n[h].country_code,l=n[h].phone_number_lengths,b=n[h].mobile_begin_with;if(t=t.startsWith(i)||t.startsWith("+"+i)?"+"+t:"+"+i+t,l.includes(t.length-i.length-1)){let a=!1;if(0==b.length||""==b[0])a=!0;else for(let r=0;r<b.length;r++)if(t.startsWith("+"+i+b[r])){a=!0;break}if(a)return t.substring(0,15)}}return""}const data=[{alpha2:"US",country_code:"1",mobile_begin_with:["201","202","203","205","206","207","208","209","210","212","213","214","215","216","217","218","219","220","223","224","225","227","228","229","231","234","239","240","248","251","252","253","254","256","260","262","267","269","270","272","274","276","278","281","283","301","302","303","304","305","307","308","309","310","312","313","314","315","316","317","318","319","320","321","323","325","327","330","331","332","334","336","337","339","341","346","347","351","352","360","361","364","369","380","385","386","401","402","404","405","406","407","408","409","410","412","413","414","415","417","419","423","424","425","430","432","434","435","440","441","442","443","445","447","458","463","464","469","470","475","478","479","480","484","501","502","503","504","505","507","508","509","510","512","513","515","516","517","518","520","530","531","534","539","540","541","551","557","559","561","562","563","564","567","570","571","572","573","574","575","580","582","585","586","601","602","603","605","606","607","608","609","610","612","614","615","616","617","618","619","620","623","626","627","628","629","630","631","636","640","641","646","650","651","656","657","659","660","661","662","667","669","678","679","680","681","682","689","701","702","703","704","706","707","708","712","713","714","715","716","717","718","719","720","724","725","726","727","730","731","732","734","737","740","743","747","752","754","757","760","762","763","764","765","769","770","771","772","773","774","775","779","781","785","786","787","801","802","803","804","805","806","808","810","812","813","814","815","816","817","818","820","828","830","831","832","835","838","840","843","845","847","848","850","854","856","857","858","859","860","862","863","864","865","870","872","878","901","903","904","906","907","908","909","910","912","913","914","915","916","917","918","919","920","925","927","928","929","930","931","934","935","936","937","938","939","940","941","945","947","949","951","952","954","956","957","959","970","971","972","973","975","978","979","980","984","985","986","989","888","800","833","844","855","866","877","279","340","983","448","943","363","326","839","826","948"],phone_number_lengths:[10]},{alpha2:"AW",country_code:"297",mobile_begin_with:["5","6","7","9"],phone_number_lengths:[7]},{alpha2:"AF",country_code:"93",mobile_begin_with:["7"],phone_number_lengths:[9]},{alpha2:"AO",country_code:"244",mobile_begin_with:["9"],phone_number_lengths:[9]},{alpha2:"AI",country_code:"1",mobile_begin_with:["2645","2647"],phone_number_lengths:[10]},{alpha2:"AX",country_code:"358",mobile_begin_with:["18"],phone_number_lengths:[6,7,8]},{alpha2:"AL",country_code:"355",mobile_begin_with:["6"],phone_number_lengths:[9]},{alpha2:"AD",country_code:"376",mobile_begin_with:["3","4","6"],phone_number_lengths:[6]},{alpha2:"AE",country_code:"971",mobile_begin_with:["5"],phone_number_lengths:[9]},{alpha2:"AR",country_code:"54",mobile_begin_with:["1","2","3"],phone_number_lengths:[8,9,10,11,12]},{alpha2:"AM",country_code:"374",mobile_begin_with:["3","4","5","7","9"],phone_number_lengths:[8]},{alpha2:"AS",country_code:"1",mobile_begin_with:["684733","684258"],phone_number_lengths:[10]},{alpha2:"AG",country_code:"1",mobile_begin_with:["2687"],phone_number_lengths:[10]},{alpha2:"AU",country_code:"61",mobile_begin_with:["4"],phone_number_lengths:[9]},{alpha2:"AT",country_code:"43",mobile_begin_with:["6"],phone_number_lengths:[10,11,12,13,14]},{alpha2:"AZ",country_code:"994",mobile_begin_with:["4","5","6","7"],phone_number_lengths:[9]},{alpha2:"BI",country_code:"257",mobile_begin_with:["7","29"],phone_number_lengths:[8]},{alpha2:"BE",country_code:"32",mobile_begin_with:["4","3"],phone_number_lengths:[9,8]},{alpha2:"BJ",country_code:"229",mobile_begin_with:["4","6","9"],phone_number_lengths:[8]},{alpha2:"BF",country_code:"226",mobile_begin_with:["6","7"],phone_number_lengths:[8]},{alpha2:"BD",country_code:"880",mobile_begin_with:["1"],phone_number_lengths:[8,9,10]},{alpha2:"BG",country_code:"359",mobile_begin_with:["87","88","89","98","99","43"],phone_number_lengths:[8,9]},{alpha2:"BH",country_code:"973",mobile_begin_with:["3"],phone_number_lengths:[8]},{alpha2:"BS",country_code:"1",mobile_begin_with:["242"],phone_number_lengths:[10]},{alpha2:"BA",country_code:"387",mobile_begin_with:["6"],phone_number_lengths:[8]},{alpha2:"BY",country_code:"375",mobile_begin_with:["25","29","33","44"],phone_number_lengths:[9]},{alpha2:"BZ",country_code:"501",mobile_begin_with:["6"],phone_number_lengths:[7]},{alpha2:"BM",country_code:"1",mobile_begin_with:["4413","4415","4417"],phone_number_lengths:[10]},{alpha2:"BO",country_code:"591",mobile_begin_with:["6","7"],phone_number_lengths:[8]},{alpha2:"BR",country_code:"55",mobile_begin_with:["119","129","139","149","159","169","179","189","199","219","229","249","279","289","319","329","339","349","359","379","389","419","429","439","449","459","469","479","489","499","519","539","549","559","619","629","639","649","659","669","679","689","699","719","739","749","759","779","799","819","829","839","849","859","869","879","889","899","919","929","939","949","959","969","979","989","999",],phone_number_lengths:[10,11]},{alpha2:"BB",country_code:"1",mobile_begin_with:["246"],phone_number_lengths:[10]},{alpha2:"BN",country_code:"673",mobile_begin_with:["7","8"],phone_number_lengths:[7]},{alpha2:"BT",country_code:"975",mobile_begin_with:["17"],phone_number_lengths:[8]},{alpha2:"BW",country_code:"267",mobile_begin_with:["71","72","73","74","75","76"],phone_number_lengths:[8]},{alpha2:"CF",country_code:"236",mobile_begin_with:["7"],phone_number_lengths:[8]},{alpha2:"CA",country_code:"1",mobile_begin_with:["204","226","236","249","250","263","289","306","343","354","365","367","368","403","416","418","431","437","438","450","468","474","506","514","519","548","579","581","584","587","600","604","613","639","647","672","683","705","709","742","753","778","780","782","807","819","825","867","873","902","905","428","382"],phone_number_lengths:[10]},{alpha2:"CH",country_code:"41",mobile_begin_with:["74","75","76","77","78","79"],phone_number_lengths:[9]},{alpha2:"CL",country_code:"56",mobile_begin_with:["9"],phone_number_lengths:[9]},{alpha2:"CN",country_code:"86",mobile_begin_with:["13","14","15","17","18","19","16"],phone_number_lengths:[11]},{alpha2:"CI",country_code:"225",mobile_begin_with:["0","4","5","6","7","8"],phone_number_lengths:[10]},{alpha2:"CM",country_code:"237",mobile_begin_with:["6"],phone_number_lengths:[9]},{alpha2:"CD",country_code:"243",mobile_begin_with:["8","9"],phone_number_lengths:[9]},{alpha2:"CG",country_code:"242",mobile_begin_with:["0"],phone_number_lengths:[9]},{alpha2:"CK",country_code:"682",mobile_begin_with:["5","7"],phone_number_lengths:[5]},{alpha2:"CO",country_code:"57",mobile_begin_with:["3"],phone_number_lengths:[10]},{alpha2:"CW",country_code:"5999",mobile_begin_with:["5","6"],phone_number_lengths:[7]},{alpha2:"KM",country_code:"269",mobile_begin_with:["3","76"],phone_number_lengths:[7]},{alpha2:"CV",country_code:"238",mobile_begin_with:["5","9"],phone_number_lengths:[7]},{alpha2:"CR",country_code:"506",mobile_begin_with:["5","6","7","8"],phone_number_lengths:[8]},{alpha2:"CU",country_code:"53",mobile_begin_with:["5"],phone_number_lengths:[8]},{alpha2:"KY",country_code:"1",mobile_begin_with:["345"],phone_number_lengths:[10]},{alpha2:"CY",country_code:"357",mobile_begin_with:["9"],phone_number_lengths:[8]},{alpha2:"CZ",country_code:"420",mobile_begin_with:["6","7"],phone_number_lengths:[9]},{alpha2:"DE",country_code:"49",mobile_begin_with:["15","16","17"],phone_number_lengths:[10,11]},{alpha2:"DJ",country_code:"253",mobile_begin_with:["77"],phone_number_lengths:[8]},{alpha2:"DM",country_code:"1",mobile_begin_with:["767"],phone_number_lengths:[10]},{alpha2:"DK",country_code:"45",mobile_begin_with:["2","30","31","40","41","42","50","51","52","53","60","61","71","81","91","92","93"],phone_number_lengths:[8]},{alpha2:"DO",country_code:"1",mobile_begin_with:["809","829","849"],phone_number_lengths:[10]},{alpha2:"DZ",country_code:"213",mobile_begin_with:["5","6","7"],phone_number_lengths:[9]},{alpha2:"EC",country_code:"593",mobile_begin_with:["9"],phone_number_lengths:[9]},{alpha2:"EG",country_code:"20",mobile_begin_with:["1"],phone_number_lengths:[10,8]},{alpha2:"ER",country_code:"291",mobile_begin_with:["1","7","8"],phone_number_lengths:[7]},{alpha2:"ES",country_code:"34",mobile_begin_with:["6","7"],phone_number_lengths:[9]},{alpha2:"EE",country_code:"372",mobile_begin_with:["5","81","82","83"],phone_number_lengths:[7,8]},{alpha2:"ET",country_code:"251",mobile_begin_with:["9"],phone_number_lengths:[9]},{alpha2:"FI",country_code:"358",mobile_begin_with:["4","5"],phone_number_lengths:[9,10]},{alpha2:"FJ",country_code:"679",mobile_begin_with:["2","7","8","9"],phone_number_lengths:[7]},{alpha2:"FK",country_code:"500",mobile_begin_with:["5","6"],phone_number_lengths:[5]},{alpha2:"FR",country_code:"33",mobile_begin_with:["6","7"],phone_number_lengths:[9]},{alpha2:"FO",country_code:"298",mobile_begin_with:[],phone_number_lengths:[6]},{alpha2:"FM",country_code:"691",mobile_begin_with:[],phone_number_lengths:[7]},{alpha2:"GA",country_code:"241",mobile_begin_with:["2","3","4","5","6","7"],phone_number_lengths:[7]},{alpha2:"GB",country_code:"44",mobile_begin_with:["7"],phone_number_lengths:[10]},{alpha2:"GE",country_code:"995",mobile_begin_with:["5","7"],phone_number_lengths:[9]},{alpha2:"GH",country_code:"233",mobile_begin_with:["2","5"],phone_number_lengths:[9]},{alpha2:"GI",country_code:"350",mobile_begin_with:["5"],phone_number_lengths:[8]},{alpha2:"GN",country_code:"224",mobile_begin_with:["6"],phone_number_lengths:[9]},{alpha2:"GP",country_code:"590",mobile_begin_with:["690"],phone_number_lengths:[9]},{alpha2:"GM",country_code:"220",mobile_begin_with:["7","9"],phone_number_lengths:[7]},{alpha2:"GW",country_code:"245",mobile_begin_with:["5","6","7"],phone_number_lengths:[7]},{alpha2:"GQ",country_code:"240",mobile_begin_with:["222","551"],phone_number_lengths:[9]},{alpha2:"GR",country_code:"30",mobile_begin_with:["6"],phone_number_lengths:[10]},{alpha2:"GD",country_code:"1",mobile_begin_with:["473"],phone_number_lengths:[10]},{alpha2:"GL",country_code:"299",mobile_begin_with:["2","4","5"],phone_number_lengths:[6]},{alpha2:"GT",country_code:"502",mobile_begin_with:["3","4","5"],phone_number_lengths:[8]},{alpha2:"GF",country_code:"594",mobile_begin_with:["694"],phone_number_lengths:[9]},{alpha2:"GU",country_code:"1",mobile_begin_with:["671"],phone_number_lengths:[10]},{alpha2:"GY",country_code:"592",mobile_begin_with:["6"],phone_number_lengths:[7]},{alpha2:"HK",country_code:"852",mobile_begin_with:["4","5","6","70","71","72","73","81","82","83","84","85","86","87","88","89","9"],phone_number_lengths:[8]},{alpha2:"HN",country_code:"504",mobile_begin_with:["3","7","8","9"],phone_number_lengths:[8]},{alpha2:"HR",country_code:"385",mobile_begin_with:["9"],phone_number_lengths:[8,9]},{alpha2:"HT",country_code:"509",mobile_begin_with:["3","4"],phone_number_lengths:[8]},{alpha2:"HU",country_code:"36",mobile_begin_with:["20","30","31","50","70"],phone_number_lengths:[9]},{alpha2:"ID",country_code:"62",mobile_begin_with:["8"],phone_number_lengths:[9,10,11,12]},{alpha2:"IN",country_code:"91",mobile_begin_with:["6","7","8","9"],phone_number_lengths:[10]},{alpha2:"IE",country_code:"353",mobile_begin_with:["82","83","84","85","86","87","88","89"],phone_number_lengths:[9]},{alpha2:"IR",country_code:"98",mobile_begin_with:["9"],phone_number_lengths:[10]},{alpha2:"IQ",country_code:"964",mobile_begin_with:["7"],phone_number_lengths:[10]},{alpha2:"IS",country_code:"354",mobile_begin_with:["6","7","8"],phone_number_lengths:[7]},{alpha2:"IL",country_code:"972",mobile_begin_with:["5"],phone_number_lengths:[9]},{alpha2:"IT",country_code:"39",mobile_begin_with:["3"],phone_number_lengths:[9,10]},{alpha2:"JM",country_code:"1",mobile_begin_with:["876"],phone_number_lengths:[10]},{alpha2:"JO",country_code:"962",mobile_begin_with:["7"],phone_number_lengths:[9]},{alpha2:"JP",country_code:"81",mobile_begin_with:["70","80","90"],phone_number_lengths:[10]},{alpha2:"KZ",country_code:"7",mobile_begin_with:["70","74","77"],phone_number_lengths:[10]},{alpha2:"KE",country_code:"254",mobile_begin_with:["7","1"],phone_number_lengths:[9]},{alpha2:"KG",country_code:"996",mobile_begin_with:["5","7","8","9"],phone_number_lengths:[9]},{alpha2:"KH",country_code:"855",mobile_begin_with:["1","6","7","8","9"],phone_number_lengths:[8,9]},{alpha2:"KI",country_code:"686",mobile_begin_with:["9","30"],phone_number_lengths:[5]},{alpha2:"KN",country_code:"1",mobile_begin_with:["869"],phone_number_lengths:[10]},{alpha2:"KR",country_code:"82",mobile_begin_with:["1"],phone_number_lengths:[9,10]},{alpha2:"KW",country_code:"965",mobile_begin_with:["5","6","9"],phone_number_lengths:[8]},{alpha2:"LA",country_code:"856",mobile_begin_with:["20"],phone_number_lengths:[10]},{alpha2:"LB",country_code:"961",mobile_begin_with:["3","7","8"],phone_number_lengths:[7,8]},{alpha2:"LR",country_code:"231",mobile_begin_with:["4","5","6","7"],phone_number_lengths:[7,8]},{alpha2:"LY",country_code:"218",mobile_begin_with:["9"],phone_number_lengths:[9]},{alpha2:"LC",country_code:"1",mobile_begin_with:["758"],phone_number_lengths:[10]},{alpha2:"LI",country_code:"423",mobile_begin_with:["7"],phone_number_lengths:[7]},{alpha2:"LK",country_code:"94",mobile_begin_with:["7"],phone_number_lengths:[9]},{alpha2:"LS",country_code:"266",mobile_begin_with:["5","6"],phone_number_lengths:[8]},{alpha2:"LT",country_code:"370",mobile_begin_with:["6"],phone_number_lengths:[8]},{alpha2:"LU",country_code:"352",mobile_begin_with:["6"],phone_number_lengths:[9]},{alpha2:"LV",country_code:"371",mobile_begin_with:["2"],phone_number_lengths:[8]},{alpha2:"MO",country_code:"853",mobile_begin_with:["6"],phone_number_lengths:[8]},{alpha2:"MA",country_code:"212",mobile_begin_with:["6","7"],phone_number_lengths:[9]},{alpha2:"MC",country_code:"377",mobile_begin_with:["4","6"],phone_number_lengths:[8,9]},{alpha2:"MD",country_code:"373",mobile_begin_with:["6","7"],phone_number_lengths:[8]},{alpha2:"MG",country_code:"261",mobile_begin_with:["3"],phone_number_lengths:[9]},{alpha2:"MV",country_code:"960",mobile_begin_with:["7","9"],phone_number_lengths:[7]},{alpha2:"MX",country_code:"52",mobile_begin_with:[],phone_number_lengths:[10,11]},{alpha2:"MH",country_code:"692",mobile_begin_with:[],phone_number_lengths:[7]},{alpha2:"MK",country_code:"389",mobile_begin_with:["7"],phone_number_lengths:[8]},{alpha2:"ML",country_code:"223",mobile_begin_with:["6","7"],phone_number_lengths:[8]},{alpha2:"MT",country_code:"356",mobile_begin_with:["7","9"],phone_number_lengths:[8]},{alpha2:"MM",country_code:"95",mobile_begin_with:["9"],phone_number_lengths:[8,9,10]},{alpha2:"ME",country_code:"382",mobile_begin_with:["6"],phone_number_lengths:[8]},{alpha2:"MN",country_code:"976",mobile_begin_with:["5","8","9"],phone_number_lengths:[8]},{alpha2:"MP",country_code:"1",mobile_begin_with:["670"],phone_number_lengths:[10]},{alpha2:"MZ",country_code:"258",mobile_begin_with:["8"],phone_number_lengths:[9]},{alpha2:"MR",country_code:"222",mobile_begin_with:[],phone_number_lengths:[8]},{alpha2:"MS",country_code:"1",mobile_begin_with:["664"],phone_number_lengths:[10]},{alpha2:"MQ",country_code:"596",mobile_begin_with:["696"],phone_number_lengths:[9]},{alpha2:"MU",country_code:"230",mobile_begin_with:["5"],phone_number_lengths:[8]},{alpha2:"MW",country_code:"265",mobile_begin_with:["77","88","99"],phone_number_lengths:[9]},{alpha2:"MY",country_code:"60",mobile_begin_with:["1","6"],phone_number_lengths:[9,10,8]},{alpha2:"YT",country_code:"262",mobile_begin_with:["639"],phone_number_lengths:[9]},{alpha2:"NA",country_code:"264",mobile_begin_with:["60","81","82","85"],phone_number_lengths:[9]},{alpha2:"NC",country_code:"687",mobile_begin_with:["7","8","9"],phone_number_lengths:[6]},{alpha2:"NE",country_code:"227",mobile_begin_with:["9"],phone_number_lengths:[8]},{alpha2:"NF",country_code:"672",mobile_begin_with:["5","8"],phone_number_lengths:[5]},{alpha2:"NG",country_code:"234",mobile_begin_with:["70","80","81","90","91"],phone_number_lengths:[10]},{alpha2:"NI",country_code:"505",mobile_begin_with:["8"],phone_number_lengths:[8]},{alpha2:"NU",country_code:"683",mobile_begin_with:[],phone_number_lengths:[4]},{alpha2:"NL",country_code:"31",mobile_begin_with:["6"],phone_number_lengths:[9]},{alpha2:"NO",country_code:"47",mobile_begin_with:["4","9"],phone_number_lengths:[8]},{alpha2:"NP",country_code:"977",mobile_begin_with:["97","98"],phone_number_lengths:[10]},{alpha2:"NR",country_code:"674",mobile_begin_with:["555"],phone_number_lengths:[7]},{alpha2:"NZ",country_code:"64",mobile_begin_with:["2"],phone_number_lengths:[8,9,10]},{alpha2:"OM",country_code:"968",mobile_begin_with:["9"],phone_number_lengths:[8]},{alpha2:"PK",country_code:"92",mobile_begin_with:["3"],phone_number_lengths:[10]},{alpha2:"PA",country_code:"507",mobile_begin_with:["6"],phone_number_lengths:[8]},{alpha2:"PE",country_code:"51",mobile_begin_with:["9"],phone_number_lengths:[9]},{alpha2:"PH",country_code:"63",mobile_begin_with:["9"],phone_number_lengths:[10]},{alpha2:"PW",country_code:"680",mobile_begin_with:[],phone_number_lengths:[7]},{alpha2:"PG",country_code:"675",mobile_begin_with:["7"],phone_number_lengths:[8]},{alpha2:"PL",country_code:"48",mobile_begin_with:["4","5","6","7","8"],phone_number_lengths:[9]},{alpha2:"PR",country_code:"1",mobile_begin_with:["787","939"],phone_number_lengths:[10]},{alpha2:"PT",country_code:"351",mobile_begin_with:["9"],phone_number_lengths:[9]},{alpha2:"PY",country_code:"595",mobile_begin_with:["9"],phone_number_lengths:[9]},{alpha2:"PS",country_code:"970",mobile_begin_with:["5"],phone_number_lengths:[9]},{alpha2:"PF",country_code:"689",mobile_begin_with:["8"],phone_number_lengths:[8]},{alpha2:"QA",country_code:"974",mobile_begin_with:["3","5","6","7"],phone_number_lengths:[8]},{alpha2:"RE",country_code:"262",mobile_begin_with:["692","693"],phone_number_lengths:[9]},{alpha2:"RO",country_code:"40",mobile_begin_with:["7"],phone_number_lengths:[9]},{alpha2:"RU",country_code:"7",mobile_begin_with:["9","495","498","499","835"],phone_number_lengths:[10]},{alpha2:"RW",country_code:"250",mobile_begin_with:["7"],phone_number_lengths:[9]},{alpha2:"SA",country_code:"966",mobile_begin_with:["5"],phone_number_lengths:[9]},{alpha2:"SD",country_code:"249",mobile_begin_with:["9"],phone_number_lengths:[9]},{alpha2:"SS",country_code:"211",mobile_begin_with:["9"],phone_number_lengths:[9]},{alpha2:"SN",country_code:"221",mobile_begin_with:["7"],phone_number_lengths:[9]},{alpha2:"SG",country_code:"65",mobile_begin_with:["8","9"],phone_number_lengths:[8]},{alpha2:"SH",country_code:"290",mobile_begin_with:[],phone_number_lengths:[4]},{alpha2:"SJ",country_code:"47",mobile_begin_with:["79"],phone_number_lengths:[8]},{alpha2:"SB",country_code:"677",mobile_begin_with:["7","8"],phone_number_lengths:[7]},{alpha2:"SL",country_code:"232",mobile_begin_with:["21","25","30","33","34","40","44","50","55","76","77","78","79","88"],phone_number_lengths:[8]},{alpha2:"SV",country_code:"503",mobile_begin_with:["7"],phone_number_lengths:[8]},{alpha2:"SM",country_code:"378",mobile_begin_with:["3","6"],phone_number_lengths:[10]},{alpha2:"SO",country_code:"252",mobile_begin_with:["61","62","63","65","66","68","69","71","90"],phone_number_lengths:[9]},{alpha2:"SX",country_code:"1",mobile_begin_with:["721"],phone_number_lengths:[10]},{alpha2:"PM",country_code:"508",mobile_begin_with:["55","41"],phone_number_lengths:[6]},{alpha2:"RS",country_code:"381",mobile_begin_with:["6"],phone_number_lengths:[8,9]},{alpha2:"ST",country_code:"239",mobile_begin_with:["98","99"],phone_number_lengths:[7]},{alpha2:"SR",country_code:"597",mobile_begin_with:["6","7","8"],phone_number_lengths:[7]},{alpha2:"SK",country_code:"421",mobile_begin_with:["9"],phone_number_lengths:[9]},{alpha2:"SI",country_code:"386",mobile_begin_with:["3","4","5","6","7"],phone_number_lengths:[8]},{alpha2:"SE",country_code:"46",mobile_begin_with:["7"],phone_number_lengths:[9]},{alpha2:"SC",country_code:"248",mobile_begin_with:["2"],phone_number_lengths:[7]},{alpha2:"SY",country_code:"963",mobile_begin_with:["9"],phone_number_lengths:[9]},{alpha2:"TC",country_code:"1",mobile_begin_with:["6492","6493","6494"],phone_number_lengths:[10]},{alpha2:"TD",country_code:"235",mobile_begin_with:["6","7","9"],phone_number_lengths:[8]},{alpha2:"TG",country_code:"228",mobile_begin_with:["9"],phone_number_lengths:[8]},{alpha2:"TH",country_code:"66",mobile_begin_with:["6","8","9"],phone_number_lengths:[9]},{alpha2:"TJ",country_code:"992",mobile_begin_with:["9"],phone_number_lengths:[9]},{alpha2:"TK",country_code:"690",mobile_begin_with:[],phone_number_lengths:[4]},{alpha2:"TM",country_code:"993",mobile_begin_with:["6"],phone_number_lengths:[8]},{alpha2:"TL",country_code:"670",mobile_begin_with:["7"],phone_number_lengths:[8]},{alpha2:"TO",country_code:"676",mobile_begin_with:[],phone_number_lengths:[5]},{alpha2:"TT",country_code:"1",mobile_begin_with:["868"],phone_number_lengths:[10]},{alpha2:"TN",country_code:"216",mobile_begin_with:["2","4","5","9"],phone_number_lengths:[8]},{alpha2:"TR",country_code:"90",mobile_begin_with:["5"],phone_number_lengths:[10]},{alpha2:"TV",country_code:"688",mobile_begin_with:[],phone_number_lengths:[5]},{alpha2:"TW",country_code:"886",mobile_begin_with:["9"],phone_number_lengths:[9]},{alpha2:"TZ",country_code:"255",mobile_begin_with:["7","6"],phone_number_lengths:[9]},{alpha2:"UG",country_code:"256",mobile_begin_with:["7"],phone_number_lengths:[9]},{alpha2:"UA",country_code:"380",mobile_begin_with:["39","50","63","66","67","68","73","9"],phone_number_lengths:[9]},{alpha2:"UY",country_code:"598",mobile_begin_with:["9"],phone_number_lengths:[8]},{alpha2:"UZ",country_code:"998",mobile_begin_with:["9","88","33"],phone_number_lengths:[9]},{alpha2:"VC",country_code:"1",mobile_begin_with:["784"],phone_number_lengths:[10]},{alpha2:"VE",country_code:"58",mobile_begin_with:["4"],phone_number_lengths:[10]},{alpha2:"VG",country_code:"1",mobile_begin_with:["284"],phone_number_lengths:[10]},{alpha2:"VI",country_code:"1",mobile_begin_with:["340"],phone_number_lengths:[10]},{alpha2:"VN",country_code:"84",mobile_begin_with:["8","9","3","7","5"],phone_number_lengths:[9]},{alpha2:"VU",country_code:"678",mobile_begin_with:["5","7"],phone_number_lengths:[7]},{alpha2:"WF",country_code:"681",mobile_begin_with:[],phone_number_lengths:[6]},{alpha2:"WS",country_code:"685",mobile_begin_with:["7"],phone_number_lengths:[7]},{alpha2:"YE",country_code:"967",mobile_begin_with:["7"],phone_number_lengths:[9]},{alpha2:"ZA",country_code:"27",mobile_begin_with:["1","2","3","4","5","6","7","8"],phone_number_lengths:[9]},{alpha2:"ZM",country_code:"260",mobile_begin_with:["9","7"],phone_number_lengths:[9]},{alpha2:"ZW",country_code:"263",mobile_begin_with:["71","73","77","78"],phone_number_lengths:[9]}];var email_brandsmanago="[iai:client_email]",tel_brandsmanago=enforcePhoneNumberPattern("[iai:client_phone]",data,"[iai:client_country_code]"),name_brandsmanago="[iai:client_name]",lastname_brandsmanago="[iai:client_lastname]",adress_brandsmanago="[iai:client_address]",city_brandsmanago="[iai:client_city]",country_brandsmanago="[iai:client_country]",zip_brandsmanago="[iai:client_zip]";
