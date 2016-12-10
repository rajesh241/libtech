CREATE TABLE `wagelists` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `finyear` varchar(2) DEFAULT NULL,
  `fullBlockCode` varchar(7) DEFAULT NULL,
  `wagelistNo` varchar(50) DEFAULT NULL,
  `stateCode` varchar(2) DEFAULT NULL,
  `districtCode` varchar(2) DEFAULT NULL,
  `blockCode` varchar(3) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `WAGELISTKEY` (`finyear`,`fullBlockCode`,`wagelistNo`)
)
