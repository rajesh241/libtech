DROP TABLE IF EXISTS `districts`;
CREATE TABLE `districts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) DEFAULT NULL,
  `crawlIP` varchar(20) DEFAULT NULL,
  `state` varchar(20) DEFAULT NULL,
  `stateShortCode` varchar(2) DEFAULT NULL,
  `stateCode` varchar(2) DEFAULT NULL,
  `districtCode` varchar(2) DEFAULT NULL,
  `isRequired` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `stateDist` (`stateCode`,`districtCode`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
