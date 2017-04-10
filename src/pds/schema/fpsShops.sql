CREATE TABLE `fpsShops` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `stateName` varchar(40) DEFAULT NULL,
  `districtName` varchar(40) DEFAULT NULL,
  `blockName` varchar(40) DEFAULT NULL,
  `fpsName` varchar(256) DEFAULT NULL,
  `stateCode` varchar(2) DEFAULT NULL,
  `districtCode` varchar(20) DEFAULT NULL,
  `blockCode` varchar(20) DEFAULT NULL,
  `fpsCode` varchar(20) DEFAULT NULL,
  `isRequired` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY  (`districtCode`,`blockCode`,`fpsCode`)
);
