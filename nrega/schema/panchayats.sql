CREATE TABLE `panchayats` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `panchayatName` varchar(40) DEFAULT NULL,
  `rawPanchayatName` varchar(40) DEFAULT NULL,
  `blockName` varchar(40) DEFAULT NULL,
  `rawBlockName` varchar(40) DEFAULT NULL,
  `districtName` varchar(40) DEFAULT NULL,
  `rawDistrictName` varchar(40) DEFAULT NULL,
  `stateName` varchar(40) DEFAULT NULL,
  `stateCode` varchar(2) DEFAULT NULL,
  `districtCode` varchar(2) DEFAULT NULL,
  `blockCode` varchar(3) DEFAULT NULL,
  `panchayatCode` varchar(3) DEFAULT NULL,
  `fullPanchayatCode` varchar(10) DEFAULT NULL,
  `isRequired` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `PANCHAYATKEY` (`fullPanchayatCode`)
);
