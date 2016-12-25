CREATE TABLE `jobcards` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `jobcard` varchar(30) DEFAULT NULL,
  `fullPanchayatCode` varchar(10) DEFAULT NULL,
  `name` varchar(256) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `stateCode` varchar(2) DEFAULT NULL,
  `districtCode` varchar(2) DEFAULT NULL,
  `blockCode` varchar(3) DEFAULT NULL,
  `panchayatCode` varchar(3) DEFAULT NULL,
  `isDownloaded` tinyint(1) DEFAULT '0',
  `downloadAttemptDate` datetime DEFAULT NULL,
  `downloadDate` datetime DEFAULT NULL,
  `isProcessed` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `jobcard` (`jobcard`),
  KEY `jobcardSearch` (`fullPanchayatCode`,`jobcard`)
);
