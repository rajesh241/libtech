CREATE TABLE `panchayatStatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fullPanchayatCode` varchar(10) DEFAULT NULL,
  `rawPanchayatName` varchar(40) DEFAULT NULL,
  `jobcardCrawlDate` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `PANCHAYATKEY` (`fullPanchayatCode`)
);
