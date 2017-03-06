CREATE TABLE `districts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `districtName` varchar(40) DEFAULT NULL,
  `rawDistrictName` varchar(40) DEFAULT NULL,
  `crawlIP` varchar(20) DEFAULT NULL,
  `stateName` varchar(40) DEFAULT NULL,
  `stateShortCode` varchar(2) DEFAULT NULL,
  `stateCode` varchar(2) DEFAULT NULL,
  `districtCode` varchar(2) DEFAULT NULL,
  `fullDistrictCode` varchar(4) DEFAULT NULL,
  `isRequired` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `dist` (`fullDistrictCode`)
) 
