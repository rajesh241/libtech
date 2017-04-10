CREATE TABLE `fpsStatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fpsCode` varchar(20) DEFAULT NULL,
  `year` int DEFAULT NULL,
  `month` int DEFAULT NULL,
  `deliveryDate` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY  (`year`,`month`,`fpsCode`)
);
